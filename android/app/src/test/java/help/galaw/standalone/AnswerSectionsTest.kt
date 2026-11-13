package help.galaw.standalone

import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertTrue

class AnswerSectionsTest {
    private val answer = """Short answer
You can ask the court to throw out evidence if police searched your car without a warrant. Under O.C.G.A. § 17-5-30, you may file a motion to suppress evidence.

How it works in Georgia
Ways to fight the evidence:
• File a motion to suppress under O.C.G.A. § 17-5-30.
• Challenge whether police had a legal right to search your car.
Ways to lessen the outcome:
• Use First Offender probation (O.C.G.A. § 42-8-60) if you have no prior felony.

Motions that could help
• Motion to suppress evidence (O.C.G.A. § 17-5-30, O.C.G.A. § 17-5-21): Asks the judge to throw out evidence. How it can help: Without the key evidence, charges are often dropped. Timing: Usually within ten days after arraignment.
• Discovery: get the prosecution's evidence (O.C.G.A. § 17-16-4): Opts into discovery. How it can help: Shows weaknesses early.
• A lawyer should decide whether and when to file any motion; deadlines can be short.

Questions to ask your lawyer
• Was the search of my car legal?
• Should we file a motion to suppress?

Where to get help
• State Bar of Georgia — Find a Lawyer directory — Private lawyers (usually paid). Search by practice area.

Note: Georgia Code text is from the 2022 edition.

Laws cited
• O.C.G.A. § 17-5-30 — Motion to suppress evidence illegally seized"""

    @Test fun quickAnswerThenTitledSectionsWithCounts() {
        val a = AnswerSections.structure(answer)
        assertTrue(a.quick.startsWith("You can ask the court") && AnswerSections.sentences(a.quick).size <= 3)
        assertEquals(listOf("Ways to fight the evidence", "Ways to lessen the outcome", "Motions that could help", "Questions to ask your lawyer", "Laws cited", "Where to get help"), a.sections.map { it.title })
        assertEquals("Georgia Code text is from the 2022 edition.", a.note)
    }

    @Test fun motionsAreShortWithTimingAndFootnotes() {
        val m = AnswerSections.structure(answer).sections.first { it.kind == "motions" }
        assertEquals(AnswerSections.Item("Motion to suppress evidence", "Without the key evidence, charges are often dropped.", "When to file: Usually within ten days after arraignment."), m.items[0])
        assertEquals("Discovery: get the prosecution's evidence", m.items[1].head)
        assertEquals(2, m.items.size)
        assertTrue(m.notes.single().startsWith("A lawyer should decide"))
        assertEquals("Motion to suppress evidence · Discovery: get the prosecution's evidence", AnswerSections.teaser(m))
    }

    @Test fun citationsAreCollectedOnceInLawsCited() {
        val a = AnswerSections.structure(answer)
        val laws = a.sections.first { it.kind == "laws" }
        assertEquals(listOf("O.C.G.A. § 17-5-30", "O.C.G.A. § 42-8-60", "O.C.G.A. § 17-5-21", "O.C.G.A. § 17-16-4"), laws.items.map { it.head })
        assertEquals("Motion to suppress evidence illegally seized", laws.items[0].detail)
        assertEquals("Use First Offender probation if you have no prior felony.", a.sections.first { it.title == "Ways to lessen the outcome" }.items[0].head)
        assertEquals("State Bar of Georgia — Find a Lawyer directory", a.sections.first { it.kind == "help" }.items[0].head)
    }

    @Test fun plainTextWithoutHeadingsIsJustAQuickAnswer() {
        val a = AnswerSections.structure("You can ask for a bond hearing. A judge decides.")
        assertEquals("You can ask for a bond hearing. A judge decides.", a.quick)
        assertTrue(a.sections.isEmpty())
    }
}
