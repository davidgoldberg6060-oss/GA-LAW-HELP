package help.galaw.standalone

/**
 * On-device transcript for an AI chat (Talk to Me, Case Chat). Messages live only in this
 * in-memory list; deleting one here removes it from the screen AND from the context that is
 * sent back to the AI on the next question, because history is always rebuilt from this list.
 */
class ChatTranscript {
    data class Message(val id: Long, val mine: Boolean, val text: String, val time: String, val shareText: String = text, val inContext: Boolean = true)

    private val items = mutableListOf<Message>()
    private var nextId = 1L

    val messages: List<Message> get() = items.toList()

    fun add(mine: Boolean, text: String, time: String, shareText: String = text, inContext: Boolean = true): Message =
        Message(nextId++, mine, text, time, shareText, inContext).also { items.add(it) }

    /** Hard-removes one message. Returns false when it was already gone. */
    fun delete(id: Long): Boolean = items.removeAll { it.id == id }

    fun clear() = items.clear()

    fun hasAnswer(): Boolean = items.any { !it.mine }

    /** Case Chat history in the backend's {role, content} shape, most recent [max] turns. */
    fun roleHistory(max: Int = 20): List<Pair<String, String>> =
        items.filter { it.inContext && it.text.isNotBlank() }.takeLast(max).map { (if (it.mine) "user" else "assistant") to it.text }

    /** Talk to Me plain-text transcript, rebuilt from the remaining messages only. */
    fun transcript(): String = buildString {
        for (m in items.filter { it.inContext }) {
            if (m.mine) append("User: ").append(m.text.trim()).append('\n')
            else append("GA.LAW.HELP: ").append(m.text.trim()).append("\n\n")
        }
    }
}
