package help.galaw.standalone

import android.content.Context
import android.graphics.Color
import android.graphics.Typeface
import android.graphics.drawable.GradientDrawable
import android.graphics.drawable.LayerDrawable
import android.view.Gravity
import android.view.View
import android.widget.FrameLayout
import android.widget.LinearLayout
import android.widget.ScrollView

/**
 * Owner-approved GA.LAW.HELP home (design mockup): Lady Justice header, GA.LAW.HELP wordmark,
 * "LEGAL ANSWERS ANYTIME", Ask-a-legal-question search, three quick cards, six tiles,
 * Emergency Information banner, quote and the five-tab bottom nav.
 */
class ApprovedHomeScreen(private val context: Context, private val actions: Actions) {
    interface Actions {
        fun openMenu(); fun openAccount(); fun ask(question: String); fun openCases(); fun openTalkToMe()
        fun openLegalTools(); fun openGeorgiaLaws(); fun openCourtInfo(); fun openLegalForms(); fun openCaseAnalysis()
        fun openKnowYourRights(); fun openResources(); fun openEmergency(); fun openHome(); fun openDocuments()
    }

    private val ui = GaUi(context)
    private fun dp(v: Int) = ui.dp(v)

    fun build(): View {
        val shell = LinearLayout(context).apply { orientation = LinearLayout.VERTICAL; background = ui.screenBackground() }
        val body = LinearLayout(context).apply { orientation = LinearLayout.VERTICAL; setPadding(dp(14), 0, dp(14), dp(12)) }
        body.addView(hero())
        val (search, field) = ui.searchField("Ask a legal question...", glowing = true, height = 58) { q ->
            if (q.isNotBlank()) actions.ask(q.trim()) else actions.openTalkToMe()
        }
        field.contentDescription = "Ask a legal question"
        body.addView(search, LinearLayout.LayoutParams(-1, dp(58)).apply { setMargins(dp(4), dp(14), dp(4), dp(12)) })
        body.addView(row(
            quickCard(R.drawable.ga_ic_folder, "My Cases", "Manage your cases", actions::openCases),
            quickCard(R.drawable.ga_ic_sms, "Talk to Me", "Get legal answers", actions::openTalkToMe),
            quickCard(R.drawable.ga_ic_description, "Legal Tools", "Forms, templates & more", actions::openLegalTools)), )
        body.addView(row(
            tile(R.drawable.ga_ic_account_balance, GaUi.BLUE_BRIGHT, "Georgia Laws", "Statutes & rules", actions::openGeorgiaLaws),
            tile(R.drawable.ga_ic_balance, GaUi.GOLD, "Court Info", "Find courts & dockets", actions::openCourtInfo),
            tile(R.drawable.ga_ic_description, GaUi.BLUE_BRIGHT, "Legal Forms", "Fill & download", actions::openLegalForms)), LinearLayout.LayoutParams(-1, -2).apply { topMargin = dp(8) })
        body.addView(row(
            tile(R.drawable.ga_ic_find_in_page, GaUi.BLUE_BRIGHT, "Case Analysis", "Get insights", actions::openCaseAnalysis),
            tile(R.drawable.ga_ic_groups, GaUi.BLUE_BRIGHT, "Know Your Rights", "Learn in plain language", actions::openKnowYourRights),
            tile(R.drawable.ga_ic_support, GaUi.BLUE_BRIGHT, "Resources", "Aid, programs & more", actions::openResources)))
        body.addView(emergencyBanner(), LinearLayout.LayoutParams(-1, dp(68)).apply { setMargins(dp(3), dp(12), dp(3), dp(8)) })
        body.addView(quote())
        shell.addView(ScrollView(context).apply { isFillViewport = true; addView(body) }, LinearLayout.LayoutParams(-1, 0, 1f))
        shell.addView(ui.bottomNav(listOf(
            GaUi.NavItem("home", "Home", R.drawable.ga_ic_home) { actions.openHome() },
            GaUi.NavItem("laws", "Laws", R.drawable.ga_ic_balance) { actions.openGeorgiaLaws() },
            GaUi.NavItem("ai", "AI Help", R.drawable.ga_ic_sms) { actions.openTalkToMe() },
            GaUi.NavItem("documents", "Documents", R.drawable.ga_ic_description) { actions.openDocuments() },
            GaUi.NavItem("account", "Account", R.drawable.ga_ic_person) { actions.openAccount() }), "home"))
        return shell
    }

