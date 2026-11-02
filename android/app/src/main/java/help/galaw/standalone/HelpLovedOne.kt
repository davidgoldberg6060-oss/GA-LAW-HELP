package help.galaw.standalone

import android.app.AlertDialog

/** Official outbound links for helping someone in GDC custody (checked to load; vendors as listed by GDC). */
object HelpLovedOne {
    const val NOTE = "These are the services the Georgia Department of Corrections lists for state prisons. Riverbend Private Prison still uses Access Securepak for packages. County jails use their own vendors: check the county sheriff's website for how to send money, call or visit. GA.LAW.HELP never takes payments; always pay on the vendor's own site."
    val LINKS = listOf(
        "Find where they are (GDC offender search)" to "https://services.gdc.ga.gov/GDC/OffenderQuery/jsp/OffQryForm.jsp",
        "Send money: GDC's instructions (JPay)" to "https://gdc.georgia.gov/friends-and-family/how-do-i-send-money-offender",
        "JPay: send money, email and video visits" to "https://www.jpay.com/login.aspx",
        "Phone calls: GDC's Securus instructions and rates" to "https://gdc.georgia.gov/offender-info/contact-offender",
        "Securus Technologies: set up a phone account" to "https://www.securustech.net/",
        "Food and property packages: GDC rules (Union Supply)" to "https://gdc.georgia.gov/friends-and-family/sending-packages-offenders",
        "Union Supply GA package ordering" to "https://gainmatepackage.com/Home.aspx",
        "Visitation rules and how to become a visitor" to "https://gdc.georgia.gov/friends-and-family/visit-inmate",
        "Schedule a visit (GDConnect)" to "https://gdconnect.gdc.ga.gov/visitation",
        "Questions about your loved one / Ombudsman" to "https://gdc.georgia.gov/friends-and-family/questions-about-your-loved-ones"
    )
    val CUSTODY = Regex("(?i)\\b(jail|prison|locked up|incarcerat|inmate|in custody|serving (a|his|her|their|my) (sentence|time)|commissary|on (the )?books|visitation|gdc)\\b")
    fun show(ui: GaUi, open: (String) -> Unit) {
        AlertDialog.Builder(ui.context).setTitle("Help your loved one").setMessage(NOTE)
            .setItems(LINKS.map { it.first + " ›" }.toTypedArray()) { _, i -> open(LINKS[i].second) }
            .setNegativeButton("Close", null).show()
    }
}
