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

    fun chargeCheck(situation: String, r: GaScreens.ChargeCheckResult): String = buildString {
        append("Charge Check (Georgia) — estimate\n").append(r.estimateNote).append("\n\nWhat happened: ").append(situation.trim())
        if (r.charges.isNotEmpty()) { append("\n\nLIKELY CHARGES"); r.charges.forEach { c -> append("\n• ").append(c.charge).append(" — ").append(c.cite.citation).append(" (").append(c.levelLabel).append(")"); c.penalty?.let { append("\n  Penalty text: “").append(it).append("”") } } }
        listOf("POSSIBLE DEFENSES & WEAK SPOTS" to r.defenses, "WAYS TO GET THE LOWEST OUTCOME" to r.lowest).forEach { (h, list) ->
            if (list.isNotEmpty()) { append("\n\n").append(h); list.forEach { o -> append("\n• ").append(o.title).append(": ").append(o.explanation.trim()); if (o.citations.isNotEmpty()) append("\n").append(cites(o.citations)) } }
        }
        append(lawyerBlock(r.lawyer))
        append("\n\n").append(r.rightsReminder).append("\n").append(r.disclaimer)
    }

    fun civilCheck(situation: String, r: GaScreens.CivilCheckResult): String = buildString {
        append("Civil Case Check (Georgia) — estimate\n").append(r.estimateNote).append("\n\nThe dispute: ").append(situation.trim())
        if (r.claims.isNotEmpty()) { append("\n\nLIKELY CLAIMS & DEFENSES"); r.claims.forEach { c -> append("\n• [").append(c.sideLabel).append("] ").append(c.claim).append(" — ").append(c.cite.citation) } }
        r.court?.let { append("\n\nCOURT: ").append(it.label); it.limit?.let { l -> append("\n  From the law: “").append(l).append("”") } }
        if (r.deadlines.isNotEmpty()) { append("\n\nDEADLINES"); r.deadlines.forEach { d -> append("\n• ").append(d.title).append(": “").append(d.quote).append("” (").append(d.cite.citation).append(")") } }
        if (r.evidence.isNotEmpty()) { append("\n\nEVIDENCE TO GATHER"); r.evidence.forEach { append("\n• ").append(it) } }
        listOf("WEAK SPOTS" to r.weakSpots, "LOWEST-COST PATHS" to r.lowCost).forEach { (h, list) ->
            if (list.isNotEmpty()) { append("\n\n").append(h); list.forEach { o -> append("\n• ").append(o.title).append(": ").append(o.explanation.trim()); if (o.citations.isNotEmpty()) append("\n").append(cites(o.citations)) } }
        }
        append(lawyerBlock(r.lawyer))
        if (r.help.isNotEmpty()) { append("\n\nFIND LEGAL HELP"); r.help.forEach { append("\n• ").append(it.title).append(": ").append(it.url) } }
        append("\n\n").append(r.disclaimer)
    }
}
