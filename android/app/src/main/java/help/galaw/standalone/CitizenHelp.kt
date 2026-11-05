package help.galaw.standalone

import android.app.AlertDialog
import android.content.Context
import android.graphics.Color
import android.view.View
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.TextView

/**
 * Citizen Help: UPL-safe guides grounded in official Georgia sources.
 * Information and links only — the app never files or serves papers for anyone.
 */
object CitizenHelp {
    const val DISCLAIMER =
        "This is legal information, not legal advice. STANDALONE ASSISTANT is not a lawyer and does not create an attorney-client relationship. Confirm forms, fees, deadlines and filing steps with the court or a licensed Georgia attorney before you act."

    data class Link(val label: String, val url: String)
    data class Section(val title: String, val body: String, val links: List<Link> = emptyList())
    data class Feature(val id: String, val title: String, val blurb: String, val sections: List<Section>)

    val FEATURES: List<Feature> = listOf(
        Feature(
            "filing_coach",
            "Motion filing coach",
            "Prepare a PDF, then file it yourself by e-file, mail or in person",
            listOf(
                Section(
                    "What this coach does",
                    "STANDALONE ASSISTANT can help you prepare a motion draft and save it as a PDF. You file it yourself. The app never submits papers to a clerk for you.",
                    listOf(
                        Link("Open Motions & Legal Work", "app:motions"),
                        Link("Georgia Guide & File (forms)", "https://www.guideandfile.com/"),
                        Link("GeorgiaLegalAid.org forms & info", "https://www.georgialegalaid.org/")
                    )
                ),
                Section(
                    "Step 1 — Affidavit of Indigence (fee waiver)",
                    "If you cannot pay court deposit, fee or cost, Georgia law lets you swear an affidavit of indigence. Your rights are then the same as if you had paid (O.C.G.A. § 9-15-2). Use the Guide & File Affidavit of Indigency interview or your court's form. A judge may review the affidavit. Bring proof of income if the court asks.",
                    listOf(
                        Link("O.C.G.A. § 9-15-2 (Justia text)", "https://law.justia.com/codes/georgia/title-9/chapter-15/section-9-15-2/"),
                        Link("Supreme Court Affidavit of Indigence (PDF)", "https://www.gasupreme.us/court-information/affidavit-of-indigence/"),
                        Link("Guide & File — Affidavit of Indigency", "https://www.guideandfile.com/")
                    )
                ),
                Section(
                    "Step 2 — Pick how you will file",
                    "Self-represented people may e-file where the court allows it, but are not required to. Attorneys must e-file many civil Superior/State cases. Check your county:\n\n• PeachCourt — free account for non-attorneys; leave “Are you an attorney?” as No.\n• Odyssey eFileGA — Self-Represented Account; same login can work with Guide & File.\n• Mail or in person — use Find My Clerk for the Superior Court Clerk.\n\nMetro tip: Gwinnett, DeKalb, Fulton and Cobb Superior civil cases commonly use Odyssey eFileGA (confirm on the active-courts list). Always check the official chart for your court.",
                    listOf(
                        Link("Which courts e-file (Judicial Council chart)", "https://georgiacourts.gov/efile-court-records/"),
                        Link("PeachCourt — register (self-represented OK)", "https://www.peachcourt.com/Account/Registration"),
                        Link("PeachCourt — first-time e-filing help", "https://awesome.peachcourt.com/knowledgebase/this-is-my-first-time-efiling-what-do-i-do"),
                        Link("Odyssey eFileGA — info for filers without lawyers", "https://www.odysseyefilega.com/prose.htm"),
                        Link("Odyssey eFileGA — active courts", "https://www.odysseyefilega.com/active-courts.htm"),
                        Link("eFileGA landing (Self-Represented Account)", "https://efilega.tylertech.cloud/OfsEfsp/ui/landing"),
                        Link("Find My Clerk (all Superior Court clerks)", "https://www.gaclerks.org/Clerks/FindMyClerk.aspx"),
                        Link("Georgia Courts directory", "https://georgiacourts.gov/georgia-courts-directory/")
                    )
                ),
                Section(
                    "E-filing fees (PeachCourt published amounts)",
                    "Court filing fees are separate from e-filing fees. On PeachCourt for cases started on or after Jan 1, 2019: a \$30 per-party fee covers 10 filings, then \$5 each; criminal e-file is often \$7 per filing where charged; card convenience fee is 3.5% + \$0.30. Clerk office public computers often charge \$0 for the e-filing fee (usual court fees still apply). Confirm current amounts on PeachCourt before you pay.",
                    listOf(Link("PeachCourt — What does eFiling cost?", "https://awesome.peachcourt.com/knowledgebase/fees"))
                ),
                Section(
                    "If you are incarcerated",
                    "Trial-court e-file usually needs email and internet access that many jails and prisons do not provide. Practical path: prepare a paper packet and use the facility’s legal mail. Official inmate habeas corpus form (Judicial Council/AOC):\n\nAppellate courts: a document from a pro se prisoner can be timely if delivered to prison officials by the deadline (mailbox rule). Use the prison legal-mail system if one exists. This does not apply to motions for reconsideration. See Georgia Supreme Court Rule 13 and Court of Appeals Rule 4.",
                    listOf(
                        Link("Inmate Form — Writ of Habeas Corpus (PDF)", "https://jcaoc.georgiacourts.gov/wp-content/uploads/2024/03/Inmate-Form_Application-for-Writ-of-Habeas-Corpus-2023.pdf"),
                        Link("Supreme Court SCED (attorneys + pro se Filing ID)", "https://www.gasupreme.us/sced/"),
                        Link("Supreme Court — Non-attorney Filing ID request", "https://www.gasupreme.us/non-attorney-request-form/"),
                        Link("Court of Appeals eFAST login", "https://efast.gaappeals.gov/login.jsf")
                    )
                )
            )
        ),
        Feature(
            "record_restriction",
            "Record restriction (expungement) wizard",
            "See which official path may fit, then use GJP / GBI / court forms",
            listOf(
                Section(
                    "How restriction works in Georgia",
                    "Georgia uses “record restriction” (often called expungement). Rules are in O.C.G.A. § 35-3-37. Pathways differ for non-convictions, misdemeanors, First Offender, and some pardoned felonies. STANDALONE ASSISTANT does not decide eligibility — use the official tools below.",
                    listOf(
                        Link("Georgia Courts — Record restrictions overview", "https://georgiacourts.gov/a2j/self-help-resources/record-restrictions-expungement/"),
                        Link("GBI — Criminal history record restrictions", "https://gbi.georgia.gov/services/georgia-criminal-history-record-restrictions"),
                        Link("Georgia Justice Project — DIY record clearing", "https://www.gjp.org/diyrecordclearing/")
                    )
                ),
                Section(
                    "Suggested order",
                    "1) Run GJP’s Georgia Conviction Check (on their site).\n2) Pick the matching DIY packet: non-conviction, misdemeanor, First Offender, or pardon path.\n3) For arrests before July 1, 2013, follow the arresting-agency / GBI application steps on the GBI and A2J pages (fees are stated there).\n4) For later arrests, the prosecutor may approve restriction at sentencing — see the A2J page.\n5) Keep copies of everything you file.",
                    listOf(Link("GJP DIY Record Clearing Resources", "https://www.gjp.org/diyrecordclearing/"))
                )
            )
        ),
        Feature(
            "fines_fees",
            "Fines, fees & ability to pay",
            "What Georgia law says about hardship and probation money",
            listOf(
                Section(
                    "Ability to pay (misdemeanor / ordinance probation)",
                    "Under O.C.G.A. § 42-8-102, the court shall waive, modify or convert fines, statutory surcharges, probation supervision fees and other moneys assessed by the court or a probation provider when it finds significant financial hardship, inability to pay, or other extenuating factors. Being indigent (under 100% of federal poverty guidelines, unless other resources exist) is one of the situations that creates a presumption of significant financial hardship unless rebutted. The court may convert amounts to community service or educational advancement.",
                    listOf(Link("O.C.G.A. § 42-8-102 (Justia text)", "https://law.justia.com/codes/georgia/title-42/chapter-8/article-6/section-42-8-102/"))
                ),
                Section(
                    "If probation is revoked only for unpaid money",
                    "When the sole basis for revocation is failure to pay fines, surcharges or probation fees, the statute requires a hearing (absent a waiver), an inquiry into why you did not pay, and written findings before revocation. No prehearing arrest warrant solely for unpaid fees. Ask the court calendar clerk how to get a hearing date.",
                    listOf(
                        Link("Fee waiver / Affidavit of Indigence statute (§ 9-15-2)", "https://law.justia.com/codes/georgia/title-9/chapter-15/section-9-15-2/"),
                        Link("Find legal help (Georgia Legal Aid)", "https://www.georgialegalaid.org/")
                    )
                ),
                Section(
                    "Questions to bring to court or counsel",
                    "• What exact amounts does the court say I owe, and for what?\n• Have I asked for a hardship finding under § 42-8-102?\n• Can any amount convert to community service or education?\n• Is there an Affidavit of Indigence on file for court costs?\nDo not ignore a court date while money is unpaid — ask for the hearing.",
                    emptyList()
                )
            )
        ),
        Feature(
            "court_dates",
            "Court date reminders",
            "Local reminders on this phone only — nothing leaves the device",
            listOf(
                Section(
                    "How reminders work",
                    "Enter a title and a date (YYYY-MM-DD). STANDALONE ASSISTANT schedules on-device notifications for 7 days before, 1 day before and the morning of that date at 9:00 a.m. local time. Dates and titles stay on this phone. Missing court can lead to a warrant and, for traffic cases, a Failure to Appear license suspension — see DDS.",
                    listOf(
                        Link("DDS — Reinstate license (includes FTA)", "https://dds.georgia.gov/georgia-licenseid/violations-suspensions-revocations/reinstate-license"),
                        Link("Set a reminder now", "app:court_date_form")
                    )
                )
            )
        ),
        Feature(
            "public_defender",
            "Ask for a public defender",
            "How to request appointed counsel",
            listOf(
                Section(
                    "Right to appointed counsel",
                    "If you face jail or prison time and cannot afford a lawyer, ask the court for a public defender or appointed counsel as early as you can — ideally at first appearance or arraignment. Bring proof of income if the court uses an application. Contact your circuit’s public defender office through the Georgia Public Defender Council site.",
                    listOf(
                        Link("Georgia Public Defender Council", "https://gapubdef.org/"),
                        Link("State Bar — find a lawyer (if you can hire one)", "https://www.gabar.org/public/find-a-lawyer")
                    )
                ),
                Section(
                    "If your appointed lawyer is not helping",
                    "You can ask the judge for a different appointed lawyer and explain the problem on the record. Keep notes of dates the lawyer did not visit, evidence ignored, or plea pressure without explanation. Complaints about licensed lawyers can go to the State Bar of Georgia. This app cannot fire or replace your lawyer.",
                    listOf(Link("State Bar of Georgia", "https://www.gabar.org/"))
                )
            )
        ),
        Feature(
            "inmate_lookup",
            "Find someone in jail or prison",
            "Official GDC search plus metro county jail lookups",
            listOf(
                Section(
                    "Georgia Department of Corrections",
                    "Use GDC’s Find an Offender tool for people in state custody. Verify anything important in writing with Inmate Records if needed.",
                    listOf(
                        Link("GDC — Find an Offender", "https://gdc.georgia.gov/offender-info/find-offender"),
                        Link("GDC offender query form", "https://services.gdc.ga.gov/GDC/OffenderQuery/jsp/OffQryForm.jsp"),
                        Link("Help a loved one (money, calls, visits)", "app:help_loved_one")
                    )
                ),
                Section(
                    "County jails (examples — confirm on the sheriff site)",
                    "County custody uses each sheriff’s inmate search. Official examples:\n• Gwinnett — check gwinnettcountysheriff.com inmate tools\n• Fulton — Fulton County Jail inmate search on the sheriff site\n• DeKalb, Cobb — sheriff inmate search pages\nIf a link moves, search the county sheriff’s official website for “inmate search.”",
                    listOf(
                        Link("Gwinnett County Sheriff", "https://www.gwinnettcountysheriff.com/"),
                        Link("Fulton County Sheriff", "https://www.fultonsheriff.org/"),
                        Link("DeKalb County Sheriff", "https://www.dekalbsheriff.org/"),
                        Link("Cobb County Sheriff", "https://www.cobbsheriff.org/")
                    )
                )
            )
        ),
        Feature(
            "parole_rights",
            "Parole, pardon & rights restoration",
            "Voting vs Board applications — from the Parole Board site",
            listOf(
                Section(
                    "Voting after a felony",
                    "According to the State Board of Pardons and Paroles: the right to vote is automatically restored when you complete your sentence(s), including incarceration, probation and parole. You do not apply to the Board to vote. You must re-register with your county registrar.",
                    listOf(Link("Pardons & Restoration of Rights (PAP)", "https://pap.georgia.gov/parole-population-georgia/pardons-restoration-rights"))
                ),
                Section(
                    "Pardon and other civil rights",
                    "A pardon is official forgiveness and does not erase the conviction from the record by itself. Restoration of civil and political rights (jury, public office, Notary) is a Board process with waiting periods described on the PAP site (commonly 2 years after sentence for restoration of rights; 5 years for many pardons — confirm current rules on the official page). Applications are free and electronic. Firearm restoration has extra rules.",
                    listOf(
                        Link("PAP — Pardons & Restoration of Rights", "https://pap.georgia.gov/parole-population-georgia/pardons-restoration-rights"),
                        Link("PAP — Pardons FAQs", "https://pap.georgia.gov/parole-consideration/pardons-restoration-rights/pardons-faqs")
                    )
                )
            )
        ),
        Feature(
            "dds_reinstatement",
            "Driver’s license reinstatement",
            "DDS paths for Super Speeder, FTA, DUI and more",
            listOf(
                Section(
                    "Check your status first",
                    "Reinstatement steps depend on the suspension type. Use DDS Online Services or the DDS 2 GO app for personalized requirements. Common types listed by DDS include Super Speeder, child support, DUI, Failure to Appear (FTA), no proof of insurance, and points.",
                    listOf(
                        Link("DDS — Reinstate license", "https://dds.georgia.gov/georgia-licenseid/violations-suspensions-revocations/reinstate-license"),
                        Link("DDS Online Services", "https://online.dds.ga.gov/")
                    )
                ),
                Section(
                    "Failure to Appear (FTA)",
                    "DDS states an FTA suspension occurs when a driver fails to appear in court or does not pay a traffic citation. Clearing the court case and following DDS reinstatement steps is required. Contact the court that issued the citation for the case status.",
                    listOf(Link("DDS reinstate license (FTA section)", "https://dds.georgia.gov/georgia-licenseid/violations-suspensions-revocations/reinstate-license"))
                )
            )
        ),
        Feature(
            "eviction_answer",
            "Eviction (dispossessory) Answer",
            "Official guided forms — you still file them yourself",
            listOf(
                Section(
                    "Act quickly",
                    "Dispossessory (eviction) cases move fast. Use Georgia Guide & File for a Dispossessory Answer interview when available, and read Georgia Courts landlord/tenant self-help. Civil Case Check in this app can outline claims and deadlines from your facts — then confirm with the official forms.",
                    listOf(
                        Link("Guide & File (Dispossessory Answer)", "https://www.guideandfile.com/"),
                        Link("Georgia Courts — Self-help (landlord/tenant)", "https://georgiacourts.gov/a2j/self-help-resources/"),
                        Link("Georgia Legal Aid", "https://www.georgialegalaid.org/"),
                        Link("Open Civil Case Check", "app:civil_check")
                    )
                )
            )
        ),
        Feature(
            "voting",
            "Voting rights after a felony",
            "Automatic restoration when the sentence is complete",
            listOf(
                Section(
                    "The short version",
                    "Per the State Board of Pardons and Paroles: you do not need a pardon to vote again. When all sentences are finished (prison, probation and parole), voting rights are restored automatically. Re-register to vote with your county registrar. Jury service, holding public office and Notary require a separate Board process.",
                    listOf(
                        Link("PAP — Restoration of Rights (voting FAQ)", "https://pap.georgia.gov/parole-population-georgia/pardons-restoration-rights"),
                        Link("Georgia Secretary of State — Register to vote", "https://sos.ga.gov/elections-division-office-secretary-state")
                    )
                )
            )
        ),
        Feature(
            "traffic_stop",
            "Traffic stop — know your rights",
            "Guest information for police encounters on the road",
            listOf(
                Section(
                    "Stay safe and clear",
                    "Keep your hands visible. You may ask whether you are free to leave. You may clearly say you do not consent to a search. You may remain silent and ask for a lawyer. Do not resist, lie or destroy evidence. This is general information, not a script that fits every situation.",
                    emptyList()
                ),
                Section(
                    "Documents officers may ask for",
                    "Licensed drivers are generally expected to show license, registration and proof of insurance when lawfully stopped. Ask Talk to Me for Georgia-specific questions after the stop, when you are safe.",
                    listOf(Link("Ask Talk to Me (AI Help)", "app:talk"))
                )
            )
        ),
        Feature(
            "reentry",
            "Reentry starter kit",
            "ID, housing, jobs, legal aid and crisis lines",
            listOf(
                Section(
                    "Official and free starting points",
                    "Use these public resources after release or while clearing a record. Always verify current programs on the linked sites.",
                    listOf(
                        Link("Georgia Justice Project — Resources", "https://www.gjp.org/resources/"),
                        Link("Georgia Legal Aid", "https://www.georgialegalaid.org/"),
                        Link("Georgia Legal Services Program", "https://www.glsp.org/"),
                        Link("Atlanta Legal Aid", "https://atlantalegalaid.org/"),
                        Link("DDS — License / ID", "https://dds.georgia.gov/"),
                        Link("PAP — Pardons & rights", "https://pap.georgia.gov/parole-population-georgia/pardons-restoration-rights"),
                        Link("211 — food, shelter, local help", "tel:211"),
                        Link("988 — crisis & suicide lifeline", "https://988lifeline.org/")
                    )
                )
            )
        )
    )

    fun hubRows(): List<Pair<String, String>> = FEATURES.map { it.title to it.blurb }

    fun feature(id: String): Feature? = FEATURES.firstOrNull { it.id == id }
}
