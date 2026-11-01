package help.galaw.standalone

import android.content.Context

/**
 * Keeps AI chats on this phone between app launches (app-private storage only; never uploaded).
 * An empty transcript removes its saved copy, so Delete / Clear chat also wipe what is stored.
 */
object ChatStore {
    private const val PREFS = "ga_chats"
    const val TALK_KEY = "talk"
    fun caseKey(caseId: Int) = "case:$caseId"

    fun load(context: Context, key: String, into: ChatTranscript) {
        into.load(context.getSharedPreferences(PREFS, Context.MODE_PRIVATE).getString(key, null))
    }

    fun save(context: Context, key: String, transcript: ChatTranscript) {
        val prefs = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE).edit()
        if (transcript.messages.isEmpty()) prefs.remove(key) else prefs.putString(key, transcript.toJson())
        prefs.apply()
    }

    /** Wipes every saved chat (used when the user deletes their data). */
    fun wipeAll(context: Context) { context.getSharedPreferences(PREFS, Context.MODE_PRIVATE).edit().clear().apply() }

    /** Opens a transcript that saves itself on every change. */
    fun open(context: Context, key: String): ChatTranscript {
        val app = context.applicationContext
        val t = ChatTranscript()
        load(app, key, t)
        t.onChange = { save(app, key, it) }
        return t
    }
}
