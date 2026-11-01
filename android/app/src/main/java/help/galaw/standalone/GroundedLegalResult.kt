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
            "what_appears_to_be_happening" to "What's happening",
            "safest_immediate_steps" to "Stay safe right now",
            "your_rights" to "Your rights",
            "law_enforcement_limits" to "What police can and can't do",
            "lawful_things_to_say_or_do" to "What to say or do"
        ),
        "case_analysis" to listOf(
            "facts_to_verify" to "Facts to confirm",
            "legal_issues" to "Legal issues",
            "prosecution_arguments" to "The other side's arguments",
            "defense_arguments" to "Your side's arguments",
            "possible_motions" to "Possible motions",
            "practical_next_steps" to "Next steps"
        ),
        "rights" to listOf(
            "situation" to "Your situation",
            "rights_that_may_apply" to "Rights that may apply",
            "law_enforcement_authority" to "What police can do",
            "law_enforcement_limits" to "What police can't do",
            "lawful_options" to "Your options"
        ),
        "motions" to listOf(
            "case_issue" to "The issue",
            "potential_motions" to "Possible motions",
            "required_facts_or_evidence" to "Facts or evidence needed",
            "opposing_arguments" to "The other side's arguments",
            "procedural_questions_to_verify" to "Questions to check"
        )
    )

    /** Server text is already clean plain text; strip any leftover markdown/meta just in case. */
    fun answer(result: JSONObject): String {
        val analysis = result.optString("analysis").trim().takeUnless { it == "null" }.orEmpty()
        if (analysis.isNotBlank()) return AnswerFormat.plain(analysis)
        val sections = result.optJSONObject("sections")
        val ordered = sectionOrder[result.optString("mode")].orEmpty()
        if (sections != null) return AnswerFormat.plain(ordered.mapNotNull { (k, h) -> sections.optString(k).trim().takeIf { it.isNotBlank() }?.let { "$h\n$it" } }.joinToString("\n\n"))
        return ""
    }

    /** (citation, short title) for each law the answer cites. Only verified records, never URLs or status labels. */
    fun lawsCited(result: JSONObject): List<Pair<String, String>> {
        val laws = result.optJSONArray("laws_cited")
        if (laws != null) return (0 until laws.length()).mapNotNull { laws.optJSONObject(it) }.map { it.optString("citation") to it.optString("title") }.filter { it.first.isNotBlank() }
        val authorities = result.optJSONArray("authorities") ?: JSONArray()
        return (0 until authorities.length()).mapNotNull { authorities.optJSONObject(it) }
            .filter { it.optString("verification_status").lowercase() in setOf("verified", "official", "validated", "confirmed") }
            .map { a ->
                val cite = (a.optString("citation_raw").ifBlank { a.optString("citation") }).replace(Regex("\\s*\\(text as of[^)]*\\)"), "")
                cite to a.optString("title").removePrefix(cite).trimStart('.', ' ').substringBefore(";").take(90)
            }.filter { it.first.isNotBlank() }
    }

    /** Compact "Laws cited" block appended under an answer. */
    fun authoritySummary(result: JSONObject): String = AnswerFormat.lawsBlock(lawsCited(result))
}