    private fun hero(): View {
        val frame = FrameLayout(context)
        frame.addView(ui.ladyJustice(), FrameLayout.LayoutParams(dp(108), dp(130), Gravity.START or Gravity.TOP).apply { leftMargin = dp(20) })
        frame.addView(ui.icon(R.drawable.ga_ic_menu, GaUi.BLUE_BRIGHT, 30).apply { contentDescription = "Open menu"; setOnClickListener { actions.openMenu() } },
            FrameLayout.LayoutParams(dp(30), dp(30), Gravity.START or Gravity.TOP).apply { setMargins(dp(4), dp(18), 0, 0) })
        val brand = LinearLayout(context).apply { orientation = LinearLayout.VERTICAL; gravity = Gravity.CENTER_HORIZONTAL }
        brand.addView(ui.wordmark(21f))
        brand.addView(ui.tagline(7.5f).apply { setPadding(0, dp(1), 0, 0) })
        frame.addView(brand, FrameLayout.LayoutParams(-2, -2, Gravity.CENTER_HORIZONTAL or Gravity.TOP).apply { setMargins(dp(34), dp(14), 0, 0) })
        frame.addView(ui.icon(R.drawable.ga_ic_search, GaUi.BLUE_BRIGHT, 28).apply { contentDescription = "Search Georgia laws"; setOnClickListener { actions.openGeorgiaLaws() } },
            FrameLayout.LayoutParams(dp(28), dp(28), Gravity.END or Gravity.TOP).apply { setMargins(0, dp(18), dp(46), 0) })
        frame.addView(ui.icon(R.drawable.ga_ic_account_circle, GaUi.BLUE_BRIGHT, 34).apply { contentDescription = "Account"; setOnClickListener { actions.openAccount() } },
            FrameLayout.LayoutParams(dp(34), dp(34), Gravity.END or Gravity.TOP).apply { setMargins(0, dp(15), dp(2), 0) })
        frame.addView(ui.text("KNOW YOUR RIGHTS\nBUILD A BETTER\nTOMORROW", 7.5f, GaUi.withAlphaStatic(GaUi.BLUE, 200), null, Gravity.START).apply { letterSpacing = 0.18f; setLineSpacing(0f, 1.2f) },
            FrameLayout.LayoutParams(-2, -2, Gravity.END or Gravity.TOP).apply { setMargins(0, dp(58), dp(6), 0) })
        val copy = LinearLayout(context).apply { orientation = LinearLayout.VERTICAL; gravity = Gravity.CENTER_HORIZONTAL }
        copy.addView(ui.fit(ui.headline("LEGAL ANSWERS ", "ANYTIME", 25f), 16, 25), LinearLayout.LayoutParams(-1, -2))
        copy.addView(ui.text("Search Georgia law, get guidance, and take the next step with confidence.", 12.5f, Color.rgb(222, 231, 241), null, Gravity.CENTER).apply { setPadding(dp(8), dp(4), dp(8), 0) })
        frame.addView(copy, FrameLayout.LayoutParams(-1, -2, Gravity.BOTTOM))
        frame.layoutParams = LinearLayout.LayoutParams(-1, dp(182))
        return frame
    }

    private fun row(vararg views: View) = LinearLayout(context).apply {
        orientation = LinearLayout.HORIZONTAL
        views.forEach { addView(it, LinearLayout.LayoutParams(0, -2, 1f).apply { setMargins(dp(2), dp(2), dp(2), dp(2)) }) }
    }

    private fun quickCard(icon: Int, title: String, subtitle: String, action: () -> Unit) = LinearLayout(context).apply {
        orientation = LinearLayout.HORIZONTAL; gravity = Gravity.CENTER_VERTICAL; setPadding(dp(9), dp(10), dp(4), dp(10))
        background = ui.glowCard(GaUi.CARD, GaUi.STROKE, 10); minimumHeight = dp(58); isClickable = true; setOnClickListener { action() }
        addView(ui.icon(icon, GaUi.BLUE_BRIGHT, 24), LinearLayout.LayoutParams(dp(24), dp(24)).apply { rightMargin = dp(7) })
        val col = LinearLayout(context).apply { orientation = LinearLayout.VERTICAL }
        col.addView(ui.fit(ui.text(title, 13f, GaUi.WHITE, ui.sansMedium), 10, 13), LinearLayout.LayoutParams(-1, -2))
        col.addView(ui.fit(ui.text(subtitle, 9f, GaUi.MUTED), 6, 9), LinearLayout.LayoutParams(-1, -2))
        addView(col, LinearLayout.LayoutParams(0, -2, 1f))
    }

