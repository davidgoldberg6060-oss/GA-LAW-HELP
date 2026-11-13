package help.galaw.standalone

import org.json.JSONObject

/**
 * Keeps the native Talk to Me conversation on the grounded legal-assistant contract.
 * This adapter deliberately does not invent or upgrade authority metadata; rendering is
 * delegated to the shared GroundedLegalMode boundary.
 */
object GroundedConversation {
    private const val MAX_CONTEXT_CHARS = 12_000

    /** Whole request must fit the guest grounded endpoint (POST /public/rights-assistant). */
    private const val MAX_REQUEST_CHARS = GuestPublicApi.MAX_QUERY_CHARS
    private const val CONTEXT_HEADER = "Conversation so far (recent context only):\n"

    data class Turn(
        val request: String,
        val result: JSONObject,
        val answer: String,
        val authoritySummary: String,
        val transcriptEntry: String,
        /** Server id of this remembered exchange (0 when answered as a guest). */
        val turnId: Long = 0L
    )

    fun request(history: CharSequence, message: String, languageInstruction: String): String {
        val cleanMessage = message.trim()
        require(cleanMessage.isNotEmpty()) { "Message cannot be empty." }
        val preamble = buildString {
            append("Continue a focused STANDALONE ASSISTANT legal-information conversation. ")
            append(languageInstruction.trim())
            append(" Stay within Georgia law, rights, police encounters, criminal/civil legal procedure, motions, sentencing, incarceration/post-conviction issues, appeals, and verified legal programs. ")
            append("Use only the verified authorities supplied by the grounded legal-assistant retrieval layer as legal support. ")
            append("If verified authority is unavailable or insufficient, say so instead of inventing a statute, case, holding, citation, deadline, or procedural rule. ")
            append("Do not answer unrelated general-chat questions.\n")
        }
        val userLine = "User: $cleanMessage"
        val fixedChars = preamble.length + userLine.length
        require(fixedChars <= MAX_REQUEST_CHARS) {
            "Your message is too long for Talk to Me. Please shorten it to about ${maxOf(0, MAX_REQUEST_CHARS - preamble.length - 6)} characters and focus on the key facts."
        }
        // Keep as much recent history as fits; older turns are dropped first.
        val contextBudget = minOf(MAX_CONTEXT_CHARS, MAX_REQUEST_CHARS - fixedChars - CONTEXT_HEADER.length - 1)
        val recent = if (contextBudget > 0) history.toString().takeLast(contextBudget) else ""
        return buildString {
            append(preamble)
            if (recent.isNotBlank()) {
                append(CONTEXT_HEADER)
                append(recent)
                append('\n')
            }
            append(userLine)
        }
    }

    fun analyze(api: ApiClient, history: CharSequence, message: String, languageInstruction: String): Turn {
        // With this device's session the server keeps the AI Help thread (and one line about the latest
        // topic elsewhere in the app), so only the new message is sent. Without a session, fall back to
        // the guest endpoint with the on-phone history.
        val shared = runCatching { api.ensureSession(); api.token != null }.getOrDefault(false)
        if (shared) {
            val request = request("", message, languageInstruction)
            val raw = api.aiHelp(request)
            val answer = GroundedLegalResult.answer(raw).ifBlank {
                "No grounded legal analysis was returned. Add specific facts, the court, case stage, charge, or legal issue and try again."
            }
            val authorities = GroundedLegalResult.authoritySummary(raw)
            return Turn(request, raw, answer, authorities, entry(message, answer, authorities),
                raw.optJSONObject("continuity")?.optLong("turn_id", 0L) ?: 0L)
        }
        val request = request(history, message, languageInstruction)
        val grounded = GroundedLegalMode.analyze(api, GroundedLegalMode.Mode.TALK_TO_ME, request)
        val transcriptEntry = buildString {
            append("User: ").append(message.trim()).append('\n')
            append("STANDALONE ASSISTANT: ").append(grounded.answer)
            if (grounded.authoritySummary.isNotBlank()) append("\n\n").append(grounded.authoritySummary)
            append("\n\n")
        }
        return Turn(
            request = request,
            result = grounded.raw,
            answer = grounded.answer,
            authoritySummary = grounded.authoritySummary,
            transcriptEntry = transcriptEntry
        )
    }

    private fun entry(message: String, answer: String, authorities: String) = buildString {
        append("User: ").append(message.trim()).append('\n')
        append("STANDALONE ASSISTANT: ").append(answer)
        if (authorities.isNotBlank()) append("\n\n").append(authorities)
        append("\n\n")
    }
}
