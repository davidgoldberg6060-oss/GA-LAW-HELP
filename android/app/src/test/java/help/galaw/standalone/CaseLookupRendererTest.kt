package help.galaw.standalone

import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class CaseLookupRendererTest {
    @Test
    fun unverifiedDocumentIdentifierIsNeverPresentedAsVerifiedCitation() {
        val result = CaseLookupController.Result(
            query = "aggravated assault",
            hits = listOf(
                CaseLookupController.CaseHit(
                    title = "Official Georgia opinion",
                    citation = "S24A0001 [UNVERIFIED DOCUMENT ID]",
                    court = "Supreme Court of Georgia",
                    date = "2026-01-01",
                    status = "unverified",
                    sourceId = "ga-sc-S24A0001"
                )
            ),
            total = 1
        )

        val rendered = CaseLookupRenderer.render(result)

        assertTrue(rendered.contains("S24A0001 [UNVERIFIED DOCUMENT ID]"))
        assertTrue(rendered.contains("Research record only"))
        assertTrue(rendered.contains("not a verified legal citation or current authority"))
        assertFalse(rendered.contains("Verified authority"))
    }

    @Test
    fun emptyLookupDoesNotInventAResult() {
        val rendered = CaseLookupRenderer.render(
            CaseLookupController.Result("made-up case", emptyList(), 0)
        )

        assertTrue(rendered.contains("No matching Georgia corpus records were found"))
        assertFalse(rendered.contains("Citation / identifier:"))
    }

    @Test
    fun missingMetadataRemainsMissingInsteadOfBeingFabricated() {
        val result = CaseLookupController.Result(
            query = "search",
            hits = listOf(CaseLookupController.CaseHit("", "", "", "", "", "")),
            total = 1
        )

        val rendered = CaseLookupRenderer.render(result)

        assertTrue(rendered.contains("Untitled corpus record"))
        assertFalse(rendered.contains("Citation / identifier:"))
        assertFalse(rendered.contains("Court:"))
        assertFalse(rendered.contains("Date:"))
        assertFalse(rendered.contains("Status:"))
        assertFalse(rendered.contains("Corpus source ID:"))
    }
}
