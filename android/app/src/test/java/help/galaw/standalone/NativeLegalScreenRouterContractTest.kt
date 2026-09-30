package help.galaw.standalone

import java.io.File
import kotlin.test.Test
import kotlin.test.assertFalse
import kotlin.test.assertTrue

class NativeLegalScreenRouterContractTest {
    private fun source(path: String): String {
        val candidates = listOf(File(path), File("../$path"), File("../../$path"))
        return candidates.firstOrNull { it.exists() }?.readText()
            ?: error("Unable to locate $path")
    }

    @Test
    fun routerUsesDedicatedNativeScreenModelsOnly() {
        val text = source("app/src/main/java/help/galaw/standalone/NativeLegalScreenRouter.kt")
        assertTrue(text.contains("CaseLookupScreenModel.search"))
        assertTrue(text.contains("RightsScreenModel.analyze"))
        assertTrue(text.contains("MotionsScreenModel.analyze"))
        assertTrue(text.contains("TalkToMeScreenModel.analyze"))
        assertFalse(text.contains("publicAsk("))
        assertFalse(text.contains("searchAuthorities("))
        assertFalse(text.contains("internalLegalSearch("))
    }
}
