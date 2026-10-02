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

        val raw = when (mode) {
            Mode.CASE_ANALYSIS -> api.caseAnalysisWithVerifiedAuthorities(clean)
            Mode.RIGHTS -> guestRightsAndEncounter(clean, "rights")
            Mode.MOTIONS -> api.motionsAnalysis(clean)
            Mode.TALK_TO_ME -> guestRightsAndEncounter(clean, "talk_to_me")
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

    /** Free research. Does not send a session and does not invent citations. */
    private fun guestRightsAndEncounter(query: String, mode: String): JSONObject {
        val encounter = GuestPublicApi.encounter(BuildConfig.API_BASE_URL, query)
        val assistant = GuestPublicApi.rightsAssistant(BuildConfig.API_BASE_URL, query, mode)
        if (assistant.optString("coverage_notice").isBlank()) {
            val notice = encounter.optString("disclaimer").ifBlank { encounter.optString("coverage_limit") }
            if (notice.isNotBlank()) assistant.put("coverage_notice", notice)
        }
        assistant.put("login_required", false)
        return assistant
    }
}
