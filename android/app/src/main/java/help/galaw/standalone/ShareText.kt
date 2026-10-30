package help.galaw.standalone

/** Plain-text versions of answers for the Share / Copy actions. Pure so it can be unit tested. */
object ShareText {
    const val NOTE = "From GA.LAW.HELP — general legal information, not legal advice. Talk to a Georgia attorney about your situation."

    private fun cites(list: List<GaScreens.LoopholeCite>): String =
        list.joinToString("\n") { c -> "• " + c.citation + (if (c.title.isNotBlank() && c.title != c.citation) " — ${c.title}" else "") + (c.sourceUrl?.let { "\n  $it" } ?: "") }

    private fun lawyerBlock(l: GaScreens.LawyerTake?): String = if (l == null || l.text.isBlank()) "" else buildString {
        append("\n\n").append(l.label.uppercase()).append("\n").append(l.text.trim())
        if (l.citations.isNotEmpty()) append("\n").append(cites(l.citations))
        append("\n(").append(l.disclaimer).append(")")
    }

    fun answer(question: String?, answer: String, lawyer: GaScreens.LawyerTake? = null): String = buildString {
        if (!question.isNullOrBlank()) append("Q: ").append(question.trim()).append("\n\n")
        append(answer.trim())
        append(lawyerBlock(lawyer))
        append("\n\n").append(NOTE)
    }

    fun loopholes(topic: String, findings: List<GaScreens.LoopholeFinding>, lawyer: GaScreens.LawyerTake?): String = buildString {
        append("Legal Loopholes — ").append(topic.trim()).append(" (Georgia)")
        findings.forEachIndexed { i, f ->
            append("\n\n").append(i + 1).append(". [").append(f.typeLabel).append("] ").append(f.title.trim()).append("\n").append(f.explanation.trim())
            if (f.citations.isNotEmpty()) append("\n").append(cites(f.citations))
        }
        append(lawyerBlock(lawyer))
        append("\n\n").append(NOTE)
    }
}
