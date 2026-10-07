package help.galaw.standalone

/**
 * Drawer labels for the navy and gold home shell.
 * Guest rights stay on /public/rights-assistant. Private cases stay login-only.
 */
object HomeDrawer {
    const val NOTICE =
        "Guest rights stay on /public/rights-assistant. Private cases, evidence, and case analysis stay login-only. " +
        "Dark mode keeps the approved navy and gold screens. Do not resist, lie, or destroy evidence."

    val items: List<String> = listOf(
        "Home",
        "My Cases",
        "AI Help",
        "Legal Tools",
        "Georgia Laws",
        "Court Info",
        "Legal Forms",
        "Case Analysis",
        "Know Your Rights",
        "Resources",
        "Emergency Help",
        "Dark Mode",
        "Settings",
        "Log Out"
    )

    val loginOnly: Set<String> = setOf("My Cases", "Case Analysis")
}
