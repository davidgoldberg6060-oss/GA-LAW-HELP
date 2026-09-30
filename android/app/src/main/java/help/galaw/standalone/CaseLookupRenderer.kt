package help.galaw.standalone

/**
 * Plain-text renderer for native Case Lookup results.
 *
 * It deliberately preserves missing metadata and labels unverified document identifiers so the
 * UI cannot accidentally present a docket/document id as a reporter citation or verified law.
 */
object CaseLookupRenderer {
    fun render(result: CaseLookupController.Result): String {
        if (result.hits.isEmpty()) {
            return "No matching Georgia corpus records were found for “${result.query}”."
        }
        return buildString {
            append("Georgia corpus matches: ").append(result.total).append('\n')
            result.hits.forEachIndexed { index, hit ->
                if (index > 0) append("\n\n")
                append(index + 1).append(". ")
                append(hit.title.ifBlank { "Untitled corpus record" })
                if (hit.citation.isNotBlank()) {
                    append("\nCitation / identifier: ").append(hit.citation)
                }
                if (hit.court.isNotBlank()) append("\nCourt: ").append(hit.court)
                if (hit.date.isNotBlank()) append("\nDate: ").append(hit.date)
                if (hit.status.isNotBlank()) append("\nStatus: ").append(hit.status)
                if (hit.sourceId.isNotBlank()) append("\nCorpus source ID: ").append(hit.sourceId)
                if (hit.citation.endsWith("[UNVERIFIED DOCUMENT ID]")) {
                    append("\nResearch record only — this identifier is not a verified legal citation or current authority.")
                }
            }
        }
    }
}
