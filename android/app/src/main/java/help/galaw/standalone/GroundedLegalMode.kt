package help.galaw.standalone

import org.json.JSONObject

/**
 * Single native boundary for legal AI modes. All substantive legal answers pass through
 * the grounded backend and the same authority renderer so the UI cannot silently upgrade
 * research-only material into supporting authority.
 *
 * Guest rights and talk-to-me use unauthenticated public endpoints. Private case and
 * motion analysis remain on login-only internal endpoints.
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
        if (mode == Mode.RIGHTS || mode == Mode.TALK_TO_ME) {
            require(clean.length <= GuestPublicApi.MAX_QUERY_CHARS) { GuestPublicApi.QUERY_TOO_LONG_MESSAGE }
        }

        val raw = when (mode) {
            Mode.CASE_ANALYSIS -> api.caseAnalysisWithVerifiedAuthorities(clean)
            Mode.RIGHTS -> GuestPublicApi.rightsAssistant(BuildConfig.API_BASE_URL, clean, "rights")
            Mode.MOTIONS -> api.motionsAnalysis(clean)
            Mode.TALK_TO_ME -> GuestPublicApi.rightsAssistant(BuildConfig.API_BASE_URL, clean, "talk_to_me")
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
