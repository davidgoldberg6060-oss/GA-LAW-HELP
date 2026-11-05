package help.galaw.standalone

import java.io.File
import kotlin.test.Test
import kotlin.test.assertTrue
import kotlin.test.assertFalse

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
    fun guestRightsActivityUsesPublicEndpoints() {
        val guestScreen = source("app/src/main/java/help/galaw/standalone/GuestRightsActivity.kt")
        assertTrue(guestScreen.contains("GuestPublicApi.rightsAssistant"))
        assertTrue(guestScreen.contains("GuestPublicApi.encounter"))
        val main = source("app/src/main/java/help/galaw/standalone/MainActivity.kt")
        assertTrue(main.contains("GuestRightsActivity"))
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

    @Test
    fun homeEncounterCardsUseGuestRightsWithoutMembership() {
        val home = source("app/src/main/java/help/galaw/standalone/MainActivity.kt")
        assertTrue(home.contains("openGuestRights(\"Know my rights during a Georgia police encounter\")"))
        assertTrue(home.contains("GuestRightsActivity.EXTRA_SITUATION"))
        assertFalse(home.contains("requirePaid{showGuide(\"KNOW MY RIGHTS\""))
        assertTrue(home.contains("if(q.isNotEmpty())openGuestRights(q)"))
        assertFalse(home.contains("requirePaid{busy(\"Asking GA.LAW.HELP"))
        assertTrue(home.contains("showHome()"))
        assertFalse(home.contains("if(api.token==null) showAuth() else showHome()"))
        assertTrue(home.contains("navItem(\"💬\",\"AI Help\"){showTalkToMe()}"))
        assertFalse(home.contains("requirePaid{showTalkToMe()}"))
        assertFalse(home.contains("requirePaid{showLawSearch()}"))
        assertTrue(home.contains("navItem(\"⚖\",\"Laws\"){openGuestRights(\"Georgia laws and rights\")}"))
        assertTrue(home.contains("openGuestRights(\"Georgia laws and rights\")"))
        val cases = home.substringAfter("YOUR LEGAL WORK")
        assertTrue(cases.contains("requirePaid{showDocuments()}"))
        assertTrue(cases.contains("requirePaid{showLegalWorkHub()}"))
    }

    @Test
    fun homeActivityGeorgiaLawsUsesPublicAskWithoutLoginGate() {
        val home = source("app/src/main/java/help/galaw/standalone/HomeActivity.kt")
        assertFalse(home.contains("if (api.token == null) { startActivity(Intent(this, AuthActivity::class.java)); finish(); return }"))
        assertTrue(home.contains("api = ApiClient(this)"))
        assertTrue(home.contains("showHome()"))
        assertTrue(home.contains("GuestPublicApi.lawSearch"))
        assertTrue(home.contains("TalkToMeController.reply"))
        assertTrue(home.contains("showGeorgiaLaws()"))
        assertFalse(home.contains("showTalkToMe()}){val result=api.publicAsk(q)"))
        assertFalse(home.contains("api.searchAuthorities(q)"))
        assertTrue(home.contains("private fun showCases(){if(!requireSignedIn())return;"))
        assertTrue(home.contains("private fun showDocuments(){if(!requireSignedIn())return;"))
        val laws = source("app/src/main/java/help/galaw/standalone/GeorgiaLawsActivity.kt")
        assertTrue(laws.contains("GuestPublicApi.rightsAssistant"))
        assertTrue(laws.contains("GuestPublicApi.encounter"))
        val api = source("app/src/main/java/help/galaw/standalone/ApiClient.kt")
        assertTrue(api.contains("GuestPublicApi.rightsAssistant"))
        assertTrue(api.contains("GuestPublicApi.encounter"))
        assertTrue(api.contains("fun publicAsk"))
    }
}
