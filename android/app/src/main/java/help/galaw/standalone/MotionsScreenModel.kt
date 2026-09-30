package help.galaw.standalone

/**
 * Presentation boundary for the native Motions experience.
 *
 * Motion research is routed only through the grounded legal-assistant mode. The UI receives
 * the same authority-status rendering used by the other legal modes, preventing research-only
 * material from being silently presented as verified Georgia authority.
 */
object MotionsScreenModel {
    private const val MAX_FACTS_CHARS = 20_000

    data class ViewState(
        val question: String,
        val answer: String,
        val authoritySummary: String,
        val displayText: String
    )

    fun analyze(api: ApiClient, rawFacts: String): ViewState {
        val facts = rawFacts.trim()
        require(facts.isNotEmpty()) {
            "Describe the case facts, charge, court stage, and the issue you want a motion to address."
        }
        require(facts.length <= MAX_FACTS_CHARS) {
            "Motion request is too long. Use the key facts, charge, court stage, evidence issue, and requested relief."
        }

        val result = GroundedLegalMode.analyze(api, GroundedLegalMode.Mode.MOTIONS, facts)
        return ViewState(
            question = facts,
            answer = result.answer,
            authoritySummary = result.authoritySummary,
            displayText = result.displayText
        )
    }
}
