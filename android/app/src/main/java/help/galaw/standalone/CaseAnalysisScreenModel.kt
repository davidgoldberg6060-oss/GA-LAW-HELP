package help.galaw.standalone

/**
 * Presentation boundary for native Case Analysis.
 *
 * Case analysis is substantive legal work, so it must use the grounded case-analysis backend
 * rather than general chat or raw retrieval. Authority status is preserved in displayText so
 * research-only material cannot be silently presented as verified Georgia authority.
 */
object CaseAnalysisScreenModel {
    private const val MAX_FACTS_CHARS = 30_000

    data class ViewState(
        val facts: String,
        val answer: String,
        val authoritySummary: String,
        val displayText: String
    )

    fun analyze(api: ApiClient, rawFacts: String): ViewState {
        val facts = rawFacts.trim()
        require(facts.isNotEmpty()) {
            "Describe the case facts, charges or claims, court, case stage, evidence, and what you need help understanding."
        }
        require(facts.length <= MAX_FACTS_CHARS) {
            "Case analysis is too long. Use the key facts, charges or claims, court, stage, evidence, deadlines, and disputed issues."
        }

        val result = GroundedLegalMode.analyze(api, GroundedLegalMode.Mode.CASE_ANALYSIS, facts)
        return ViewState(
            facts = facts,
            answer = result.answer,
            authoritySummary = result.authoritySummary,
            displayText = result.displayText
        )
    }
}
