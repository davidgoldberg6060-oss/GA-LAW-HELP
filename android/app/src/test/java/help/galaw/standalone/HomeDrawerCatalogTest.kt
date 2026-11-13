package help.galaw.standalone

import java.io.File
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFalse
import kotlin.test.assertTrue

class HomeDrawerCatalogTest {
    @Test
    fun drawerIncludesCitizenHelpAndGuestRights() {
        assertEquals(
            listOf(
                "Home", "My Case (start here)", "Case Workspace", "Talk to Me (AI)", "Paper reader", "Georgia Laws",
                "Funny & Weird Laws", "Motions & Legal Work", "Legal Forms", "Court Information", "Courtroom prep",
                "Know Your Rights", "Citizen Help", "Resources", "Emergency Information",
                "Payments & Subscription", "Settings", "Send feedback", "Profile", "Help & Support"
            ),
            HomeDrawerCatalog.items.map { it.label }
        )
        assertTrue(HomeDrawerCatalog.items.none { it.requiresSignIn })
        assertFalse(HomeDrawerCatalog.items.first { it.id == "rights" }.requiresSignIn)
        assertEquals("citizen", HomeDrawerCatalog.items.first { it.label == "Citizen Help" }.id)
    }

    @Test
    fun homeMenuKeepsGuestRightsAndCitizenHelp() {
        val home = source("app/src/main/java/help/galaw/standalone/HomeActivity.kt")
        assertTrue(home.contains("HomeDrawerCatalog.items"))
        assertTrue(home.contains("Guest rights stay on /public/rights-assistant"))
        assertTrue(home.contains("showCitizenHelpHub"))
        assertTrue(home.contains("showFeedback"))
        assertTrue(home.contains("Criminal — public defender council"))
        assertTrue(home.contains("Civil — Georgia Courts self-help"))
        assertTrue(home.contains("Family — Georgia Legal Aid"))
        assertFalse(home.contains("resist police by"))
        assertFalse(home.contains("lexis.com"))
    }

    private fun source(path: String): String {
        val candidates = listOf(File(path), File("../$path"), File("../../$path"))
        return candidates.firstOrNull { it.exists() }?.readText() ?: error("Unable to locate $path")
    }
}
