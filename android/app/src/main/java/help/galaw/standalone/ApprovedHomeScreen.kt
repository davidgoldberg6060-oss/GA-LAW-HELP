package help.galaw.standalone

import android.graphics.Color
import android.graphics.Typeface
import android.graphics.drawable.GradientDrawable
import android.view.Gravity
import android.view.View
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity

/** Owner-approved GA.LAW.HELP home template: Lady Justice hero + 3x3 legal dashboard. */
class ApprovedHomeScreen(private val activity: AppCompatActivity, private val actions: Actions) {
    interface Actions {
        fun openMenu(); fun openAccount(); fun ask(question: String); fun openCases(); fun openTalkToMe()
        fun openLegalTools(); fun openGeorgiaLaws(); fun openCourtInfo(); fun openLegalForms(); fun openCaseAnalysis()
        fun openKnowYourRights(); fun openResources(); fun openEmergency(); fun openHome(); fun openDocuments()
    }

    private val navy = Color.rgb(2, 17, 29)
    private val panel = Color.rgb(7, 29, 47)
    private val border = Color.rgb(25, 82, 120)
    private val blue = Color.rgb(38, 169, 255)
    private val gold = Color.rgb(226, 181, 78)
    private val muted = Color.rgb(175, 194, 208)
    private fun dp(v: Int) = (v * activity.resources.displayMetrics.density).toInt()

    fun build(): View {
        val shell = LinearLayout(activity).apply { orientation = LinearLayout.VERTICAL; setBackgroundColor(navy) }
        val body = LinearLayout(activity).apply { orientation = LinearLayout.VERTICAL; setPadding(dp(12), dp(8), dp(12), dp(14)) }
        body.addView(header())
        body.addView(hero())
        body.addView(gridRow(
            tile("▰", "My Cases", "Track & manage", Color.rgb(34, 159, 255), actions::openCases),
            tile("●", "AI Help", "Ask legal questions", Color.rgb(43, 201, 112), actions::openTalkToMe),
            tile("▤", "Legal Tools", "Motions, timelines", gold, actions::openLegalTools)))
        body.addView(gridRow(
            tile("⚖", "Georgia Laws", "Statutes & cases", Color.rgb(235, 61, 65), actions::openGeorgiaLaws),
            tile("▰", "Court Info", "Find courts & info", Color.rgb(144, 103, 246), actions::openCourtInfo),
            tile("▤", "Legal Forms", "State forms library", Color.rgb(245, 139, 53), actions::openLegalForms)))
        body.addView(gridRow(
            tile("⌕", "Case Analysis", "Analyze & strategy", Color.rgb(45, 195, 206), actions::openCaseAnalysis),
            tile("♦", "Know Your Rights", "Learn your rights", Color.rgb(233, 91, 124), actions::openKnowYourRights),
            tile("♟", "Resources", "Links & support", Color.rgb(155, 176, 191), actions::openResources)))
        body.addView(emergencyBanner(), LinearLayout.LayoutParams(-1, -2).apply { setMargins(dp(3), dp(7), dp(3), dp(8)) })
        val scroll = ScrollView(activity).apply { isFillViewport = true; addView(body) }
        shell.addView(scroll, LinearLayout.LayoutParams(-1, 0, 1f)); shell.addView(bottomNav()); return shell
    }

    private fun header() = LinearLayout(activity).apply {
        orientation = LinearLayout.HORIZONTAL; gravity = Gravity.CENTER_VERTICAL
        addView(text("☰", 25f, false, blue).apply { gravity = Gravity.CENTER; contentDescription = "Open menu"; setOnClickListener { actions.openMenu() } }, LinearLayout.LayoutParams(dp(42), dp(48)))
        addView(text("⚖  GA.LAW.HELP", 19f, true, gold).apply { gravity = Gravity.CENTER_VERTICAL }, LinearLayout.LayoutParams(0, dp(48), 1f))
        addView(text("⌕", 27f, false, Color.WHITE).apply { gravity = Gravity.CENTER; contentDescription = "Search Georgia laws"; setOnClickListener { actions.openGeorgiaLaws() } }, LinearLayout.LayoutParams(dp(42), dp(48)))
    }

