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
            Mode.MOTIONS -> api.motionsAnalysis(clean)
            Mode.RIGHTS, Mode.TALK_TO_ME -> guestRights(mode, clean)
        }
        val answer = GroundedLegalResult.answer(raw).ifBlank {
            "No grounded legal analysis was returned. Add specific facts, the court, case stage, charge, or legal issue and try again."
        }
        val authoritySummary = GroundedLegalResult.authoritySummary(raw)
        val displayText = buildString {
            append(answer)
            if (authoritySummary.isNotBlank()) append("\n\n").append(authoritySummary)
            if (mode == Mode.RIGHTS || mode == Mode.TALK_TO_ME) {
                append("\n\nStay calm. Do not resist, lie, or destroy evidence. This is general information, not a claim that any citation is current Georgia law.")
            }
        }
        return Result(mode, raw, answer, authoritySummary, displayText)
    }

    private fun guestRights(mode: Mode, query: String): JSONObject {
        val base = BuildConfig.API_BASE_URL
        val encounter = GuestPublicApi.encounter(base, query)
        val assistant = GuestPublicApi.rightsAssistant(base, query, mode.wireName)
        if (!assistant.has("coverage_notice") && encounter.has("disclaimer")) {
            assistant.put("coverage_notice", encounter.optString("disclaimer"))
        }
        if (!assistant.has("official_indexes") && encounter.has("official_indexes")) {
            assistant.put("official_indexes", encounter.get("official_indexes"))
        }
        assistant.put("guest", true)
        assistant.put("login_required", false)
        return assistant
    }
}
