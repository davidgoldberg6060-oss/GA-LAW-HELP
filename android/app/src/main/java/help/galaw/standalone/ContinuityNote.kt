package help.galaw.standalone

import android.view.Gravity
import android.view.View
import android.widget.LinearLayout
import org.json.JSONObject

/**
 * One quiet line at the top of an AI screen so the user can see the AI is continuing — never a
 * cross-screen transcript. Each screen keeps its own thread; the server adds at most one short line
 * about the latest topic elsewhere in the app. "Start fresh" clears only this screen.
 */
object ContinuityNote {
    private const val MAX_TOPIC = 70

    private fun clip(s: String): String { val t = s.trim().replace(Regex("\\s+"), " "); return if (t.length <= MAX_TOPIC) t else t.take(MAX_TOPIC).substringBeforeLast(' ') + "…" }

    /**
     * Text for the line, or null when there is nothing to continue.
     * [showOwn]: forms (Charge Check, Civil Check, Loopholes) show their own last topic because the old
     * result is not on screen; chat screens already show their own messages, so they only show "elsewhere".
     */
    fun line(state: JSONObject?, showOwn: Boolean): String? {
        if (state == null) return null
        val own = state.optString("screen_last_topic").takeIf { !state.isNull("screen_last_topic") && it.isNotBlank() }
        val other = state.optString("elsewhere_topic").takeIf { !state.isNull("elsewhere_topic") && it.isNotBlank() }
        val screen = state.optString("elsewhere_screen").takeIf { !state.isNull("elsewhere_screen") && it.isNotBlank() } ?: "another screen"
        return when {
            other != null -> "Continuing from $screen: “${clip(other)}”"
            showOwn && own != null -> "Picking up where you left off: “${clip(own)}”"
            else -> null
        }
    }

    fun view(ui: GaUi, text: String, onFresh: () -> Unit): View = LinearLayout(ui.context).apply {
        orientation = LinearLayout.HORIZONTAL; gravity = Gravity.CENTER_VERTICAL; tag = "continuity"
        setPadding(0, ui.dp(2), 0, ui.dp(6))
        addView(ui.text(text, 12.5f, GaUi.MUTED, ui.sansMedium).apply { maxLines = 2 }, LinearLayout.LayoutParams(0, -2, 1f))
        addView(ui.text("Start fresh", 12.5f, GaUi.GOLD, ui.sansMedium).apply {
            setPadding(ui.dp(12), ui.dp(6), 0, ui.dp(6)); isClickable = true
            contentDescription = "Start fresh. The AI forgets earlier questions on this screen."
            setOnClickListener { onFresh() }
        })
        contentDescription = text
    }
}
