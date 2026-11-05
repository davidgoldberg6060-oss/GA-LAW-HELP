package help.galaw.standalone

import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertTrue

class CitizenHelpTest {
    @Test
    fun allTwelveFeaturesPresentWithDisclaimerAndHttpsLinks() {
        assertEquals(12, CitizenHelp.FEATURES.size)
        assertTrue(CitizenHelp.DISCLAIMER.contains("not legal advice", ignoreCase = true))
        val ids = CitizenHelp.FEATURES.map { it.id }.toSet()
        assertTrue(ids.containsAll(listOf(
            "filing_coach", "record_restriction", "fines_fees", "court_dates",
            "public_defender", "inmate_lookup", "parole_rights", "dds_reinstatement",
            "eviction_answer", "voting", "traffic_stop", "reentry"
        )))
        CitizenHelp.FEATURES.forEach { f ->
            assertTrue(f.sections.isNotEmpty(), f.id)
            f.sections.forEach { sec ->
                sec.links.forEach { link ->
                    assertTrue(
                        link.url.startsWith("https://") || link.url.startsWith("app:") || link.url.startsWith("tel:"),
                        "${f.id} bad url ${link.url}"
                    )
                }
            }
        }
        // Filing coach must point at official e-file / clerk sources
        val filing = CitizenHelp.feature("filing_coach")!!
        val urls = filing.sections.flatMap { it.links.map { l -> l.url } }
        assertTrue(urls.any { it.contains("peachcourt") })
        assertTrue(urls.any { it.contains("odysseyefilega") || it.contains("efilega") })
        assertTrue(urls.any { it.contains("gaclerks.org") })
        assertTrue(urls.any { it.contains("9-15-2") || it.contains("affidavit-of-indigence") })
    }
}
