package help.galaw.standalone

/**
 * Presentation boundary for the native Case Lookup screen.
 *
 * Keeps the Activity free of corpus parsing and prevents UI code from silently falling back
 * to legacy authority search or generative legal answers. Search results come only from the
 * internal Georgia corpus through CaseLookupController and are labeled by CaseLookupRenderer.
 */
object CaseLookupScreenModel {
    data class State(
        val query: String,
        val title: String,
        val body: String,
        val resultCount: Int
    )

    fun search(api: ApiClient, rawQuery: String): State {
        val result = CaseLookupController.lookup(api, rawQuery)
        return State(
            query = result.query,
            title = "GEORGIA CASE LOOKUP",
            body = CaseLookupRenderer.render(result),
            resultCount = result.hits.size
        )
    }
}
