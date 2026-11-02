package help.galaw.standalone

import android.app.AlertDialog
import android.view.View

/** Plain-English glossary for legal terms that appear in answers. */
object Glossary {
    val TERMS = listOf(
        "Arraignment" to "The first court hearing where the charges are read and a plea (usually not guilty) is entered.",
        "Bond" to "Money or a promise the court accepts so a person can be released from jail while the case goes on.",
        "Indictment" to "A formal charge issued by a grand jury in a felony case.",
        "Accusation" to "A formal charge filed by the prosecutor, usually in misdemeanor cases.",
        "Plea" to "The defendant's answer to the charge: guilty, not guilty, or no contest (nolo contendere).",
        "First Offender" to "A Georgia program where a first-time offender's case can end without a conviction if the sentence is completed.",
        "Probation" to "Serving a sentence in the community under supervision and conditions instead of in custody.",
        "Parole" to "Early release from prison, supervised by the State Board of Pardons and Paroles.",
        "Habeas corpus" to "A court case that challenges whether someone is being held legally.",
        "Motion" to "A written request asking the judge to do something in the case.",
        "Suppress" to "To ask the judge to keep evidence out of the case, for example because of an illegal search.",
        "Demurrer" to "A motion saying the charging document itself is legally defective.",
        "Discovery" to "The process of getting the evidence the other side has, like police reports and videos.",
        "Immunity" to "Protection from being prosecuted at all; in Georgia it can apply to lawful self-defense.",
        "Justification" to "A legal defense that the act was allowed, such as self-defense.",
        "Lesser included offense" to "A less serious crime contained within the charged crime that a jury can consider instead.",
        "Speedy trial" to "The right to have the trial happen without unreasonable delay; Georgia has a formal demand process.",
        "Sentence modification" to "Asking the sentencing judge to reduce or change a sentence within the allowed time.",
        "Appeal" to "Asking a higher court to review and correct mistakes made in the trial court.",
        "Public defender" to "A lawyer provided free to someone charged with a crime who cannot afford one.",
        "Ombudsman" to "An office that looks into complaints and concerns about people in custody.",
        "Grievance" to "A written complaint filed through the facility's official process.",
        "Revocation" to "Ending probation or parole and sending the person back to custody.",
        "Warrant" to "A court order allowing police to arrest someone or search a place.",
        "Felony" to "A serious crime that can be punished by more than a year in prison.",
        "Misdemeanor" to "A less serious crime, usually punished by up to 12 months in jail or a fine.",
        "Pro se" to "Representing yourself in court without a lawyer.",
        "Next friend" to "Someone who brings a court case on behalf of another person who cannot do it themselves."
    )
    fun find(text: String): List<Pair<String, String>> = TERMS.filter { Regex("(?i)\\b" + Regex.escape(it.first)).containsMatchIn(text) }
    fun button(ui: GaUi, text: String): View? { val f = find(text); if (f.isEmpty()) return null
        return ui.secondaryButton("Legal terms explained (" + f.size + ")") {
            AlertDialog.Builder(ui.context).setTitle("Legal terms in plain English")
                .setMessage(f.joinToString("\n\n") { it.first + ": " + it.second }).setPositiveButton("Close", null).show() } }
}
