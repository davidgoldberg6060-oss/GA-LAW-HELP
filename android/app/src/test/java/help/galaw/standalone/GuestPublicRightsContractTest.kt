package help.galaw.standalone

import java.io.File
import kotlin.test.Test
import kotlin.test.assertTrue

class GuestPublicRightsContractTest {
    private fun source(path: String): String {
        val candidates = listOf(File(path), File("../$path"), File("../../$path"))
        return candidates.firstOrNull { it.exists() }?.readText()
            ?: error("Unable to locate $path")
    }

    @Test
    fun rightsAndTalkToMeUsePublicGuestEndpoints() {
        val mode = source("app/src/main/java/help/galaw/standalone/GroundedLegalMode.kt")
        assertTrue(mode.contains("GuestPublicApi.rightsAssistant"))
        val guest = source("app/src/main/java/help/galaw/standalone/GuestPublicApi.kt")
        assertTrue(guest.contains("/public/encounter"))
        assertTrue(guest.contains("/public/rights-assistant"))
    }

    @Test
    fun privateCaseAnalysisStaysOnAuthenticatedClient() {
        val mode = source("app/src/main/java/help/galaw/standalone/GroundedLegalMode.kt")
        assertTrue(mode.contains("api.caseAnalysisWithVerifiedAuthorities"))
        assertTrue(mode.contains("api.motionsAnalysis"))
    }
}
