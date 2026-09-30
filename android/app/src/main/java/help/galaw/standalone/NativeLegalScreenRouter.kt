package help.galaw.standalone

/**
 * Single application boundary used by native Android legal screens.
 *
 * Keeping screen actions here prevents MainActivity and future Compose screens from choosing
 * legacy/general-chat endpoints directly. Case lookup remains retrieval-only; substantive legal
 * analysis is delegated to the grounded mode-specific screen models.
 */
object NativeLegalScreenRouter {
    fun caseAnalysis(api: ApiClient, facts: String): CaseAnalysisScreenModel.ViewState =
        CaseAnalysisScreenModel.analyze(api, facts)

    fun caseLookup(api: ApiClient, query: String): CaseLookupScreenModel.ViewState =
        CaseLookupScreenModel.search(api, query)

    fun rights(api: ApiClient, facts: String): RightsScreenModel.ViewState =
        RightsScreenModel.analyze(api, facts)

    fun motions(api: ApiClient, facts: String): MotionsScreenModel.ViewState =
        MotionsScreenModel.analyze(api, facts)

    fun talkToMe(
        api: ApiClient,
        message: String,
        recentContext: String = "",
        languageInstruction: String = "Respond in English."
    ): TalkToMeScreenModel.ViewState =
        TalkToMeScreenModel.analyze(api, message, recentContext, languageInstruction)
}
