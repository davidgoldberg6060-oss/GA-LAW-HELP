package help.galaw.standalone

import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertTrue

/** Automatic "Your Defense Plan" answers render like the web (src/answerSections.ts). */
class DefensePlanSectionsTest {
    private val plan = """Your Defense Plan: DUI

Quick answer
Your strongest angle is the blood test. Ask for the license hearing right away.

How they'd build the case against you
• Likely charge: DUI (O.C.G.A. § 40-6-391).
• Impairment: They'd point to the blood test. They'd still need a reliable lab result.
• Weak spots: who drew the blood is unknown.

How to fight back
• Impairment: The State cannot establish impairment because the sample's handling is unproven. Challenge: chain of custody. Motion: Motion to suppress evidence.

Key deadlines
• Check your paperwork for the license deadline.

Questions to ask your lawyer
• Can the blood test be challenged?"""

    @Test fun planBadgeAndSections() {
        val a = AnswerSections.structure(plan)
        assertEquals("Your Defense Plan · DUI", a.plan)
        assertTrue(a.quick.startsWith("Your strongest angle is the blood test."))
        assertEquals(listOf("How they'd build the case against you", "How to fight back", "Key deadlines", "Questions to ask your lawyer"), a.sections.take(4).map { it.title })
        assertEquals("case", a.sections[0].kind)
        assertEquals(AnswerSections.Item("Impairment", "They'd point to the blood test. They'd still need a reliable lab result."), a.sections[0].items[1])
        assertEquals("fight", a.sections[1].kind)
        assertEquals(AnswerSections.Item("Impairment", "The State cannot establish impairment because the sample's handling is unproven.",
            "Challenge: chain of custody · Motion: Motion to suppress evidence"), a.sections[1].items[0])
        assertEquals("deadlines", a.sections[2].kind)
    }

    @Test fun normalAnswerHasNoBadge() {
        assertEquals("", AnswerSections.structure("Short answer\nYes.\n\nHow it works in Georgia\n• A point.").plan)
    }
}
