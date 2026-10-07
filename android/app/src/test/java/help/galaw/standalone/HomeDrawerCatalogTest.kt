package help.galaw.standalone

import java.io.File
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFalse
import kotlin.test.assertTrue

class HomeDrawerCatalogTest {
    @Test
    fun drawerMatchesApprovedHomeItems() {
        assertEquals(
            listOf(
                "Home", "My Cases", "AI Help", "Legal Tools", "Georgia Laws", "Court Info",
                "Legal Forms", "Case Analysis", "Know Your Rights", "Resources", "Emergency Help",
                "Dark Mode", "Settings", "Log Out"
            ),
            HomeDrawerCatalog.items.map { it.label }
        )
        assertEquals(setOf("cases", "analysis"), HomeDrawerCatalog.items.filter { it.requiresSignIn }.map { it.id }.toSet())
        assertFalse(HomeDrawerCatalog.items.first { it.id == "rights" }.requiresSignIn)
    }

    @Test
    fun homeMenuKeepsGuestRightsAndPrivateCasesSplit() {
        val home = source("app/src/main/java/help/galaw/standalone/HomeActivity.kt")
        assertTrue(home.contains("HomeDrawerCatalog.items"))
        assertTrue(home.contains("Guest rights stay on /public/rights-assistant"))
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
