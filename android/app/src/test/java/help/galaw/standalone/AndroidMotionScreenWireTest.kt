package help.galaw.standalone

import java.io.File
import kotlin.test.Test
import kotlin.test.assertTrue

class AndroidMotionScreenWireTest {
    private fun source(path: String): String {
        val candidates = listOf(File(path), File("../$path"), File("../../$path"))
        return candidates.firstOrNull { it.exists() }?.readText()
            ?: error("Unable to locate $path")
    }

    @Test
    fun privateCaseMotionScreenUsesAuthenticatedEndpoint() {
        val api = source("app/src/main/java/help/galaw/standalone/ApiClient.kt")
        assertTrue(api.contains("/cases/$id/motion-screen"))
        assertTrue(api.contains("fun motionScreen("))
        val home = source("app/src/main/java/help/galaw/standalone/HomeActivity.kt")
        assertTrue(home.contains("api.motionScreen"))
        assertTrue(home.contains("Verified Motion Screen"))
        assertTrue(home.contains("Do not treat unverified citations as current Georgia law"))
    }
}
