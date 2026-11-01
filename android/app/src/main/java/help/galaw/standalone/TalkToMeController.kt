package help.galaw.standalone

/**
 * Native Talk to Me controller. Keeps transcript mutation and grounded legal analysis out of
 * Activity UI code so the screen cannot accidentally fall back to an ungrounded endpoint.
 */
object TalkToMeController {
    data class Reply(
        val transcriptEntry: String,
        val answer: String,
        val authoritySummary: String,
        val followUps: List<String> = emptyList(),
        val cached: Boolean = false,
        val caseStage: String = "",
        val caseStageLabel: String = ""
    )

    fun reply(
        api: ApiClient,
        history: CharSequence,
        message: String,
        languageInstruction: String
    ): Reply {
        // General Georgia legal Q&A (criminal and civil). Police-encounter help stays on Know Your Rights.
        val turn = GroundedConversation.analyze(api, history, message, languageInstruction)
        return Reply(
            transcriptEntry = turn.transcriptEntry,
            answer = turn.answer,
            authoritySummary = turn.authoritySummary,
            followUps = followUps(turn.result),
            cached = turn.result.optBoolean("cached"),
            caseStage = turn.result.optString("case_stage"),
            caseStageLabel = turn.result.optString("case_stage_label")
        )
    }

    fun followUps(raw: org.json.JSONObject): List<String> {
        val arr = raw.optJSONArray("follow_ups") ?: return emptyList()
        return (0 until arr.length()).map { arr.optString(it).trim() }.filter { it.isNotBlank() && it.length <= 120 }.take(3)
    }

    fun append(history: StringBuilder, reply: Reply) {
        history.append(reply.transcriptEntry)
    }
}
