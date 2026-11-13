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
        val caseStageLabel: String = "",
        val helpResources: List<HelpResource> = emptyList(),
        /** Server id of the remembered exchange (0 = not remembered). */
        val turnId: Long = 0L,
        /** Automatic Defense Plan: "built", "needs_details", or "" for a normal answer. */
        val planStatus: String = "",
        val publicDefenderProblems: Boolean = false
    )

    /** One verified "Where to get help" entry from the server catalogue (https link, optional phone). */
    data class HelpResource(val name: String, val url: String, val phone: String)

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
            caseStageLabel = turn.result.optString("case_stage_label"),
            helpResources = helpResources(turn.result),
            turnId = turn.turnId,
            planStatus = turn.result.optJSONObject("defense_plan")?.optString("status").orEmpty(),
            publicDefenderProblems = turn.result.optBoolean("public_defender_problems")
        )
    }

    fun followUps(raw: org.json.JSONObject): List<String> {
        val arr = raw.optJSONArray("follow_ups") ?: return emptyList()
        return (0 until arr.length()).map { arr.optString(it).trim() }.filter { it.isNotBlank() && it.length <= 120 }.take(3)
    }

    fun helpResources(raw: org.json.JSONObject): List<HelpResource> {
        val arr = raw.optJSONArray("help_resources") ?: return emptyList()
        return (0 until arr.length()).mapNotNull { arr.optJSONObject(it) }.mapNotNull { o ->
            val url = o.optString("url").trim()
            val name = o.optString("name").trim()
            val phone = o.optString("phone").takeIf { o.has("phone") && !o.isNull("phone") }.orEmpty().trim()
            if (name.isBlank() || !url.startsWith("https://")) null else HelpResource(name, url, phone)
        }.take(8)
    }

    /** Digits-only tel: URI for an official phone number, or "" when none. */
    fun telUri(phone: String): String {
        val digits = phone.filter { it.isDigit() }
        return if (digits.length in 10..11) "tel:$digits" else ""
    }

    fun append(history: StringBuilder, reply: Reply) {
        history.append(reply.transcriptEntry)
    }
}
