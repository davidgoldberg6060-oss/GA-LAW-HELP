package help.galaw.standalone

/** Native presentation boundary for the Talk to Me legal conversation. */
object TalkToMeScreenModel {
    private const val MAX_CONTEXT_CHARS = 12_000
    private const val MAX_MESSAGE_CHARS = 8_000

    /** Whole prompt must fit the guest grounded endpoint (POST /public/rights-assistant). */
    private const val MAX_REQUEST_CHARS = GuestPublicApi.MAX_QUERY_CHARS
    private const val CONTEXT_HEADER = "\nConversation so far (recent context only):\n"

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

        val preamble = buildString {
            append("Continue a focused GA.LAW.HELP legal-information conversation. ")
            append(languageInstruction.trim()).append(' ')
            append("Stay within Georgia law, rights, police encounters, criminal/civil legal procedure, motions, sentencing, incarceration/post-conviction issues, appeals, and verified legal programs. Do not answer unrelated general-chat questions.")
        }
        val userLine = "\nUser: $message"
        val fixedChars = preamble.length + userLine.length
        require(fixedChars <= MAX_REQUEST_CHARS) {
            "Your message is too long for Talk to Me. Please shorten it to about ${maxOf(0, MAX_REQUEST_CHARS - preamble.length - 7)} characters and focus on the key facts."
        }
        // Keep as much recent context as fits the guest endpoint limit; older context is dropped first.
        val contextBudget = minOf(MAX_CONTEXT_CHARS, MAX_REQUEST_CHARS - fixedChars - CONTEXT_HEADER.length)
        val context = if (contextBudget > 0) rawRecentContext.takeLast(contextBudget) else ""
        val prompt = buildString {
            append(preamble)
            if (context.isNotBlank()) append(CONTEXT_HEADER).append(context)
            append(userLine)
        }
        val result = GroundedLegalMode.analyze(api, GroundedLegalMode.Mode.TALK_TO_ME, prompt)
        return ViewState(message, result.answer, result.authoritySummary, result.displayText)
    }
}
