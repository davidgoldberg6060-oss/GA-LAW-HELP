package help.galaw.standalone

import org.json.JSONObject

/**
 * Single native boundary for legal AI modes. All substantive legal answers pass through
 * the grounded backend and the same authority renderer so the UI cannot silently upgrade
 * research-only material into supporting authority.
 */
object GroundedLegalMode {
    enum class Mode(val wireName: String) {
        CASE_ANALYSIS("case_analysis"),
        RIGHTS("rights"),
        MOTIONS("motions"),
        TALK_TO_ME("talk_to_me")
    }

    data class Result(
        val mode: Mode,
        val raw: JSONObject,
        val answer: String,
        val authoritySummary: String,
        val displayText: String
    )

    fun analyze(api: ApiClient, mode: Mode, query: String): Result {
        val clean = query.trim()
        require(clean.isNotEmpty()) { "Legal question cannot be empty." }
        require(clean.length <= 50_000) { "Legal question is too large." }

        val raw = when (mode) {
            Mode.CASE_ANALYSIS -> api.caseAnalysisWithVerifiedAuthorities(clean)
            Mode.RIGHTS -> api.rightsAnalysis(clean)
            Mode.MOTIONS -> api.motionsAnalysis(clean)
            Mode.TALK_TO_ME -> api.talkToMeAnalysis(clean)
        }
        val answer = GroundedLegalResult.answer(raw).ifBlank {
            "No grounded legal analysis was returned. Add specific facts, the court, case stage, charge, or legal issue and try again."
        }
        val authoritySummary = GroundedLegalResult.authoritySummary(raw)
        val displayText = buildString {
            append(answer)
            if (authoritySummary.isNotBlank()) append("\n\n").append(authoritySummary)
        }
        return Result(mode, raw, answer, authoritySummary, displayText)
    }
}
