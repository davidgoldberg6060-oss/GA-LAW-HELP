package help.galaw.standalone

import java.io.File
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFalse
import kotlin.test.assertTrue

class GeorgiaLawTitlesTest {
    @Test
    fun catalogUsesOfficialIndexesNotLexis() {
        assertEquals(listOf(16, 17, 19, 40, 42, 44), GeorgiaLawTitles.titles.map { it.number })
        assertTrue(GeorgiaLawTitles.CODE_REVISION_URL.startsWith("https://www.legis.ga.gov/"))
        assertTrue(GeorgiaLawTitles.UNANNOTATED_RELEASE_URL.contains("gov.ga.ocga"))
        assertFalse(GeorgiaLawTitles.NOTICE.contains("lexis.com", ignoreCase = true))
        assertTrue(GeorgiaLawTitles.NOTICE.contains("not Lexis"))
    }

    @Test
    fun georgiaLawsScreenStaysOnGuestRightsPath() {
        val activity = source("app/src/main/java/help/galaw/standalone/GeorgiaLawsActivity.kt")
        assertTrue(activity.contains("GuestPublicApi.rightsAssistant"))
        assertTrue(activity.contains("/public/rights-assistant"))
        assertFalse(activity.contains("/cases/"))
        val home = source("app/src/main/java/help/galaw/standalone/HomeActivity.kt")
        assertTrue(home.contains("GeorgiaLawsActivity"))
        assertFalse(home.contains("showGeorgiaLaws(){if(!requireSignedIn())"))
        val approved = source("app/src/main/java/help/galaw/standalone/ApprovedHomeScreen.kt")
        assertTrue(approved.contains("actions::openGeorgiaLaws"))
    }

    private fun source(path: String): String {
        val candidates = listOf(File(path), File("../$path"), File("../../$path"))
        return candidates.firstOrNull { it.exists() }?.readText() ?: error("Unable to locate $path")
    }
}
