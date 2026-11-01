package help.galaw.standalone

import android.content.Intent
import android.graphics.Color
import android.graphics.Typeface
import android.graphics.drawable.GradientDrawable
import android.net.Uri
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

/** Navy and gold Georgia Laws screen: official code index and court opinion indexes. */
class GeorgiaLawsActivity : AppCompatActivity() {
    private val navy = Color.rgb(2, 17, 29)
    private val panel = Color.rgb(7, 29, 47)
    private val gold = Color.rgb(226, 181, 78)
    private val blue = Color.rgb(38, 169, 255)
    private val muted = Color.rgb(175, 194, 208)
    private var selected = GeorgiaLawTitles.titles.first()
    private var codeTab = true

    private fun dp(v: Int) = (v * resources.displayMetrics.density).toInt()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState); SystemBars.apply(this);render()
    }

    private fun render() {
        val shell = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL; setBackgroundColor(navy) }
        val body = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(dp(16), dp(14), dp(16), dp(24))
        }
        body.addView(TextView(this).apply {
            text = "←  Georgia Laws"
            textSize = 22f
            setTextColor(gold)
            setTypeface(typeface, Typeface.BOLD)
            setOnClickListener { finish() }
        })
        body.addView(note(GeorgiaLawTitles.NOTICE))
        val chips = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL }
        GeorgiaLawTitles.titles.forEach { title ->
            chips.addView(Button(this).apply {
                text = "Title ${title.number} · ${title.name}"
                isAllCaps = false
                setTextColor(if (title.number == selected.number) navy else Color.WHITE)
                background = rounded(if (title.number == selected.number) gold else panel, gold)
                setOnClickListener { selected = title; render() }
            }, LinearLayout.LayoutParams(-1, -2).apply { setMargins(0, dp(4), 0, dp(4)) })
        }
        body.addView(chips)
        val tabs = LinearLayout(this).apply { orientation = LinearLayout.HORIZONTAL }
        tabs.addView(tabButton("Code", codeTab) { codeTab = true; render() }, LinearLayout.LayoutParams(0, -2, 1f))
        tabs.addView(tabButton("Case Law", !codeTab) { codeTab = false; render() }, LinearLayout.LayoutParams(0, -2, 1f))
        body.addView(tabs)
        if (codeTab) {
            body.addView(note("Unannotated official index for Title ${selected.number}. No Lexis editor notes are shown, and section text is not pasted from memory."))
            body.addView(linkButton("Code Revision Commission") { openUrl(selected.codeIndexUrl) })
            body.addView(linkButton("Unannotated electronic release") { openUrl(GeorgiaLawTitles.UNANNOTATED_RELEASE_URL) })
        } else {
            body.addView(note("Court opinion indexes for Title ${selected.number}. An empty local corpus is not filled in. Opinions are not verified as current law from this screen."))
            body.addView(linkButton("Supreme Court of Georgia opinions") { openUrl(GeorgiaLawTitles.SUPREME_OPINIONS_URL) })
            body.addView(linkButton("Court of Appeals opinions") { openUrl(GeorgiaLawTitles.APPEALS_OPINIONS_URL) })
        }
        val question = EditText(this).apply {
            hint = "Ask a guest question about Title ${selected.number}"
            setHintTextColor(muted)
            setTextColor(Color.WHITE)
            minLines = 3
            gravity = Gravity.TOP
            setPadding(dp(12), dp(10), dp(12), dp(10))
            background = rounded(panel, blue)
        }
        body.addView(question, LinearLayout.LayoutParams(-1, -2).apply { setMargins(0, dp(10), 0, 0) })
        val answer = note("Guest help uses /public/rights-assistant. Do not resist, lie, or destroy evidence. This is not a substitute for a licensed Georgia attorney.")
        body.addView(answer)
        body.addView(linkButton("Ask without signing in") {
            val q = question.text.toString().trim()
            if (q.isBlank()) {
                Toast.makeText(this, "Enter a question first.", Toast.LENGTH_SHORT).show()
                return@linkButton
            }
            thread {
                try {
                    val prompt = "Title ${selected.number} ${selected.name}. $q"
                    GuestPublicApi.encounter(BuildConfig.API_BASE_URL, prompt)
                    val raw = GuestPublicApi.rightsAssistant(BuildConfig.API_BASE_URL, prompt, "rights")
                    val text = raw.optString("answer").ifBlank { raw.optString("analysis") }
                        .ifBlank { raw.optString("coverage_notice", "No guest answer was returned. No citation was invented.") }
                    runOnUiThread { answer.text = text }
                } catch (error: Exception) {
                    runOnUiThread { answer.text = error.message ?: "Guest rights help is unavailable. No citation was invented." }
                }
            }
        })
        shell.addView(ScrollView(this).apply { addView(body) }, LinearLayout.LayoutParams(-1, -1))
        setContentView(shell)
    }

    private fun tabButton(label: String, active: Boolean, action: () -> Unit) = Button(this).apply {
        text = label
        isAllCaps = false
        setTextColor(if (active) navy else Color.WHITE)
        background = rounded(if (active) gold else panel, gold)
        setOnClickListener { action() }
    }

    private fun linkButton(label: String, action: () -> Unit) = Button(this).apply {
        text = label
        isAllCaps = false
        setTextColor(Color.WHITE)
        background = rounded(Color.rgb(10, 39, 62), blue)
        setOnClickListener { action() }
    }

    private fun note(value: String) = TextView(this).apply {
        text = value
        textSize = 13f
        setTextColor(muted)
        setPadding(0, dp(8), 0, dp(8))
    }

    private fun rounded(fill: Int, stroke: Int) = GradientDrawable().apply {
        setColor(fill)
        cornerRadius = dp(12).toFloat()
        setStroke(dp(1), stroke)
    }

    private fun openUrl(url: String) {
        runCatching { startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(url))) }
            .onFailure { Toast.makeText(this, "No browser is available for this official index.", Toast.LENGTH_LONG).show() }
    }
}
