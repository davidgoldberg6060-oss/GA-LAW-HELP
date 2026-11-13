package help.galaw.standalone

/**
 * Splits a plain-text AI answer into a short "Quick answer" (1-3 sentences) and small collapsible
 * sections with item counts, so a phone screen shows a few lines instead of a wall of text.
 * Nothing is dropped: citation lists move to "Laws cited" and side notes become footnotes.
 * Pure Kotlin (unit-tested on the JVM); kept in step with the web's src/answerSections.ts.
 */
object AnswerSections {
    data class Item(val head: String, val detail: String? = null, val meta: String? = null)
    data class Section(val title: String, val kind: String, val items: MutableList<Item> = mutableListOf(), val notes: MutableList<String> = mutableListOf())
    data class Structured(val quick: String, val sections: List<Section>, val note: String)

    const val VISIBLE = 4
    private const val QUICK_SENTENCES = 3

    private val BULLET = Regex("^\\s*(?:[•●▪*-]|\\d{1,2}[.)])\\s+")
    private val QUICK = Regex("^(short answer|quick answer|what's happening|your situation|the issue|facts to confirm)$", RegexOption.IGNORE_CASE)
    private val TOP = setOf(
        "short answer", "quick answer", "how it works in georgia", "how it works", "steps you can take", "questions to ask your lawyer",
        "motions that could help", "deadlines and costs", "where to get help", "laws cited",
        "what's happening", "stay safe right now", "your rights", "what police can and can't do", "what to say or do",
        "facts to confirm", "legal issues", "the other side's arguments", "your side's arguments", "possible motions",
        "next steps", "your situation", "rights that may apply", "what police can do", "what police can't do",
        "your options", "the issue", "facts or evidence needed", "questions to check")
    private val RENAME = mapOf(
        "how it works in georgia" to "How it works", "challenging the evidence" to "Ways to fight the evidence",
        "rights and court procedure" to "Your rights in court", "information to gather for your lawyer" to "What to gather for your lawyer",
        "possible motions" to "Motions that could help")
    private val GROUP = Regex("^[A-Z][A-Za-z ,'’/&()-]{2,60}:$")
    private val CITE = Regex("O\\.C\\.G\\.A\\.\\s*§§?\\s*\\d{1,2}-\\d{1,3}-\\d+(?:\\.\\d+)?|Unif\\.\\s*(?:Super|State|Magis|Juv)\\.\\s*Ct\\.\\s*R\\.\\s*[\\d.]+")
    private val CITE_PAREN = Regex("\\s*\\([^()]*?(?:O\\.C\\.G\\.A\\.|Unif\\.\\s*\\w+\\.\\s*Ct\\.\\s*R\\.)[^()]*\\)")
    private val SIDE = Regex("^(tap\\s+[\"“]?open my case|a lawyer should decide|providers decide eligibility|contacting them doesn'?t guarantee)", RegexOption.IGNORE_CASE)
    private val ABBR = Regex("\\b(O\\.C\\.G\\.A|U\\.S\\.C|U\\.S|Ga|App|Ct|R|Super|Unif|v|No|St|Mr|Ms|Dr)\\.")

    fun kindOf(title: String): String {
        val t = title.lowercase()
        return when {
            "motion" in t -> "motions"; t.startsWith("questions") -> "questions"; t.startsWith("deadlines") -> "deadlines"
            t == "laws cited" -> "laws"; t.startsWith("where to get help") -> "help"; else -> "info"
        }
    }

    private fun cleanTitle(raw: String): String { val t = raw.trim().trimEnd(':').trim(); return RENAME[t.lowercase()] ?: t }

    fun isTopHeading(line: String): Boolean {
        val l = line.trim(); val t = l.trimEnd(':')
        if (t.lowercase() in TOP) return true
        if (t.isEmpty() || t.length > 50 || BULLET.containsMatchIn(t) || Regex("[.,;!?:]$").containsMatchIn(l)) return false
        return t[0].isUpperCase() && t.split(Regex("\\s+")).size <= 7
    }

    fun sentences(text: String): List<String> {
        val guarded = ABBR.replace(text) { it.value.replace('.', '\u0001') }
        return guarded.split(Regex("(?<=[.!?])\\s+(?=[A-Z0-9“\"(])")).map { it.replace('\u0001', '.').trim() }.filter { it.isNotEmpty() }
    }

    fun stripCitationLists(text: String): String =
        CITE_PAREN.replace(text, "").replace(Regex("\\s+([,.:;])"), "$1").replace(Regex("\\s{2,}"), " ").trim()

    fun citationsIn(text: String): List<String> = CITE.findAll(text).map { it.value.replace(Regex("\\s+"), " ").replace("§§", "§") }.distinct().toList()

