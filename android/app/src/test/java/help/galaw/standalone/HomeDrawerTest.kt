package help.galaw.standalone

import java.io.File
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFalse
import kotlin.test.assertTrue

class HomeDrawerTest {
    @Test
    fun drawerMatchesApprovedHomePlusSettings() {
        assertEquals(
            listOf(
                "Home",
                "My Cases",
                "AI Help",
                "Legal Tools",
                "Georgia Laws",
                "Court Info",
                "Legal Forms",
                "Case Analysis",
                "Know Your Rights",
                "Resources",
                "Emergency Help",
                "Dark Mode",
                "Settings",
                "Log Out"
            ),
            HomeDrawer.items
        )
        assertEquals(setOf("My Cases", "Case Analysis"), HomeDrawer.loginOnly)
        assertTrue(HomeDrawer.NOTICE.contains("/public/rights-assistant"))
        assertFalse(HomeDrawer.NOTICE.contains("resist police", ignoreCase = true))
    }

    @Test
    fun homeMenuUsesDrawerAndKeepsCasesLoginOnly() {
        val home = source("app/src/main/java/help/galaw/standalone/HomeActivity.kt")
        assertTrue(home.contains("HomeDrawer.items"))
        assertTrue(home.contains("if(requireSignedIn())showCases()"))
        assertTrue(home.contains("if(requireSignedIn())showCaseAnalysis()"))
        assertFalse(home.contains("showKnowYourRights(){if(!requireSignedIn())"))
        assertFalse(home.contains("showGeorgiaLaws(){if(!requireSignedIn())"))
        assertTrue(home.contains("api.logout()"))
    }

    private fun source(path: String): String {
        val candidates = listOf(File(path), File("../$path"), File("../../$path"))
        return candidates.firstOrNull { it.exists() }?.readText() ?: error("Unable to locate $path")
    }
}
