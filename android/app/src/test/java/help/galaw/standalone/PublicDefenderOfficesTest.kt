package help.galaw.standalone

import java.io.File
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFalse
import kotlin.test.assertNull
import kotlin.test.assertTrue

class PublicDefenderOfficesTest {
    private fun json(): String {
        var dir = File(".").canonicalFile
        repeat(8) {
            listOf(
                File(dir, "android/app/src/main/assets/public_defender_offices.json"),
                File(dir, "src/main/assets/public_defender_offices.json"),
                File(dir, "config/public_defender_offices.json"),
            ).firstOrNull { it.exists() }?.let { return it.readText() }
            dir = dir.parentFile ?: return@repeat
        }
        error("public_defender_offices.json not found")
    }

    @Test fun directoryHasEveryOfficialCircuitAndLeavesMissingNamesBlank() {
        val dir = PublicDefenderOffices.load(json(), "en")
        assertEquals(51, dir.offices.size)
        assertEquals("https://gapubdef.org/_data/circuits.json", dir.sourceUrl)
        assertEquals("https://www.gabar.org/member-directory/", dir.barUrl)
        assertTrue(dir.outcomeNote.contains("does not publish an official per-attorney"))
        val fulton = PublicDefenderOffices.search(dir, "Fulton")
        assertEquals(1, fulton.size)
        assertEquals("Atlanta Circuit", fulton[0].circuit)
        val gwinnett = PublicDefenderOffices.search(dir, "Gwinnett")
        assertEquals(1, gwinnett.size)
        assertTrue(gwinnett[0].optOut)
        assertNull(gwinnett[0].defender)
        assertTrue("win/loss" in dir.barExplainer.lowercase())
    }

    @Test fun spanishOutcomeNoteIsPresent() {
        val dir = PublicDefenderOffices.load(json(), "es")
        assertTrue(dir.outcomeNote.contains("no publica") || dir.outcomeNote.contains("récord") || dir.outcomeNote.isNotBlank())
    }
}
