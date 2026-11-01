package help.galaw.standalone

/**
 * Side drawer items, in the order of the approved design mockup.
 * No item needs sign-in: the app uses an anonymous device session for private case tools.
 */
data class HomeDrawerItem(val id: String, val label: String, val requiresSignIn: Boolean)

object HomeDrawerCatalog {
    val items: List<HomeDrawerItem> = listOf(
        HomeDrawerItem("home", "Home", false),
        HomeDrawerItem("cases", "My Cases", false),
        HomeDrawerItem("ai", "Talk to Me (AI)", false),
        HomeDrawerItem("laws", "Georgia Laws", false),
        HomeDrawerItem("funny", "Funny & Weird Laws", false),
        HomeDrawerItem("loopholes", "Legal Loopholes", false),
        HomeDrawerItem("charges", "Charge Check", false),
        HomeDrawerItem("motions", "Motions & Legal Work", false),
        HomeDrawerItem("forms", "Legal Forms", false),
        HomeDrawerItem("court", "Court Information", false),
        HomeDrawerItem("rights", "Know Your Rights", false),
        HomeDrawerItem("resources", "Resources", false),
        HomeDrawerItem("emergency", "Emergency Information", false),
        HomeDrawerItem("payments", "Payments & Subscription", false),
        HomeDrawerItem("settings", "Settings", false),
        HomeDrawerItem("profile", "Profile", false),
        HomeDrawerItem("help", "Help & Support", false)
    )
}
