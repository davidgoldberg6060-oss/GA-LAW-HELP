package help.galaw.standalone

import kotlin.test.Test
import kotlin.test.assertTrue

class ShareTextTest {
    private val cite = GaScreens.LoopholeCite("O.C.G.A. § 9-3-33", "Injuries to the person", "https://example.test/9-3-33")
    private val take = GaScreens.LawyerTake("If I Was Your Lawyer, I Would Say", "Keep your records.", "Not legal advice — this app is not your lawyer.", listOf(cite))

    @Test fun answerIncludesCitationsLawyerTakeAndNote() {
        val t = ShareText.answer("How long?", "Two years.", take)
        assertTrue(t.startsWith("Q: How long?"))
        assertTrue("IF I WAS YOUR LAWYER, I WOULD SAY" in t)
        assertTrue("O.C.G.A. § 9-3-33 — Injuries to the person" in t && "https://example.test/9-3-33" in t)
        assertTrue("this app is not your lawyer" in t && t.endsWith(ShareText.NOTE))
    }

    @Test fun loopholesListsEveryFinding() {
        val f = GaScreens.LoopholeFinding("Gap", "Title", "Explanation", listOf(cite))
        val t = ShareText.loopholes("DUI", listOf(f, f.copy(title = "Second")), null)
        assertTrue("1. [Gap] Title" in t && "2. [Gap] Second" in t && t.endsWith(ShareText.NOTE))
    }
}
