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
    fun signInScreenOpensGuestRightsWithoutAccount() {
        val auth = source("app/src/main/java/help/galaw/standalone/AuthActivity.kt")
        assertTrue(auth.contains("GuestRightsActivity"))
        assertTrue(auth.contains("Know your rights without signing in"))
        val guestScreen = source("app/src/main/java/help/galaw/standalone/GuestRightsActivity.kt")
        assertTrue(guestScreen.contains("GuestPublicApi.rightsAssistant"))
        assertTrue(guestScreen.contains("GuestPublicApi.encounter"))
    }

    @Test
    fun privateCaseAnalysisStaysOnAuthenticatedClient() {
        val mode = source("app/src/main/java/help/galaw/standalone/GroundedLegalMode.kt")
        assertTrue(mode.contains("api.caseAnalysisWithVerifiedAuthorities"))
        assertTrue(mode.contains("api.motionsAnalysis"))
    }

    @Test
    fun homeRightsSearchUsesPublicGuestEndpoints() {
        val screen = source("app/src/main/java/help/galaw/standalone/InternalLegalSearchActivity.kt")
        assertTrue(screen.contains("GuestPublicApi.rightsAssistant"))
        assertTrue(screen.contains("GuestPublicApi.encounter"))
        assertTrue(screen.contains("api.groundedLegalAssistant"))
        assertTrue(screen.contains("login_required"))
    }
}

    @Test
    fun homeEncounterCardsUseGuestRightsWithoutMembership() {
        val home = source("app/src/main/java/help/galaw/standalone/MainActivity.kt")
        assertTrue(home.contains("openGuestRights(\"Know my rights during a Georgia police encounter\")"))
        assertTrue(home.contains("GuestRightsActivity.EXTRA_SITUATION"))
        assertTrue(!home.contains("requirePaid{showGuide(\"KNOW MY RIGHTS\""))
        val cases = home.substringAfter("YOUR LEGAL WORK")
        assertTrue(cases.contains("requirePaid{showDocuments()}"))
        assertTrue(cases.contains("requirePaid{showLegalWorkHub()}"))
    }
