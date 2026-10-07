package help.galaw.standalone

/**
 * Official-index catalog for the Georgia Laws screen.
 * Section text is not stored here. Lexis annotations are not used.
 * A missing DATABASE_URL must not be treated as an ingested corpus.
 */
data class GeorgiaLawTitle(
    val number: Int,
    val name: String,
    val codeIndexUrl: String,
    val caseLawIndexUrl: String
)

object GeorgiaLawTitles {
    const val NOTICE =
        "Code links open the Georgia Code Revision Commission index and the state's unannotated electronic release. " +
        "They are not Lexis annotations and are not a claim that a section is current. " +
        "Case Law links open court opinion indexes only. This screen does not invent citations or load a private case."

    const val CODE_REVISION_URL = "https://www.legis.ga.gov/joint-offices/code-revision"
    const val UNANNOTATED_RELEASE_URL = "https://archive.org/details/gov.ga.ocga.2018"
    const val SUPREME_OPINIONS_URL = "https://www.gasupreme.us/opinions/"
    const val APPEALS_OPINIONS_URL = "https://www.gaappeals.us/"

    val titles: List<GeorgiaLawTitle> = listOf(
        GeorgiaLawTitle(16, "Crimes and Offenses", CODE_REVISION_URL, SUPREME_OPINIONS_URL),
        GeorgiaLawTitle(17, "Criminal Procedure", CODE_REVISION_URL, SUPREME_OPINIONS_URL),
        GeorgiaLawTitle(19, "Domestic Relations", CODE_REVISION_URL, APPEALS_OPINIONS_URL),
        GeorgiaLawTitle(40, "Motor Vehicles and Traffic", CODE_REVISION_URL, APPEALS_OPINIONS_URL),
        GeorgiaLawTitle(42, "Penal Institutions", CODE_REVISION_URL, SUPREME_OPINIONS_URL),
        GeorgiaLawTitle(44, "Property", CODE_REVISION_URL, APPEALS_OPINIONS_URL)
    )

    fun byNumber(number: Int): GeorgiaLawTitle = titles.first { it.number == number }
}
