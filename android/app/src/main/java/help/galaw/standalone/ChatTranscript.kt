package help.galaw.standalone

/**
 * On-device transcript for an AI chat (Talk to Me, Case Chat). Deleting one message here removes it
 * from the screen AND from the context that is sent back to the AI on the next question, because
 * history is always rebuilt from this list. [onChange] fires after every add/delete/clear so the
 * saved on-phone copy ([ChatStore]) is rewritten (or wiped) at the same moment.
 */
class ChatTranscript(var onChange: ((ChatTranscript) -> Unit)? = null) {
    data class Message(val id: Long, val mine: Boolean, val text: String, val time: String, val shareText: String = text, val inContext: Boolean = true, val turn: Long = 0L)

    private val items = mutableListOf<Message>()
    private var nextId = 1L

    val messages: List<Message> get() = items.toList()

    fun add(mine: Boolean, text: String, time: String, shareText: String = text, inContext: Boolean = true): Message =
        Message(nextId++, mine, text, time, shareText, inContext).also { items.add(it); onChange?.invoke(this) }

    /** Hard-removes one message. Returns false when it was already gone. */
    fun delete(id: Long): Boolean = items.removeAll { it.id == id }.also { if (it) onChange?.invoke(this) }

    fun clear() { items.clear(); onChange?.invoke(this) }

    fun toJson(): String = org.json.JSONArray().apply {
        items.forEach { m -> put(org.json.JSONObject().put("id", m.id).put("mine", m.mine).put("text", m.text).put("time", m.time).put("share", m.shareText).put("ctx", m.inContext).put("turn", m.turn)) }
    }.toString()

    /** Restores a saved transcript (no [onChange] callback while loading). */
    fun load(json: String?) {
        items.clear()
        val arr = runCatching { org.json.JSONArray(json ?: "[]") }.getOrNull() ?: org.json.JSONArray()
        for (i in 0 until arr.length()) {
            val o = arr.optJSONObject(i) ?: continue
            val text = o.optString("text"); if (text.isBlank()) continue
            items.add(Message(o.optLong("id"), o.optBoolean("mine"), text, o.optString("time"), o.optString("share", text), o.optBoolean("ctx", true), o.optLong("turn", 0L)))
        }
        nextId = (items.maxOfOrNull { it.id } ?: 0L) + 1
    }

    fun hasAnswer(): Boolean = items.any { !it.mine }

    /** Links a question and its answer to the server's remembered exchange, so deleting either also
     *  makes the AI forget it (the server keeps this screen's thread for continuity). */
    fun tagTurn(ids: List<Long>, turn: Long) {
        if (turn <= 0L) return
        var changed = false
        for (i in items.indices) if (items[i].id in ids) { items[i] = items[i].copy(turn = turn); changed = true }
        if (changed) onChange?.invoke(this)
    }

    fun turnOf(id: Long): Long = items.firstOrNull { it.id == id }?.turn ?: 0L

    /** Case Chat history in the backend's {role, content} shape, most recent [max] turns. */
    fun roleHistory(max: Int = 20): List<Pair<String, String>> =
        items.filter { it.inContext && it.text.isNotBlank() }.takeLast(max).map { (if (it.mine) "user" else "assistant") to it.text }

    /** Talk to Me plain-text transcript, rebuilt from the remaining messages only. */
    fun transcript(): String = buildString {
        for (m in items.filter { it.inContext }) {
            if (m.mine) append("User: ").append(m.text.trim()).append('\n')
            else append("STANDALONE ASSISTANT: ").append(m.text.trim()).append("\n\n")
        }
    }
}
