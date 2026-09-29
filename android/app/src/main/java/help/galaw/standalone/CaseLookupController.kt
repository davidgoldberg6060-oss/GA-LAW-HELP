package help.galaw.standalone

import org.json.JSONArray
import org.json.JSONObject

/**
 * Native Case Lookup boundary for the app's internal Georgia legal corpus.
 *
 * Case Lookup is retrieval-only: it returns records that the backend actually indexed and
 * never asks a generative model to invent a case, citation, holding, docket number, or result.
 */
object CaseLookupController {
    private const val MAX_QUERY_CHARS = 2_000
    private const val DEFAULT_LIMIT = 25

    data class CaseHit(
        val title: String,
        val citation: String,
        val court: String,
        val date: String,
        val status: String,
        val sourceId: String
    )

    data class Result(
        val query: String,
        val hits: List<CaseHit>,
        val total: Int
    )

    fun lookup(api: ApiClient, rawQuery: String, limit: Int = DEFAULT_LIMIT): Result {
        val query = rawQuery.trim()
        require(query.isNotEmpty()) { "Enter a Georgia case, charge, citation, court, or legal issue." }
        require(query.length <= MAX_QUERY_CHARS) { "Case lookup query is too long." }
        val safeLimit = limit.coerceIn(1, 50)
        val payload = api.internalLegalSearch(query, "case_lookup", safeLimit)
        return Result(query, parseHits(payload), payload.optInt("total", parseHits(payload).size))
    }

    private fun parseHits(payload: JSONObject): List<CaseHit> {
        val items = firstArray(payload, "items", "results", "authorities", "matches") ?: JSONArray()
        return buildList {
            for (i in 0 until items.length()) {
                val item = items.optJSONObject(i) ?: continue
                // Do not manufacture missing metadata. Blank means the corpus did not supply it.
                add(
                    CaseHit(
                        title = item.optString("title").trim(),
                        citation = item.optString("citation").trim(),
                        court = item.optString("court").trim(),
                        date = item.optString("date", item.optString("decision_date")).trim(),
                        status = item.optString("status", item.optString("verification_status")).trim(),
                        sourceId = item.optString("source_id", item.optString("id")).trim()
                    )
                )
            }
        }
    }

    private fun firstArray(payload: JSONObject, vararg keys: String): JSONArray? {
        for (key in keys) payload.optJSONArray(key)?.let { return it }
        return null
    }
}
