package help.galaw.standalone

import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFalse
import kotlin.test.assertTrue

class ReadAloudTest {
    @Test fun spokenTextKeepsLegalWordingAndAddsNotice() {
        val body = "Challenge the stop. See O.C.G.A. § 40-6-391."
        val butler = ReadAloud.spokenText(body, "butler", "en")
        assertTrue(butler.startsWith(ReadAloud.BUTLER_VOICE.introEn))
        assertTrue("Challenge the stop" in butler)
        assertTrue("O.C.G.A. § 40-6-391" in butler)
        assertTrue(butler.endsWith(ReadAloud.NOTICE_EN))
        val nanny = ReadAloud.spokenText(body, "nanny", "en")
        assertTrue(nanny.startsWith(ReadAloud.NANNY_VOICE.introEn))
        assertTrue(ReadAloud.BUTLER_VOICE.rate < ReadAloud.NANNY_VOICE.rate)
        assertEquals("en-GB", ReadAloud.BUTLER_VOICE.locale.toLanguageTag().let { if (it.startsWith("en-GB") || it == "en-GB") "en-GB" else it })
    }

    @Test fun catalogDoesNotUseTrademarksOrActorNames() {
        val blob = listOf(ReadAloud.BUTLER_VOICE, ReadAloud.NANNY_VOICE).joinToString(" ") { it.label + " " + it.description + " " + it.introEn }.lowercase()
        for (banned in listOf("alfred", "batman", "drescher", "fran ")) {
            assertFalse(banned in blob)
        }
        assertEquals("The Butler", ReadAloud.BUTLER_VOICE.label)
        assertEquals("The Nanny", ReadAloud.NANNY_VOICE.label)
        assertTrue("original" in ReadAloud.BUTLER_VOICE.description.lowercase())
    }

    @Test fun spanishReadingUsesSpanishIntroAndNotice() {
        val spoken = ReadAloud.spokenText("Impugne la parada.", "nanny", "es")
        assertTrue(spoken.startsWith(ReadAloud.NANNY_VOICE.introEs))
        assertTrue(ReadAloud.NOTICE_ES in spoken)
        assertEquals("", ReadAloud.spokenText("", "butler"))
        assertEquals(ReadAloud.BUTLER, ReadAloud.normalize("The Butler"))
        assertEquals(ReadAloud.OFF, ReadAloud.normalize("off"))
    }
}
