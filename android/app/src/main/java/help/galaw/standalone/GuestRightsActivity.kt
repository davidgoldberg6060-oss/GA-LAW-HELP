package help.galaw.standalone

import android.content.Intent
import android.graphics.Color
import android.graphics.Typeface
import android.os.Bundle
import android.view.Gravity
import android.widget.Button
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import kotlin.concurrent.thread
import org.json.JSONObject

class GuestRightsActivity : AppCompatActivity() {
    companion object { const val EXTRA_SITUATION = "situation" }
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val navy = Color.rgb(4, 18, 31)
        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(40, 48, 40, 48)
            setBackgroundColor(navy)
        }
        val title = TextView(this).apply {
            text = "Know your rights"
            textSize = 26f
            setTextColor(Color.WHITE)
            setTypeface(typeface, Typeface.BOLD)
        }
        val subtitle = TextView(this).apply {
            text = "Free guest help. This is general legal information, not a substitute for a licensed Georgia attorney. Stay calm. Do not resist, lie, or destroy evidence."
            textSize = 14f
            setTextColor(Color.rgb(190, 205, 215))
        }
        val question = EditText(this).apply {
            hint = "Describe the encounter or rights question"
            setText(intent.getStringExtra(EXTRA_SITUATION).orEmpty())
            setHintTextColor(Color.rgb(150, 172, 190))
            setTextColor(Color.WHITE)
            minLines = 4
            gravity = Gravity.TOP
        }
        val answer = TextView(this).apply {
            textSize = 15f
            setTextColor(Color.WHITE)
        }
        val ask = Button(this).apply {
            text = "Ask without signing in"
            isAllCaps = false
            setOnClickListener {
                val q = question.text.toString().trim()
                if (q.isBlank()) {
                    Toast.makeText(this@GuestRightsActivity, "Describe what is happening first.", Toast.LENGTH_LONG).show()
                    return@setOnClickListener
                }
                Toast.makeText(this@GuestRightsActivity, "Looking up guest rights help…", Toast.LENGTH_SHORT).show()
                thread {
                    try {
                        val pack = GuestPublicApi.encounter(BuildConfig.API_BASE_URL, q)
                        val raw = GuestPublicApi.rightsAssistant(BuildConfig.API_BASE_URL, q, "rights")
                        val text = guestRightsDisplay(pack, raw)
                        runOnUiThread { answer.text = text }
                    } catch (error: Exception) {
                        runOnUiThread { Toast.makeText(this@GuestRightsActivity, error.message ?: "Guest rights help is unavailable.", Toast.LENGTH_LONG).show() }
                    }
                }
            }
        }
        val back = Button(this).apply {
            text = "Back to sign in"
            isAllCaps = false
            setOnClickListener {
                startActivity(Intent(this@GuestRightsActivity, AuthActivity::class.java))
                finish()
            }
        }
        listOf(title, subtitle, question, ask, answer, back).forEach { root.addView(it) }
        setContentView(ScrollView(this).apply { setBackgroundColor(navy); addView(root) })
    }
}

/** Render the public encounter pack beside the rights-assistant answer. Index links are court pages, not current-law claims. */
internal fun guestRightsDisplay(pack: JSONObject, assistant: JSONObject): String {
    val analysis = GroundedLegalResult.answer(assistant).ifBlank { assistant.toString(2) }
    return buildString {
        append(analysis)
        val disclaimer = pack.optString("disclaimer")
        val limit = pack.optString("coverage_limit")
        if (disclaimer.isNotBlank()) append("\n\n").append(disclaimer)
        if (limit.isNotBlank()) append("\n\n").append(limit)
        val indexes = pack.optJSONArray("official_indexes")
        if (indexes != null && indexes.length() > 0) {
            append("\n\nOfficial indexes (not a complete code, and not a claim that any citation is current Georgia law):")
            for (i in 0 until indexes.length()) {
                val row = indexes.optJSONObject(i) ?: continue
                val url = row.optString("url")
                if (!url.startsWith("https://")) continue
                val title = row.optString("title").ifBlank { url }
                append("\n- ").append(title).append(" ").append(url)
            }
        }
        append("\n\nStay calm. Do not resist, lie, or destroy evidence. Private cases stay behind sign-in.")
    }
}
