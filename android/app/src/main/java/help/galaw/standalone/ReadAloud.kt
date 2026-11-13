package help.galaw.standalone

import android.content.Context
import android.speech.tts.TextToSpeech
import android.speech.tts.UtteranceProgressListener
import java.util.Locale

/**
 * Free on-device read-aloud. Two original voices (not based on any real person or character):
 * The Butler (en-GB, slightly slower and lower) and The Nanny (en-US, slightly livelier).
 * Legal wording is never rewritten. The not-legal-advice notice is always spoken.
 */
object ReadAloud {
    const val PREF_KEY = "read_aloud_voice"
    const val OFF = "off"
    const val BUTLER = "butler"
    const val NANNY = "nanny"
    const val NOTICE_EN = "This is legal information, not legal advice."
    const val NOTICE_ES = "Esto es información legal, no asesoramiento jurídico."

    data class Voice(
        val id: String, val label: String, val description: String,
        val locale: Locale, val localeEs: Locale, val pitch: Float, val rate: Float,
        val introEn: String, val introEs: String
    )

    val BUTLER_VOICE = Voice(
        BUTLER, "The Butler",
        "A refined, warm, older British voice. An original voice, not based on any person or character.",
        Locale.UK, Locale("es", "ES"), 0.85f, 0.88f,
        "Allow me to read this for you.", "Permítame leérselo."
    )
    val NANNY_VOICE = Voice(
        NANNY, "The Nanny",
        "A chatty, warm New York voice. An original voice, not based on any person or character.",
        Locale.US, Locale("es", "US"), 1.12f, 1.06f,
        "All right, dear, here is what this says.", "Está bien, querida, esto es lo que dice."
    )

    fun normalize(value: String?): String = when (value?.lowercase()?.trim()) {
        BUTLER, "the butler" -> BUTLER
        NANNY, "the nanny" -> NANNY
        else -> OFF
    }

    fun voice(value: String?): Voice? = when (normalize(value)) {
        BUTLER -> BUTLER_VOICE
        NANNY -> NANNY_VOICE
        else -> null
    }

    fun saved(ctx: Context): String =
        normalize(ctx.getSharedPreferences("ga_settings", Context.MODE_PRIVATE).getString(PREF_KEY, OFF))

    fun save(ctx: Context, id: String) {
        ctx.getSharedPreferences("ga_settings", Context.MODE_PRIVATE).edit().putString(PREF_KEY, normalize(id)).apply()
        if (normalize(id) == OFF) stop()
    }

    fun spokenText(body: String, voiceId: String?, language: String = "en"): String {
        val text = body.trim()
        if (text.isEmpty()) return ""
        val spanish = language.lowercase().startsWith("es")
        val notice = if (spanish) NOTICE_ES else NOTICE_EN
        val info = voice(voiceId)
        var spoken = text
        if (info != null) {
            val intro = if (spanish) info.introEs else info.introEn
            if (!spoken.startsWith(intro)) spoken = intro + "\n\n" + spoken
        }
        if (!spoken.contains(notice)) spoken = spoken.trim() + "\n\n" + notice
        return spoken.trim()
    }

    @Volatile private var tts: TextToSpeech? = null
    @Volatile private var ready = false
    @Volatile private var pending: Triple<Context, String, String>? = null

    fun speak(ctx: Context, body: String, language: String = "en") {
        val id = saved(ctx)
        if (id == OFF) return
        val text = spokenText(body, id, language)
        if (text.isEmpty()) return
        val app = ctx.applicationContext
        val existing = tts
        if (existing != null && ready) {
            utter(existing, text, id, language)
            return
        }
        pending = Triple(app, text, language + "|" + id)
        if (existing != null) return
        tts = TextToSpeech(app) { status ->
            ready = status == TextToSpeech.SUCCESS
            val queued = pending
            pending = null
            if (ready && queued != null) {
                val parts = queued.third.split("|")
                utter(tts ?: return@TextToSpeech, queued.second, parts.getOrElse(1) { id }, parts[0])
            }
        }
        tts?.setOnUtteranceProgressListener(object : UtteranceProgressListener() {
            override fun onStart(utteranceId: String?) {}
            override fun onDone(utteranceId: String?) {}
            override fun onError(utteranceId: String?) {}
        })
    }

    fun stop() {
        pending = null
        tts?.stop()
    }

    fun shutdown() {
        stop()
        tts?.shutdown()
        tts = null
        ready = false
    }

    private fun utter(engine: TextToSpeech, text: String, voiceId: String, language: String) {
        val info = voice(voiceId) ?: return
        val spanish = language.lowercase().startsWith("es")
        val locale = if (spanish) info.localeEs else info.locale
        engine.language = locale
        engine.setPitch(info.pitch)
        engine.setSpeechRate(info.rate)
        engine.speak(text, TextToSpeech.QUEUE_FLUSH, null, "ga-read-aloud")
    }
}
