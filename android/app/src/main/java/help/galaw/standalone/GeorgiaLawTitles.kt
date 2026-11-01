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
    const val SUPREME_OPINIONS_URL = "https://www.gasupreme.us/"
    const val APPEALS_OPINIONS_URL = "https://www.gaappeals.us/"

    val titles: List<GeorgiaLawTitle> = listOf(
        GeorgiaLawTitle(16, "Crimes and Offenses", CODE_REVISION_URL, SUPREME_OPINIONS_URL),
        GeorgiaLawTitle(17, "Criminal Procedure", CODE_REVISION_URL, SUPREME_OPINIONS_URL),
        GeorgiaLawTitle(19, "Domestic Relations", CODE_REVISION_URL, APPEALS_OPINIONS_URL),
        GeorgiaLawTitle(40, "Motor Vehicles and Traffic", CODE_REVISION_URL, APPEALS_OPINIONS_URL),
        GeorgiaLawTitle(42, "Penal Institutions", CODE_REVISION_URL, SUPREME_OPINIONS_URL),
        GeorgiaLawTitle(44, "Property", CODE_REVISION_URL, APPEALS_OPINIONS_URL)
    )

    /** All 53 O.C.G.A. titles for the Georgia Laws title filter. */
    val codeTitles: List<Pair<Int, String>> = listOf(
        1 to "General Provisions",
        2 to "Agriculture",
        3 to "Alcoholic Beverages",
        4 to "Animals",
        5 to "Appeal and Error",
        6 to "Aviation",
        7 to "Banking and Finance",
        8 to "Buildings and Housing",
        9 to "Civil Practice",
        10 to "Commerce and Trade",
        11 to "Commercial Code",
        12 to "Conservation and Natural Resources",
        13 to "Contracts",
        14 to "Corporations, Partnerships, and Associations",
        15 to "Courts",
        16 to "Crimes and Offenses",
        17 to "Criminal Procedure",
        18 to "Debtor and Creditor",
        19 to "Domestic Relations",
        20 to "Education",
        21 to "Elections",
        22 to "Eminent Domain",
        23 to "Equity",
        24 to "Evidence",
        25 to "Fire Protection and Safety",
        26 to "Food, Drugs, and Cosmetics",
        27 to "Game and Fish",
        28 to "General Assembly",
        29 to "Guardian and Ward",
        30 to "Handicapped Persons",
        31 to "Health",
        32 to "Highways, Bridges, and Ferries",
        33 to "Insurance",
        34 to "Labor and Industrial Relations",
        35 to "Law Enforcement Officers and Agencies",
        36 to "Local Government",
        37 to "Mental Health",
        38 to "Military, Emergency Management, and Veterans Affairs",
        39 to "Minors",
        40 to "Motor Vehicles and Traffic",
        41 to "Nuisances",
        42 to "Penal Institutions",
        43 to "Professions and Businesses",
        44 to "Property",
        45 to "Public Officers and Employees",
        46 to "Public Utilities and Public Transportation",
        47 to "Retirement and Pensions",
        48 to "Revenue and Taxation",
        49 to "Social Services",
        50 to "State Government",
        51 to "Torts",
        52 to "Waters of the State, Ports, and Watercraft",
        53 to "Wills, Trusts, and Administration of Estates"
    )

    fun byNumber(number: Int): GeorgiaLawTitle = titles.first { it.number == number }
}