    private fun hero() = LinearLayout(activity).apply {
        orientation = LinearLayout.VERTICAL; gravity = Gravity.CENTER_HORIZONTAL; setPadding(0, 0, 0, dp(7))
        addView(ImageView(activity).apply { setImageResource(R.drawable.ic_lady_justice); scaleType = ImageView.ScaleType.CENTER_INSIDE; contentDescription = "Blindfolded Lady Justice holding scales" }, LinearLayout.LayoutParams(-1, dp(185)))
        addView(text("GA.LAW.HELP", 28f, true, gold).apply { gravity = Gravity.CENTER; setTypeface(Typeface.create(Typeface.SERIF, Typeface.BOLD)) })
        addView(text("KNOW YOUR RIGHTS. PROTECT YOUR FUTURE.", 10f, false, Color.rgb(184, 207, 222)).apply { gravity = Gravity.CENTER; letterSpacing = .08f; setPadding(0, dp(2), 0, dp(3)) })
        addView(text("Georgia legal help, documents, case tools\nand AI guidance in one secure place.", 12f, false, Color.rgb(215, 225, 232)).apply { gravity = Gravity.CENTER })
    }

    private fun gridRow(vararg views: View) = LinearLayout(activity).apply {
        orientation = LinearLayout.HORIZONTAL
        views.forEach { addView(it, LinearLayout.LayoutParams(0, dp(104), 1f).apply { setMargins(dp(3), dp(3), dp(3), dp(3)) }) }
    }

    private fun tile(icon: String, title: String, subtitle: String, iconColor: Int, action: () -> Unit) = LinearLayout(activity).apply {
        orientation = LinearLayout.VERTICAL; gravity = Gravity.CENTER; setPadding(dp(4), dp(6), dp(4), dp(5)); background = rounded(panel, border, 1, 12)
        addView(text(icon, 25f, true, iconColor).apply { gravity = Gravity.CENTER })
        addView(text(title, 12f, true, Color.WHITE).apply { gravity = Gravity.CENTER; setPadding(0, dp(2), 0, 0) })
        addView(text(subtitle, 9f, false, muted).apply { gravity = Gravity.CENTER })
        setOnClickListener { action() }
    }

    private fun emergencyBanner() = LinearLayout(activity).apply {
        orientation = LinearLayout.HORIZONTAL; gravity = Gravity.CENTER_VERTICAL; setPadding(dp(12), dp(9), dp(10), dp(9)); background = rounded(Color.rgb(116, 18, 25), Color.rgb(229, 57, 63), 1, 12)
        addView(text("☎", 27f, true, Color.WHITE).apply { gravity = Gravity.CENTER }, LinearLayout.LayoutParams(dp(45), -1))
        addView(LinearLayout(activity).apply { orientation = LinearLayout.VERTICAL; addView(text("Emergency Help", 13f, true, Color.WHITE)); addView(text("Important contacts & immediate resources", 9f, false, Color.rgb(242, 205, 208))) }, LinearLayout.LayoutParams(0, -2, 1f))
        addView(text("›", 24f, true, Color.WHITE)); setOnClickListener { actions.openEmergency() }
    }

    private fun bottomNav() = LinearLayout(activity).apply {
        orientation = LinearLayout.HORIZONTAL; setPadding(dp(3), dp(3), dp(3), dp(4)); setBackgroundColor(Color.rgb(3, 20, 34))
        listOf(Triple("⌂", "Home", actions::openHome), Triple("⚖", "Laws", actions::openGeorgiaLaws), Triple("●", "AI Help", actions::openTalkToMe), Triple("▰", "Documents", actions::openDocuments), Triple("●", "Account", actions::openAccount)).forEachIndexed { i, item ->
            addView(text("${item.first}\n${item.second}", 9.5f, false, if (i == 0) blue else muted).apply { gravity = Gravity.CENTER; setPadding(0, dp(5), 0, dp(5)); setOnClickListener { item.third() } }, LinearLayout.LayoutParams(0, -2, 1f))
        }
    }

    private fun text(value: String, size: Float, bold: Boolean, color: Int) = TextView(activity).apply { text = value; textSize = size; setTextColor(color); if (bold) setTypeface(typeface, Typeface.BOLD) }
    private fun rounded(fill: Int, stroke: Int, strokeWidth: Int, radius: Int) = GradientDrawable().apply { setColor(fill); cornerRadius = dp(radius).toFloat(); if (strokeWidth > 0) setStroke(dp(strokeWidth), stroke) }
}
