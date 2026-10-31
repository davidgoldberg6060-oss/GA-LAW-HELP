package help.galaw.standalone

/**
 * Side drawer items, in the order of the approved design mockup.
 * Private case tools stay login-only. Guest rights and official indexes do not.
 */
data class HomeDrawerItem(val id: String, val label: String, val requiresSignIn: Boolean)

object HomeDrawerCatalog {
    val items: List<HomeDrawerItem> = listOf(
        HomeDrawerItem("home", "Home", false),
        HomeDrawerItem("cases", "My Cases", true),
        HomeDrawerItem("ai", "Talk to Me (AI)", false),
        HomeDrawerItem("laws", "Georgia Laws", false),
        HomeDrawerItem("loopholes", "Legal Loopholes", true),
        HomeDrawerItem("charges", "Charge Check", true),
        HomeDrawerItem("motions", "Motions & Legal Work", true),
        HomeDrawerItem("forms", "Legal Forms", false),
        HomeDrawerItem("court", "Court Information", false),
        HomeDrawerItem("rights", "Know Your Rights", false),
        HomeDrawerItem("resources", "Resources", false),
        HomeDrawerItem("emergency", "Emergency Information", false),
        HomeDrawerItem("payments", "Payments & Subscription", false),
        HomeDrawerItem("settings", "Settings", false),
        HomeDrawerItem("profile", "Profile", true),
        HomeDrawerItem("help", "Help & Support", false)
    )
}
