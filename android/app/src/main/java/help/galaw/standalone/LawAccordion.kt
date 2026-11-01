package help.galaw.standalone

import android.content.Intent
import android.graphics.Color
import android.net.Uri
import android.os.Handler
import android.os.Looper
import android.text.SpannableStringBuilder
import android.text.Spanned
import android.text.style.LeadingMarginSpan
import android.view.Gravity
import android.view.MotionEvent
import android.view.View
import android.view.ViewGroup
import android.widget.LinearLayout
import android.widget.ProgressBar
import android.widget.ScrollView
import android.widget.TextView
import org.json.JSONObject
import kotlin.concurrent.thread

/**
 * Tap a law, rule, regulation or case anywhere in the app: its FULL stored text expands inline
 * under the tapped item. Only one item is open at a time; tapping the open one collapses it.
 * The official source is a small optional link at the bottom, never the main tap action.
 */
object LawAccordion {
    /** Fetches {citation,title,text,note,source_url}. Replaced in tests. */
    var loader: (citation: String, id: Long?) -> JSONObject = { c, id -> GuestPublicApi.law(BuildConfig.API_BASE_URL, c, id) }
    private val cache = HashMap<String, JSONObject>()
    private var openKey: String? = null
    private var openPanel: View? = null
    private val main = Handler(Looper.getMainLooper())

    fun isOpen(citation: String) = openKey == key(citation)
    private fun key(c: String) = c.replace(Regex("\\s*\\(text as of[^)]*\\)"), "").trim()

    fun collapse() { (openPanel?.parent as? ViewGroup)?.removeView(openPanel); openPanel = null; openKey = null }

    fun toggle(anchor: View, citation: String, id: Long? = null, sourceUrl: String? = null) {
        val k = key(citation)
        val wasOpen = openKey == k
        collapse()
        if (wasOpen) return
        // Insert below the tapped item in the nearest vertical list (chat bubbles sit in a horizontal row).
        var target: View = anchor
        while ((target.parent as? LinearLayout)?.orientation == LinearLayout.HORIZONTAL) target = target.parent as View
        val parent = target.parent as? ViewGroup ?: return
        val ui = GaUi(anchor.context)
        val panel = LinearLayout(anchor.context).apply {
            orientation = LinearLayout.VERTICAL; setPadding(ui.dp(12), ui.dp(10), ui.dp(12), ui.dp(10))
            background = ui.rounded(Color.argb(240, 6, 18, 33), 10, GaUi.STROKE_SOFT, 1.2f)
            tag = "law-panel:$k"; contentDescription = "Full text of $k"
        }
        val spinner = LinearLayout(anchor.context).apply {
            orientation = LinearLayout.HORIZONTAL; gravity = Gravity.CENTER_VERTICAL
            addView(ProgressBar(anchor.context).apply { indeterminateTintList = android.content.res.ColorStateList.valueOf(GaUi.GOLD) }, LinearLayout.LayoutParams(ui.dp(22), ui.dp(22)).apply { rightMargin = ui.dp(10) })
            addView(ui.text("Loading full text…", 13.5f, GaUi.MUTED))
        }
        panel.addView(spinner)
        parent.addView(panel, parent.indexOfChild(target) + 1, LinearLayout.LayoutParams(-1, -2).apply { topMargin = ui.dp(6); bottomMargin = ui.dp(6) })
        openPanel = panel; openKey = k
        val show = { law: JSONObject? -> if (openPanel === panel) { panel.removeView(spinner); fill(ui, panel, k, law, sourceUrl) } }
        cache[k]?.let { show(it); return }
        thread {
            val law = runCatching { loader(k, id) }.getOrNull()
            if (law != null) cache[k] = law
            main.post { show(law) }
        }
    }

    private fun fill(ui: GaUi, panel: LinearLayout, citation: String, law: JSONObject?, fallbackUrl: String?) {
        val ctx = panel.context
        if (law == null) { panel.addView(ui.text("The full text of $citation isn't in GA.LAW.HELP yet, or you're offline. Tap again to retry later.", 14f, GaUi.MUTED)); return }
        fun s(k: String) = law.optString(k).takeIf { it.isNotBlank() && it != "null" }
        s("title")?.let { panel.addView(ui.text(it, 15f, GaUi.WHITE, ui.sansMedium).apply { setPadding(0, 0, 0, ui.dp(6)) }) }
        val body = ui.text(format(s("text") ?: "No text is stored for this item yet.", ui.dp(14)), 14.5f, GaUi.TEXT).apply { setTextIsSelectable(true); setLineSpacing(0f, 1.15f) }
        val scroll = ScrollView(ctx).apply {
            isVerticalScrollBarEnabled = true; addView(body)
            // Scroll the law text, not the page, while a finger is on it.
            setOnTouchListener { v, e -> v.parent.requestDisallowInterceptTouchEvent(e.action != MotionEvent.ACTION_UP && e.action != MotionEvent.ACTION_CANCEL); false }
        }
        body.measure(View.MeasureSpec.makeMeasureSpec(ctx.resources.displayMetrics.widthPixels - ui.dp(80), View.MeasureSpec.AT_MOST), View.MeasureSpec.UNSPECIFIED)
        val h = minOf(body.measuredHeight, ui.dp(420))
        panel.addView(scroll, LinearLayout.LayoutParams(-1, if (body.measuredHeight > ui.dp(420)) h else -2))
        s("note")?.let { panel.addView(ui.text("Note: $it", 12f, GaUi.MUTED).apply { setPadding(0, ui.dp(8), 0, 0) }) }
        val url = s("source_url") ?: fallbackUrl
        if (url != null && url.startsWith("https://")) panel.addView(ui.text("View official source", 12.5f, GaUi.BLUE_BRIGHT).apply {
            setPadding(0, ui.dp(8), 0, ui.dp(2)); isClickable = true; contentDescription = "View official source for $citation"
            setOnClickListener { runCatching { ctx.startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(url))) } }
        })
    }

    /** Paragraph breaks before (a)/(1)/(A)/(i) markers, indented by level. */
    fun format(raw: String, indentPx: Int): CharSequence {
        val text = raw.replace("\r", "").replace(Regex("[ \\t]+"), " ")
            .replace(Regex("(?<=[.;:])\\s+(?=\\((?:[a-z]{1,2}|\\d{1,3}|[A-Z]{1,2}|[ivx]{1,5})\\)\\s)"), "\n")
            .replace(Regex("\n{3,}"), "\n\n").trim()
        val sb = SpannableStringBuilder()
        text.split("\n").forEachIndexed { i, line ->
            val l = line.trim(); if (l.isEmpty()) return@forEachIndexed
            val level = when {
                Regex("^\\((?:i|ii|iii|iv|v|vi|vii|viii|ix|x)\\)\\s").containsMatchIn(l) -> 3
                Regex("^\\([a-z]{1,2}\\)\\s").containsMatchIn(l) -> 0
                Regex("^\\(\\d{1,3}\\)\\s").containsMatchIn(l) -> 1
                Regex("^\\([A-Z]{1,2}\\)\\s").containsMatchIn(l) -> 2
                else -> 0
            }
            if (sb.isNotEmpty()) sb.append("\n\n")
            val start = sb.length; sb.append(l)
            if (level > 0) sb.setSpan(LeadingMarginSpan.Standard(indentPx * level), start, sb.length, Spanned.SPAN_EXCLUSIVE_EXCLUSIVE)
        }
        return sb
    }
}