    fun toItem(raw: String, kind: String): Item {
        val original = BULLET.replace(raw.trim(), "")
        val t = stripCitationLists(original)
        if (kind == "motions") {
            val withCite = Regex("^(.{3,110}?)\\s*\\([^()]*?(?:O\\.C\\.G\\.A\\.|Unif\\.)[^()]*\\):\\s+(.*)$").find(original)
            val parts = withCite?.let { listOf(it.groupValues[1], stripCitationLists(it.groupValues[2])) }
                ?: Regex("^(.{3,90}?):\\s+(.*)$").find(t)?.let { listOf(it.groupValues[1], it.groupValues[2]) }
            if (parts != null) {
                val rest = parts[1]
                val helps = Regex("How it can help:\\s*(.*?)(?=\\s+Timing:|$)", RegexOption.IGNORE_CASE).find(rest)?.groupValues?.get(1)?.trim()
                val timing = Regex("Timing:\\s*(.*)$", RegexOption.IGNORE_CASE).find(rest)?.groupValues?.get(1)?.trim()
                val purpose = rest.split(Regex("\\s+How it can help:", RegexOption.IGNORE_CASE))[0].split(Regex("\\s+Timing:", RegexOption.IGNORE_CASE))[0].trim()
                return Item(parts[0].trim(), (helps ?: purpose).ifBlank { null }, timing?.let { "When to file: $it" })
            }
        }
        if (kind == "help") {
            Regex("^([^.]{3,110})\\s+[—–]\\s+(.*)$").find(t)?.let { m ->
                return Item(m.groupValues[1].trim(), sentences(m.groupValues[2]).take(2).joinToString(" ").ifBlank { null })
            }
        }
        if (kind == "questions") return Item(t)
        Regex("^([^.!?]{3,70}):\\s+(.*)$").find(t)?.let { return Item(it.groupValues[1].trim(), it.groupValues[2].trim().ifBlank { null }) }
        val s = sentences(t)
        return if (s.size > 1) Item(s[0], s.drop(1).joinToString(" ")) else Item(t)
    }

    private fun lawKey(c: String) = c.replace(Regex("\\s*\\(text as of[^)]*\\)", RegexOption.IGNORE_CASE), "").replace(Regex("\\s+"), " ").trim().lowercase()

    fun structure(raw: String): Structured {
        val text = raw.replace("\r", "")
        val cites = citationsIn(text)
        val sections = mutableListOf<Section>()
        val quickParts = mutableListOf<String>()
        val lawLines = mutableListOf<Pair<String, String>>()
        var note = ""
        var top = ""
        var cur: Section? = null
        var sawHeading = false
        fun open(title: String) {
            val t = cleanTitle(title)
            cur = sections.firstOrNull { it.title.equals(t, true) } ?: Section(t, kindOf(t)).also { sections.add(it) }
        }
        for (raw0 in text.split("\n")) {
            val line = raw0.trim()
            if (line.isEmpty()) continue
            if (line.startsWith("Note:", true)) { note = line.substringAfter(":").trim(); continue }
            val bullet = BULLET.containsMatchIn(line)
            if (!bullet && isTopHeading(line)) {
                sawHeading = true; top = line.trimEnd(':').trim().lowercase(); cur = null
                if (!QUICK.matches(top) && top != "laws cited") open(line)
                continue
            }
            if (!bullet && GROUP.matches(line) && sawHeading && !QUICK.matches(top)) { open(line); continue }
            val body = BULLET.replace(line, "").trim()
            if (body.isEmpty()) continue
            if (top == "laws cited") {
                val p = body.split(Regex("\\s+[—–]\\s+"), limit = 2)
                if (p[0].isNotBlank()) lawLines.add(p[0].trim() to p.getOrElse(1) { "" })
                continue
            }
            if (QUICK.matches(top) || (!sawHeading && cur == null)) { quickParts.add(body); continue }
            if (cur == null) open("More about this")
            val sec = cur!!
            if (SIDE.containsMatchIn(body)) { sec.notes.add(body); continue }
            if ((sec.kind == "info" || sec.kind == "deadlines") && !Regex("^[^.!?]{3,70}:\\s").containsMatchIn(body)) {
                val parts = sentences(body)
                if (parts.size > 2 || (!bullet && body.length > 120)) { parts.forEach { sec.items.add(toItem(it, sec.kind)) }; continue }
            }
            if (!bullet && body.first().isLowerCase() && sec.items.isNotEmpty()) {
                val last = sec.items.removeAt(sec.items.size - 1)
                sec.items.add(last.copy(detail = ((last.detail ?: "") + " " + body).trim())); continue
            }
            sec.items.add(toItem(body, sec.kind))
        }
        val qs = sentences(stripCitationLists(quickParts.joinToString(" ")))
        var quick = qs.take(QUICK_SENTENCES).joinToString(" ")
        val overflow = qs.drop(QUICK_SENTENCES)
        if (quick.isEmpty()) sections.firstOrNull { it.items.isNotEmpty() }?.let { s -> val f = s.items.removeAt(0); quick = listOfNotNull(f.head, f.detail).joinToString(" ") }
        if (overflow.isNotEmpty()) {
            val target = sections.firstOrNull { it.kind == "info" && it.items.isNotEmpty() } ?: Section("More about this", "info").also { sections.add(0, it) }
            target.items.addAll(0, overflow.map { toItem(it, "info") })
        }
        val kept = sections.filter { it.items.isNotEmpty() || it.notes.isNotEmpty() }.toMutableList()
        val seen = HashSet<String>()
        val laws = (lawLines + cites.map { it to "" }).mapNotNull { (c, t) ->
            val k = lawKey(c); if (k.isEmpty() || !seen.add(k)) null else Item(c.replace(Regex("\\s*\\(text as of[^)]*\\)", RegexOption.IGNORE_CASE), "").trim(), t.ifBlank { null })
        }
        if (laws.isNotEmpty()) {
            val lawSec = Section(AnswerFormat.LAWS_HEADING, "laws", laws.toMutableList())
            val at = kept.indexOfFirst { it.kind == "help" }
            if (at >= 0) kept.add(at, lawSec) else kept.add(lawSec)
        }
        return Structured(quick, kept, note)
    }

    /** "Motion to suppress evidence · Demand for speedy trial · …" under a closed Motions title. */
    fun teaser(s: Section, n: Int = 2): String =
        if (s.kind != "motions" || s.items.isEmpty()) "" else s.items.take(n).joinToString(" · ") { it.head } + if (s.items.size > n) " · …" else ""
}
