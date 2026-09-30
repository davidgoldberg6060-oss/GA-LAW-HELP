package help.galaw.standalone

import java.io.File
import kotlin.test.Test
import kotlin.test.assertFalse
import kotlin.test.assertTrue

class CaseAnalysisScreenContractTest {
    private fun source(path: String): String {
        val candidates = listOf(File(path), File("../$path"), File("../../$path"))
        return candidates.firstOrNull { it.exists() }?.readText()
            ?: error("Unable to locate $path")
    }

    @Test
    fun caseAnalysisUsesGroundedCaseAnalysisModeOnly() {
        val text = source("app/src/main/java/help/galaw/standalone/CaseAnalysisScreenModel.kt")
        assertTrue(text.contains("GroundedLegalMode.Mode.CASE_ANALYSIS"))
        assertTrue(text.contains("GroundedLegalMode.analyze"))
        assertFalse(text.contains("publicAsk("))
        assertFalse(text.contains("searchAuthorities("))
        assertFalse(text.contains("internalLegalSearch("))
    }

    @Test
    fun caseAnalysisPreservesAuthorityRendererOutput() {
        val text = source("app/src/main/java/help/galaw/standalone/CaseAnalysisScreenModel.kt")
        assertTrue(text.contains("result.authoritySummary"))
        assertTrue(text.contains("result.displayText"))
    }

    @Test
    fun unifiedRouterExposesGroundedCaseAnalysis() {
        val text = source("app/src/main/java/help/galaw/standalone/NativeLegalScreenRouter.kt")
        assertTrue(text.contains("fun caseAnalysis("))
        assertTrue(text.contains("CaseAnalysisScreenModel.analyze"))
    }
}
