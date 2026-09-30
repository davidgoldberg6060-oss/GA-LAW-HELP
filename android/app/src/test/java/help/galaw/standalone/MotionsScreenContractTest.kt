package help.galaw.standalone

import java.io.File
import kotlin.test.Test
import kotlin.test.assertFalse
import kotlin.test.assertTrue

class MotionsScreenContractTest {
    private fun source(path: String): String {
        val candidates = listOf(File(path), File("../$path"), File("../../$path"))
        return candidates.firstOrNull { it.exists() }?.readText()
            ?: error("Unable to locate $path")
    }

    @Test
    fun motionsScreenModelUsesGroundedMotionsModeOnly() {
        val text = source("app/src/main/java/help/galaw/standalone/MotionsScreenModel.kt")
        assertTrue(text.contains("GroundedLegalMode.Mode.MOTIONS"))
        assertTrue(text.contains("GroundedLegalMode.analyze"))
        assertFalse(text.contains("publicAsk("))
        assertFalse(text.contains("searchAuthorities("))
        assertFalse(text.contains("internalLegalSearch("))
    }

    @Test
    fun motionsScreenPreservesAuthorityRendererOutput() {
        val text = source("app/src/main/java/help/galaw/standalone/MotionsScreenModel.kt")
        assertTrue(text.contains("result.authoritySummary"))
        assertTrue(text.contains("result.displayText"))
    }
}
