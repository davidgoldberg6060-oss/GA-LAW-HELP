package help.galaw.standalone

/**
 * Presentation boundary for the native Case Lookup screen.
 *
 * Keeps the Activity free of corpus parsing and prevents UI code from silently falling back
 * to legacy authority search or generative legal answers. Search results come only from the
 * internal Georgia corpus through CaseLookupController and are labeled by CaseLookupRenderer.
 */
object CaseLookupScreenModel {
    data class ViewState(
        val query: String,
        val title: String,
        val body: String,
        val resultCount: Int
    )

    /** Older call sites used State; keep that name as an alias of ViewState. */
    typealias State = ViewState

    fun search(api: ApiClient, rawQuery: String): ViewState {
        val result = CaseLookupController.lookup(api, rawQuery)
        return ViewState(
            query = result.query,
            title = "GEORGIA CASE LOOKUP",
            body = CaseLookupRenderer.render(result),
            resultCount = result.hits.size
        )
    }
}
