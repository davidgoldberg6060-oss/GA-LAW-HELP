package help.galaw.standalone

import org.json.JSONArray
import org.json.JSONObject

/**
 * Converts the structured /internal/legal-assistant response into safe native copy.
 * The backend remains authoritative about which records may ground an answer; this
 * renderer never upgrades an authority's verification, currency, or precedential status.
 */
object GroundedLegalResult {
    private val sectionOrder = mapOf(
        "talk_to_me" to listOf(
            "what_appears_to_be_happening" to "WHAT APPEARS TO BE HAPPENING",
            "safest_immediate_steps" to "SAFEST IMMEDIATE STEPS",
            "your_rights" to "YOUR RIGHTS",
            "law_enforcement_limits" to "WHAT LAW ENFORCEMENT MAY / MAY NOT DO",
            "lawful_things_to_say_or_do" to "WHAT TO SAY OR DO",
            "verified_georgia_authority" to "VERIFIED GEORGIA AUTHORITY",
            "important_limitations" to "IMPORTANT LIMITATIONS"
        ),
        "case_analysis" to listOf(
            "facts_to_verify" to "FACTS TO VERIFY",
            "legal_issues" to "LEGAL ISSUES",
            "prosecution_arguments" to "PROSECUTION ARGUMENTS",
            "defense_arguments" to "DEFENSE ARGUMENTS",
            "possible_motions" to "POSSIBLE MOTIONS",
            "practical_next_steps" to "PRACTICAL NEXT STEPS",
            "verified_georgia_authority" to "VERIFIED GEORGIA AUTHORITY",
            "important_limitations" to "IMPORTANT LIMITATIONS"
        ),
        "rights" to listOf(
            "situation" to "SITUATION",
            "rights_that_may_apply" to "RIGHTS THAT MAY APPLY",
            "law_enforcement_authority" to "LAW ENFORCEMENT AUTHORITY",
            "law_enforcement_limits" to "LAW ENFORCEMENT LIMITS",
            "lawful_options" to "LAWFUL OPTIONS",
            "verified_georgia_authority" to "VERIFIED GEORGIA AUTHORITY",
            "important_limitations" to "IMPORTANT LIMITATIONS"
        ),
        "motions" to listOf(
            "case_issue" to "CASE ISSUE",
            "potential_motions" to "POTENTIAL MOTIONS",
            "required_facts_or_evidence" to "REQUIRED FACTS OR EVIDENCE",
            "opposing_arguments" to "OPPOSING ARGUMENTS",
            "procedural_questions_to_verify" to "PROCEDURAL QUESTIONS TO VERIFY",
            "verified_georgia_authority" to "VERIFIED GEORGIA AUTHORITY",
            "important_limitations" to "IMPORTANT LIMITATIONS"
        )
    )

    fun answer(result: JSONObject): String {
        val sections = result.optJSONObject("sections")
        val mode = result.optString("mode")
        val ordered = sectionOrder[mode].orEmpty()
        if (sections != null && ordered.any { sections.optString(it.first).isNotBlank() }) {
            return buildString {
                ordered.forEach { (key, heading) ->
                    val value = sections.optString(key).trim()
                    if (value.isNotBlank()) append(heading).append('\n').append(value).append("\n\n")
                }
            }.trim()
        }
        return result.optString("analysis").trim()
    }

    fun authoritySummary(result: JSONObject): String {
        val authorities = result.optJSONArray("authorities") ?: JSONArray()
        val groundedCount = result.optInt("grounded_authority_count", 0)
        val notice = result.optString("coverage_notice").trim()
        return buildString {
            append("Verified authorities used to ground this answer: ").append(groundedCount)
            if (notice.isNotBlank()) append("\n").append(notice)
            for (i in 0 until authorities.length()) {
                val authority = authorities.optJSONObject(i) ?: continue
                append("\n\n").append(authority.optString("citation", authority.optString("title", "Georgia authority")))
                val title = authority.optString("title").trim()
                if (title.isNotBlank()) append("\n").append(title)
                append("\nVerification: ").append(authority.optString("verification_status", "unknown"))
                append(" • Currency: ").append(authority.optString("currency_status", "unknown"))
                append(" • Precedential status: ").append(authority.optString("precedential_status", "unknown"))
                val source = authority.optString("source_url").trim()
                if (source.startsWith("https://")) append("\nSource: ").append(source)
                if (authority.optBoolean("usable_as_support", true).not()) append("\nResearch only — not used as supporting authority.")
            }
        }
    }
}
