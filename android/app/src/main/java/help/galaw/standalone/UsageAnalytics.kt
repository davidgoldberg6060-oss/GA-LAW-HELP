package help.galaw.standalone

import android.content.Context
import org.json.JSONArray
import org.json.JSONObject
import kotlin.concurrent.thread

/**
 * First-party anonymous usage counts and the "How's the app so far?" prompt.
 * Never sends IP addresses, names, or the text of legal questions.
 */
object UsageAnalytics {
    const val PREFS = "ga_usage"
    const val SESSION_GAP_MS = 30L * 60L * 1000L
    const val PROMPT_AFTER_OPENS = 4
    const val PROMPT_GAP_MS = 14L * 24L * 60L * 60L * 1000L
    const val COMMENT_MAX = 2000
    val FEATURES = setOf("chat", "case_check", "motion_maker", "funny_laws", "find_legal_help", "uploads")
    val CATEGORIES = listOf(
        "bug" to "Bug or crash",
        "design" to "Design or hard to use",
        "idea" to "Missing feature or idea",
        "slow" to "Slow",
        "other" to "Other",
    )
    private val EMAIL = Regex("^[A-Za-z0-9._%+\\-]+@[A-Za-z0-9.\\-]+\\.[A-Za-z]{2,}$")

    fun shouldPrompt(opens: Int, lastPromptAt: Long, lastFeedbackAt: Long, now: Long): Boolean {
        if (opens < PROMPT_AFTER_OPENS) return false
        val last = maxOf(lastPromptAt, lastFeedbackAt)
        return last == 0L || now - last >= PROMPT_GAP_MS
    }

    fun validateFeedback(rating: Int?, category: String, comment: String, email: String): String? {
        if (CATEGORIES.none { it.first == category }) return "Choose a category."
        val text = comment.trim()
        if (rating == null && text.isEmpty()) return "Please add a star rating or a short comment."
        if (rating != null && rating !in 1..5) return "Rating must be 1 to 5 stars."
        val mail = email.trim()
        if (mail.isNotEmpty() && !EMAIL.matches(mail)) return "That contact email does not look valid."
        return null
    }

    fun onAppStart(context: Context, api: ApiClient) {
        val prefs = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
        val now = System.currentTimeMillis()
        val events = JSONArray()
        if (!prefs.getBoolean("first_open", false)) {
            prefs.edit().putBoolean("first_open", true).putBoolean("installed", true).apply()
            events.put(JSONObject().put("type", "first_open"))
            events.put(JSONObject().put("type", "install"))
        }
        events.put(JSONObject().put("type", "open"))
        val last = prefs.getLong("last_session", 0L)
        if (last == 0L || now - last >= SESSION_GAP_MS) events.put(JSONObject().put("type", "session"))
        val opens = prefs.getInt("open_count", 0) + 1
        prefs.edit().putLong("last_session", now).putInt("open_count", opens).apply()
        thread { runCatching { api.reportUsage(events) } }
    }

    fun feature(api: ApiClient, name: String) {
        if (name !in FEATURES) return
        val events = JSONArray().put(JSONObject().put("type", "feature").put("feature", name))
        thread { runCatching { api.reportUsage(events) } }
    }

    fun promptDue(context: Context, now: Long = System.currentTimeMillis()): Boolean {
        val prefs = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
        return shouldPrompt(prefs.getInt("open_count", 0), prefs.getLong("last_prompt", 0L), prefs.getLong("last_feedback", 0L), now)
    }

    fun markPromptSeen(context: Context) {
        context.getSharedPreferences(PREFS, Context.MODE_PRIVATE).edit().putLong("last_prompt", System.currentTimeMillis()).apply()
    }

    fun markFeedbackSent(context: Context) {
        context.getSharedPreferences(PREFS, Context.MODE_PRIVATE).edit().putLong("last_feedback", System.currentTimeMillis()).apply()
    }
}
