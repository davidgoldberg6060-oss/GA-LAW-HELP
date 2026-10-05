package help.galaw.standalone

/**
 * Native Talk to Me controller. Keeps transcript mutation and grounded legal analysis out of
 * Activity UI code so the screen cannot accidentally fall back to an ungrounded endpoint.
 */
object TalkToMeController {
    data class Reply(
        val transcriptEntry: String,
        val answer: String,
        val authoritySummary: String
    )

    fun reply(
        api: ApiClient,
        history: CharSequence,
        message: String,
        languageInstruction: String
    ): Reply {
        // Load the public encounter pack without a session. A pack failure must not block the answer.
        runCatching { GuestPublicApi.encounter(BuildConfig.API_BASE_URL, message) }
        val turn = GroundedConversation.analyze(api, history, message, languageInstruction)
        return Reply(
            transcriptEntry = turn.transcriptEntry,
            answer = turn.answer,
            authoritySummary = turn.authoritySummary
        )
    }

    fun append(history: StringBuilder, reply: Reply) {
        history.append(reply.transcriptEntry)
    }
}
