package help.galaw.standalone

import android.graphics.Typeface
import android.text.SpannableStringBuilder
import android.text.Spanned
import android.text.style.ForegroundColorSpan
import android.text.style.LeadingMarginSpan
import android.text.style.RelativeSizeSpan
import android.text.style.StyleSpan

/**
 * Renders AI answers for chat bubbles and result cards: short friendly headings in bold,
 * "•" bullets with a hanging indent, and no raw markdown (#, **, *) ever shown.
 */
object AnswerFormat {
    const val LAWS_HEADING = "Laws cited"

    /** Compact "Laws cited" block: citation — short title, one per line (no URLs or status labels). */
    fun lawsBlock(items: List<Pair<String, String>>): String =
        if (items.isEmpty()) "" else LAWS_HEADING + "\n" + items.joinToString("\n") { (c, t) -> "• " + c + (if (t.isNotBlank()) " — $t" else "") }

    private val meta = Regex(
        "(?i)\\b(supplied|provided|retrieved|indexed|traceable)\\s+(verified\\s+)?(georgia\\s+)?(authorit|statute|law|source|record)" +
            "|\\bverified (indexed )?(georgia )?authorit|\\bthis system\\b|\\bgrounding\\b|\\bdatabase\\b|\\bcorpus\\b|" +
            "precedential status|currency: unknown")

    /** Plain text with markdown removed (also used for share/copy). */
    fun plain(raw: String): String {
        val out = ArrayList<String>()
        for (line0 in raw.replace("\r", "").lines()) {
            var line = line0.trimEnd()
            val isHeading = Regex("^\\s*#{1,6}\\s*").containsMatchIn(line) || Regex("^\\s*\\*\\*[^*]+\\*\\*:?\\s*$").matches(line)
            line = line.replace(Regex("^\\s*#{1,6}\\s*"), "")
            line = line.replace(Regex("\\*\\*(.+?)\\*\\*"), "$1").replace(Regex("__(.+?)__"), "$1")
            line = line.replace(Regex("^\\s*[*+\\-]\\s+"), "• ").replace(Regex("^\\s*\\d+[.)]\\s+"), "• ")
            line = line.replace(Regex("(?<![\\w*])\\*(?!\\s)(.+?)(?<!\\s)\\*(?!\\w)"), "$1").replace("`", "")
            if (isHeading) line = friendlyHeading(line)
            if (line.startsWith("Verified authorities used to ground") || line.startsWith("Grounding includes") ||
                line.startsWith("Verification:") || line.startsWith("Source: https://archive.org")) continue
            if (meta.containsMatchIn(line)) {
                line = line.split(Regex("(?<=[.!?])\\s+")).filterNot { meta.containsMatchIn(it) }.joinToString(" ")
                if (line.isBlank()) continue
            }
            out.add(line)
        }
        return out.joinToString("\n").replace(Regex("\n{3,}"), "\n\n").trim()
    }

    private fun friendlyHeading(h: String): String {
        val t = h.trim().trimEnd(':')
        if (t.isEmpty() || t != t.uppercase()) return t
        return t.lowercase().replaceFirstChar { it.uppercase() }.replace("georgia", "Georgia")
    }

    private fun looksLikeHeading(line: String, next: String?): Boolean {
        val t = line.trim()
        if (t.isEmpty() || t.startsWith("•") || t.length > 60 || t.endsWith(".") || t.endsWith("?") || t.endsWith("!") || t.endsWith(",")) return false
        if (t.startsWith("Note:")) return false
        return next != null && next.isNotBlank()
    }

    /** Styled text for a TextView. [accent] colors headings. */
    fun styled(raw: String, accent: Int = GaUi.GOLD, onLaw: ((String) -> Unit)? = null): CharSequence {
        val lines = plain(raw).lines()
        val sb = SpannableStringBuilder()
        var inLaws = false
        lines.forEachIndexed { i, line ->
            if (line.trim().equals(LAWS_HEADING, ignoreCase = true)) inLaws = true
            val start = sb.length
            sb.append(line)
            val end = sb.length
            val next = lines.drop(i + 1).firstOrNull { it.isNotBlank() }
            when {
                looksLikeHeading(line, next) -> {
                    sb.setSpan(StyleSpan(Typeface.BOLD), start, end, Spanned.SPAN_EXCLUSIVE_EXCLUSIVE)
                    sb.setSpan(ForegroundColorSpan(accent), start, end, Spanned.SPAN_EXCLUSIVE_EXCLUSIVE)
                    sb.setSpan(RelativeSizeSpan(1.04f), start, end, Spanned.SPAN_EXCLUSIVE_EXCLUSIVE)
                }
                line.startsWith("• ") -> {
                    sb.setSpan(LeadingMarginSpan.Standard(0, 28), start, end, Spanned.SPAN_EXCLUSIVE_EXCLUSIVE)
                    if (inLaws && onLaw != null) {
                        val cite = line.removePrefix("• ").substringBefore(" — ").trim()
                        sb.setSpan(object : android.text.style.ClickableSpan() {
                            override fun onClick(widget: android.view.View) { onLaw(cite) }
                            override fun updateDrawState(ds: android.text.TextPaint) { ds.color = GaUi.BLUE_BRIGHT; ds.isUnderlineText = false }
                        }, start + 2, start + 2 + cite.length, Spanned.SPAN_EXCLUSIVE_EXCLUSIVE)
                    }
                }
                line.startsWith("Note:") -> sb.setSpan(RelativeSizeSpan(0.88f), start, end, Spanned.SPAN_EXCLUSIVE_EXCLUSIVE)
            }
            if (i < lines.size - 1) sb.append('\n')
        }
        return sb
    }
}
