package help.galaw.standalone

import java.io.File
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertTrue

class CourtroomPrepTest {
    private fun json(): String {
        val candidates = listOf(
            File("src/main/assets/courtroom_prep.json"),
            File("android/app/src/main/assets/courtroom_prep.json"),
            File("../app/src/main/assets/courtroom_prep.json"),
            File("../../../../../../../config/courtroom_prep.json"),
        )
        // Walk up from the JVM cwd looking for the file.
        var dir = File(".").canonicalFile
        repeat(8) {
            listOf(
                File(dir, "android/app/src/main/assets/courtroom_prep.json"),
                File(dir, "config/courtroom_prep.json"),
                File(dir, "src/main/assets/courtroom_prep.json"),
            ).firstOrNull { it.exists() }?.let { return it.readText() }
            dir = dir.parentFile ?: return@repeat
        }
        return candidates.first { it.exists() }.readText()
    }

    @Test fun generalChecklistIncludesDayBeforeDayOfAndHonorific() {
        val pack = CourtroomPrep.prepFor(json(), null, "en")
        assertEquals("day_before", pack.sections[0].id)
        assertEquals("day_of", pack.sections[1].id)
        val text = CourtroomPrep.asText(pack)
        assertTrue("Your Honor" in text)
        assertTrue("30 to 45 minutes" in text)
        assertTrue("not legal advice" in text)
    }

    @Test fun duiChecklistIsTailored() {
        val pack = CourtroomPrep.prepFor(json(), "dui", "en")
        assertEquals("dui", pack.caseType)
        assertEquals("DUI", pack.label)
        val text = CourtroomPrep.asText(pack).lowercase()
        assertTrue("implied-consent" in text || "als" in text || "license" in text)
    }

    @Test fun spanishChecklistKeepsCitationsAndDisclaimer() {
        val pack = CourtroomPrep.prepFor(json(), "eviction", "es")
        assertEquals("es", pack.language)
        assertTrue(pack.notice.contains("no asesoramiento jurídico"))
        assertTrue(pack.sections.any { it.title.contains("El día antes") })
        assertTrue(CourtroomPrep.asText(pack).contains("Your Honor") || pack.quick.contains("Your Honor") || pack.sections.any { it.items.any { line -> "Your Honor" in line } })
    }
}
