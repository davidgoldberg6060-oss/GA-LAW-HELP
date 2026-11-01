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

class GuestRightsActivity : AppCompatActivity() {
    companion object { const val EXTRA_SITUATION = "situation" }
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val gui = GaUi(this)
        window.statusBarColor = GaUi.NAVY_TOP
        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(gui.dp(18), gui.dp(4), gui.dp(18), gui.dp(28))
        }
        val title = TextView(this).apply {
            text = "Know Your Rights"
            textSize = 28f
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
            setHintTextColor(GaUi.MUTED)
            setTextColor(Color.WHITE)
            minLines = 4
            gravity = Gravity.TOP
            background = gui.glowCard(GaUi.CARD, GaUi.STROKE_SOFT, 10, false)
            setPadding(gui.dp(14), gui.dp(12), gui.dp(14), gui.dp(12))
        }
        val answer = TextView(this).apply {
            textSize = 15f
            setTextColor(Color.WHITE)
        }
        val ask = gui.primaryButton("Ask without signing in") {}.apply {
            setOnClickListener {
                val q = question.text.toString().trim()
                if (q.isBlank()) {
                    Toast.makeText(this@GuestRightsActivity, "Describe what is happening first.", Toast.LENGTH_LONG).show()
                    return@setOnClickListener
                }
                Toast.makeText(this@GuestRightsActivity, "Looking up guest rights help…", Toast.LENGTH_SHORT).show()
                thread {
                    try {
                        GuestPublicApi.encounter(BuildConfig.API_BASE_URL, q)
                        val raw = GuestPublicApi.rightsAssistant(BuildConfig.API_BASE_URL, q, "rights")
                        val text = GroundedLegalResult.answer(raw).ifBlank { raw.toString(2) }
                        runOnUiThread { answer.text = text }
                    } catch (error: Exception) {
                        runOnUiThread { Toast.makeText(this@GuestRightsActivity, error.message ?: "Guest rights help is unavailable.", Toast.LENGTH_LONG).show() }
                    }
                }
            }
        }
        val back = gui.secondaryButton("Back") {}.apply {
            setOnClickListener { finish() }
        }
        listOf(title, subtitle, question, ask, answer, back).forEach { root.addView(it, LinearLayout.LayoutParams(-1, -2).apply { topMargin = gui.dp(10) }) }
        val shell = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL; background = gui.screenBackground() }
        shell.addView(gui.pageHeader { finish() })
        shell.addView(ScrollView(this).apply { addView(root) }, LinearLayout.LayoutParams(-1, 0, 1f))
        setContentView(shell)
    }
}
