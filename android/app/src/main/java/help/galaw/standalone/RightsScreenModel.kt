package help.galaw.standalone

/**
 * Presentation boundary for the native Rights experience.
 *
 * Rights answers are generated only through the grounded legal-assistant mode. This model
 * intentionally has no general-chat or legacy authority-search fallback, so a native screen
 * cannot accidentally present unsupported Georgia law as verified legal authority.
 */
object RightsScreenModel {
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
            "Describe what is happening so GA.LAW.HELP can research the relevant Georgia rights."
        }
        require(facts.length <= MAX_FACTS_CHARS) {
            "Rights description is too long. Use the key facts, what law enforcement did or asked, and what happened next."
        }

        val result = GroundedLegalMode.analyze(api, GroundedLegalMode.Mode.RIGHTS, facts)
        return ViewState(
            question = facts,
            answer = result.answer,
            authoritySummary = result.authoritySummary,
            displayText = result.displayText
        )
    }
}