    private fun tile(icon: Int, tint: Int, title: String, subtitle: String, action: () -> Unit) = LinearLayout(context).apply {
        orientation = LinearLayout.VERTICAL; gravity = Gravity.CENTER; setPadding(dp(4), dp(12), dp(4), dp(12))
        val glow = GradientDrawable().apply { gradientType = GradientDrawable.RADIAL_GRADIENT; gradientRadius = ui.dpf(60f); setGradientCenter(0.5f, 0.3f); colors = intArrayOf(GaUi.withAlphaStatic(GaUi.BLUE, 45), Color.TRANSPARENT); cornerRadius = ui.dpf(12f) }
        background = LayerDrawable(arrayOf(ui.glowCard(GaUi.CARD, GaUi.STROKE, 12), glow)).apply { setLayerInset(1, dp(3), dp(3), dp(3), dp(3)) }
        minimumHeight = dp(120); isClickable = true; setOnClickListener { action() }
        addView(ui.icon(icon, tint, 42))
        addView(ui.fit(ui.text(title, 15f, GaUi.WHITE, ui.sansMedium, Gravity.CENTER).apply { setPadding(dp(2), dp(10), dp(2), dp(2)) }, 10, 15), LinearLayout.LayoutParams(-1, -2))
        addView(ui.fit(ui.text(subtitle, 11.5f, GaUi.MUTED, null, Gravity.CENTER).apply { setPadding(dp(2), 0, dp(2), 0) }, 7, 11), LinearLayout.LayoutParams(-1, -2))
    }

    private fun emergencyBanner() = LinearLayout(context).apply {
        orientation = LinearLayout.HORIZONTAL; gravity = Gravity.CENTER_VERTICAL; setPadding(dp(16), dp(8), dp(12), dp(8))
        val fill = GradientDrawable(GradientDrawable.Orientation.LEFT_RIGHT, intArrayOf(Color.rgb(150, 18, 26), Color.rgb(96, 10, 18), Color.rgb(120, 14, 22))).apply { cornerRadius = ui.dpf(12f); setStroke(dp(1), Color.rgb(255, 92, 96)) }
        val halo = ui.rounded(Color.TRANSPARENT, 15, GaUi.withAlphaStatic(GaUi.RED, 90), 3f)
        background = LayerDrawable(arrayOf(halo, fill)).apply { setLayerInset(1, dp(3), dp(3), dp(3), dp(3)) }
        isClickable = true; setOnClickListener { actions.openEmergency() }; contentDescription = "Emergency Information"
        addView(ui.icon(R.drawable.ga_ic_warning, Color.rgb(255, 120, 120), 34), LinearLayout.LayoutParams(dp(34), dp(34)).apply { rightMargin = dp(12) })
        val col = LinearLayout(context).apply { orientation = LinearLayout.VERTICAL }
        col.addView(ui.fit(ui.text("EMERGENCY INFORMATION", 15f, GaUi.WHITE, ui.sansBold), 9, 15), LinearLayout.LayoutParams(-1, -2))
        col.addView(ui.fit(ui.text("Get immediate help and important resources.", 11f, Color.rgb(250, 214, 216)), 6, 11), LinearLayout.LayoutParams(-1, -2))
        addView(col, LinearLayout.LayoutParams(0, -2, 1f))
        addView(ui.text("Find help now", 11.5f, GaUi.WHITE, ui.sansMedium).apply { maxLines = 1; setPadding(dp(6), 0, 0, 0) })
        addView(ui.icon(R.drawable.ga_ic_chevron_right, GaUi.WHITE, 22))
    }

    private fun quote() = LinearLayout(context).apply {
        orientation = LinearLayout.VERTICAL; gravity = Gravity.CENTER_HORIZONTAL; setPadding(0, dp(12), 0, dp(10))
        addView(ui.fit(ui.text("\u201CJustice is not a privilege. It\u2019s a right.\u201D", 19f, Color.rgb(236, 242, 250), Typeface.create(Typeface.SERIF, Typeface.ITALIC), Gravity.CENTER), 12, 19), LinearLayout.LayoutParams(-1, -2))
        addView(ui.text("GA.LAW.HELP", 11f, Color.rgb(200, 214, 230), null, Gravity.CENTER).apply { letterSpacing = 0.2f; setPadding(0, dp(8), 0, dp(8)) })
        addView(View(context).apply { background = ui.rounded(GaUi.BLUE_BRIGHT, 1) }, LinearLayout.LayoutParams(dp(54), dp(2)))
        addView(ui.text("INFORMATION\nEMPOWERS\nPEOPLE", 7.5f, GaUi.withAlphaStatic(GaUi.BLUE, 190)).apply { letterSpacing = 0.2f; setLineSpacing(0f, 1.25f) },
            LinearLayout.LayoutParams(-2, -2).apply { gravity = Gravity.END; setMargins(0, dp(8), dp(4), 0) })
    }
}
