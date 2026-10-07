package help.galaw.standalone

/**
 * Drawer labels for the navy and gold home shell.
 * Private case tools stay login-only. Guest rights and official indexes do not.
 */
data class HomeDrawerItem(val id: String, val label: String, val requiresSignIn: Boolean)

object HomeDrawerCatalog {
    val items: List<HomeDrawerItem> = listOf(
        HomeDrawerItem("home", "Home", false),
        HomeDrawerItem("cases", "My Cases", true),
        HomeDrawerItem("ai", "AI Help", false),
        HomeDrawerItem("tools", "Legal Tools", false),
        HomeDrawerItem("laws", "Georgia Laws", false),
        HomeDrawerItem("court", "Court Info", false),
        HomeDrawerItem("forms", "Legal Forms", false),
        HomeDrawerItem("analysis", "Case Analysis", true),
        HomeDrawerItem("rights", "Know Your Rights", false),
        HomeDrawerItem("resources", "Resources", false),
        HomeDrawerItem("emergency", "Emergency Help", false),
        HomeDrawerItem("dark", "Dark Mode", false),
        HomeDrawerItem("settings", "Settings", false),
        HomeDrawerItem("logout", "Log Out", false)
    )
}
