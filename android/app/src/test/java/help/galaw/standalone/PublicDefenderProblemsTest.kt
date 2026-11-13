package help.galaw.standalone

import java.io.File
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFalse
import kotlin.test.assertTrue

class PublicDefenderProblemsTest {
    private fun json(): String {
        var dir = File(".").canonicalFile
        repeat(8) {
            listOf(
                File(dir, "android/app/src/main/assets/public_defender_problems.json"),
                File(dir, "src/main/assets/public_defender_problems.json"),
                File(dir, "config/public_defender_problems.json"),
            ).firstOrNull { it.exists() }?.let { return it.readText() }
            dir = dir.parentFile ?: return@repeat
        }
        error("public_defender_problems.json not found")
    }

    @Test fun detectsDistrustButNotAPlainRequestForCounsel() {
        assertTrue(PublicDefenderProblems.detects("my public defender is working with the state"))
        assertFalse(PublicDefenderProblems.detects("how do I get a public defender"))
    }

    @Test fun guideKeepsVerifiedHabeasDeadlinesAndActName() {
        val pack = PublicDefenderProblems.packFor(json(), "en")
        val text = PublicDefenderProblems.asText(pack)
        assertTrue("O.C.G.A. § 9-14-42" in text)
        assertTrue("4 years" in text)
        assertTrue("1 year" in text)
        assertTrue("180 days" in text)
        assertFalse("Georgia Public Defender Act" in text)
        assertEquals("discharge_appointed_counsel", pack.motionKey)
        assertTrue(pack.templates.any { it.motionKey == "discharge_appointed_counsel" })
        val es = PublicDefenderProblems.packFor(json(), "es")
        assertTrue(PublicDefenderProblems.asText(es).contains("no asesoramiento jurídico"))
    }
}
