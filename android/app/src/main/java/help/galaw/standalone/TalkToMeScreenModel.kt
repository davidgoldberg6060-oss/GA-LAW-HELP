package help.galaw.standalone

/** Native presentation boundary for the Talk to Me legal conversation. */
object TalkToMeScreenModel {
    private const val MAX_CONTEXT_CHARS = 12_000
    private const val MAX_MESSAGE_CHARS = 8_000

    data class ViewState(
        val message: String,
        val answer: String,
        val authoritySummary: String,
        val displayText: String
    )

    fun analyze(api: ApiClient, rawMessage: String, rawRecentContext: String = "", languageInstruction: String = "Respond in English."): ViewState {
        val message = rawMessage.trim()
        require(message.isNotEmpty()) { "Enter a Georgia legal question or describe what is happening." }
        require(message.length <= MAX_MESSAGE_CHARS) { "Message is too long. Use the key legal facts and question." }

        val context = rawRecentContext.takeLast(MAX_CONTEXT_CHARS)
        val prompt = buildString {
            append("Continue a focused GA.LAW.HELP legal-information conversation. ")
            append(languageInstruction.trim()).append(' ')
            append("Stay within Georgia law, rights, police encounters, criminal/civil legal procedure, motions, sentencing, incarceration/post-conviction issues, appeals, and verified legal programs. Do not answer unrelated general-chat questions.")
            if (context.isNotBlank()) append("\nConversation so far (recent context only):\n").append(context)
            append("\nUser: ").append(message)
        }
        val result = GroundedLegalMode.analyze(api, GroundedLegalMode.Mode.TALK_TO_ME, prompt)
        return ViewState(message, result.answer, result.authoritySummary, result.displayText)
    }
}
