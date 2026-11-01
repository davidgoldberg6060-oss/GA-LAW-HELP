package help.galaw.standalone

import android.content.Context
import android.graphics.Color
import android.graphics.Typeface
import android.util.TypedValue
import android.view.Gravity
import android.view.inputmethod.EditorInfo
import android.view.View
import android.widget.EditText
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
        fun openFunnyLaws(); fun openLegalTools(); fun openGeorgiaLaws(); fun openCourtInfo(); fun openLegalForms(); fun openCaseAnalysis()
        fun openKnowYourRights(); fun openResources(); fun openEmergency(); fun openHome(); fun openDocuments()
    }

    private val ui = GaUi(context)
    private val regular: Typeface = Typeface.DEFAULT
    private val medium get() = ui.sansMedium
    private val bold get() = ui.sansBold

    /**
     * The screen is the approved mockup itself: artwork strips cropped from the owner's mockup
     * (Lady Justice header, glowing controls, photographic tiles, courthouse backdrop) laid out
     * full width, with live text, input and touch targets placed at the mockup's exact
     * coordinates (1024-unit grid). Extra height on tall phones is shared between the sections.
     */
    fun build(): View {
        val shell = LinearLayout(context).apply { orientation = LinearLayout.VERTICAL; setBackgroundColor(BG) }
        val body = Column()
        body.addView(header())
        body.addGap()
        body.addView(quickCards())
        body.addGap()
        body.addView(tiles(R.drawable.ga_home_tiles_1, 568, 808, 0))
        body.addGap()
        body.addView(tiles(R.drawable.ga_home_tiles_2, 808, 1030, 3))
        body.addGap()
        body.addView(emergency())
        body.addGap()
        body.addView(footer(), LinearLayout.LayoutParams(-1, ui.u(FOOTER), 1f))
        shell.addView(ScrollView(context).apply { isFillViewport = true; isVerticalScrollBarEnabled = false; addView(body) }, LinearLayout.LayoutParams(-1, 0, 1f))
        shell.addView(ui.bottomNav(listOf(
            GaUi.NavItem("home", "Home", R.drawable.ga_ic_home) { actions.openHome() },
            GaUi.NavItem("laws", "Laws", R.drawable.ga_ic_balance) { actions.openGeorgiaLaws() },
            GaUi.NavItem("ai", "AI Help", R.drawable.ga_ic_sms) { actions.openTalkToMe() },
            GaUi.NavItem("funny", "Funny", R.drawable.ga_ic_mood) { actions.openFunnyLaws() },
            GaUi.NavItem("documents", "Documents", R.drawable.ga_ic_description) { actions.openDocuments() },
            GaUi.NavItem("account", "Account", R.drawable.ga_ic_person) { actions.openAccount() }), "home"))
        return shell
    }

    /**
     * On phones taller than the 2:3 mockup the sections keep their exact mockup proportions; the
     * spare height goes partly to the courthouse footer (which stretches) and the rest to even gaps.
     */
    private inner class Column : LinearLayout(context) {
        private val gaps = mutableListOf<View>()
        init { orientation = VERTICAL }
        fun addGap() { val g = View(context); gaps += g; addView(g, LayoutParams(-1, 0)) }
        override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
            val extra = if (MeasureSpec.getMode(heightMeasureSpec) == MeasureSpec.EXACTLY) (MeasureSpec.getSize(heightMeasureSpec) - ui.u(1388)).coerceAtLeast(0) else 0
            val footerExtra = minOf(extra * 0.5f, ui.uf(FOOTER * 1.6f))
            val gap = if (gaps.isEmpty()) 0 else ((extra - footerExtra) / gaps.size).toInt()
            gaps.forEach { it.layoutParams.height = gap }
            super.onMeasure(widthMeasureSpec, heightMeasureSpec)
        }
    }

    /** Lady Justice header, wordmark, headline, subtitle and search bar (mockup y 0–445). */
    private fun header(): View {
        val f = ui.artStrip(R.drawable.ga_home_header, 445, "GA.LAW.HELP. Clear answers. A stronger Georgia. Know your rights, build a better tomorrow. Legal answers anytime.")
        ui.hit(f, 18, 18, 82, 76, "Open menu") { actions.openMenu() }
        ui.hit(f, 826, 14, 896, 84, "Search Georgia laws", 40) { actions.openGeorgiaLaws() }
        ui.hit(f, 926, 12, 1004, 86, "Account", 40) { actions.openAccount() }
        ui.placeText(f, "Search Georgia law, get guidance, and take the next step with confidence.", regular, Color.rgb(247, 250, 253), 122, 294, 910)
        // Live search input sitting on the mockup's glowing bar.
        val probe = ui.placeText(FrameLayout(context), "Ask a legal question...", regular, 0, 155, 377, 405)
        val field = EditText(context).apply {
            hint = "Ask a legal question..."; contentDescription = "Ask a legal question"
            setHintTextColor(Color.rgb(160, 181, 214)); setTextColor(Color.WHITE); background = null; isSingleLine = true
            setTextSize(TypedValue.COMPLEX_UNIT_PX, probe.textSize); includeFontPadding = false; gravity = Gravity.CENTER_VERTICAL
            setPadding(0, 0, 0, 0); imeOptions = EditorInfo.IME_ACTION_SEARCH
            setOnEditorActionListener { v, _, _ -> submit(v.text.toString()); true }
        }
        val b = android.graphics.Rect(); field.paint.getTextBounds("A", 0, 1, b)
        f.addView(field, FrameLayout.LayoutParams(ui.u(880 - 155), ui.u(431 - 344)).apply { leftMargin = ui.u(155) - b.left; topMargin = ui.u(344) })
        ui.hit(f, 884, 350, 956, 422, "Ask", 40) { submit(field.text.toString()) }
        return f
    }

    /** My Cases · Talk to Me · Legal Tools (mockup y 445–568). */
    private fun quickCards(): View {
        val f = ui.artStrip(R.drawable.ga_home_quick, 568 - 445)
        quick(f, 37, 333, 456, 552, "My Cases", "Manage your cases", intArrayOf(150, 485, 241), intArrayOf(150, 515, 292), actions::openCases)
        quick(f, 364, 662, 455, 555, "Talk to Me", "Get legal answers", intArrayOf(469, 484, 569), intArrayOf(469, 514, 609), actions::openTalkToMe)
        quick(f, 694, 987, 456, 552, "Legal Tools", "Forms, templates & more", intArrayOf(799, 485, 906), intArrayOf(799, 514, 969), actions::openLegalTools)
        return f
    }

    private fun submit(q: String) { if (q.isNotBlank()) actions.ask(q.trim()) else actions.openTalkToMe() }

    private fun quick(f: FrameLayout, x0: Int, x1: Int, y0: Int, y1: Int, title: String, sub: String, t: IntArray, s: IntArray, action: () -> Unit) {
        ui.placeText(f, title, medium, Color.WHITE, t[0], t[1], t[2], originY = 445)
        ui.placeText(f, sub, regular, Color.rgb(199, 213, 231), s[0], s[1], s[2], originY = 445)
        ui.hit(f, x0, y0, x1, y1, "$title. $sub", 14, originY = 445, action = action)
    }

    private class Tile(val x0: Int, val y0: Int, val x1: Int, val y1: Int, val title: String, val sub: String, val t: IntArray, val s: IntArray, val action: () -> Unit)

    private val tileSpecs by lazy { listOf(
        Tile(27, 584, 333, 796, "Georgia Laws", "Statutes & rules", intArrayOf(103, 717, 261), intArrayOf(110, 754, 255), actions::openGeorgiaLaws),
        Tile(362, 584, 668, 796, "Court Info", "Find courts & dockets", intArrayOf(456, 717, 575), intArrayOf(416, 754, 615), actions::openCourtInfo),
        Tile(697, 584, 1000, 796, "Legal Forms", "Fill & download", intArrayOf(780, 717, 921), intArrayOf(780, 754, 919), actions::openLegalForms),
        Tile(27, 819, 334, 1018, "Case Analysis", "Get insights", intArrayOf(102, 940, 262), intArrayOf(128, 976, 237), actions::openCaseAnalysis),
        Tile(362, 819, 668, 1018, "Know Your Rights", "Learn in plain language", intArrayOf(413, 940, 620), intArrayOf(411, 976, 621), actions::openKnowYourRights),
        Tile(697, 819, 1000, 1018, "Resources", "Aid, programs & more", intArrayOf(791, 940, 910), intArrayOf(750, 977, 949), actions::openResources)) }

    /** One row of three photographic tiles. */
    private fun tiles(res: Int, o: Int, end: Int, first: Int): View {
        val f = ui.artStrip(res, end - o)
        tileSpecs.subList(first, first + 3).forEach { tile(f, o, it.x0, it.y0, it.x1, it.y1, it.title, it.sub, it.t, it.s, it.action) }
        return f
    }

    private fun tile(f: FrameLayout, o: Int, x0: Int, y0: Int, x1: Int, y1: Int, title: String, sub: String, t: IntArray, s: IntArray, action: () -> Unit) {
        ui.placeText(f, title, medium, Color.WHITE, t[0], t[1], t[2], originY = o)
        ui.placeText(f, sub, regular, Color.rgb(204, 221, 241), s[0], s[1], s[2], originY = o)
        ui.hit(f, x0, y0, x1, y1, "$title. $sub", 14, originY = o, action = action)
    }

    /** Emergency Information banner (mockup y 1030–1152). */
    private fun emergency(): View {
        val o = 1030
        val f = ui.artStrip(R.drawable.ga_home_emergency, 1152 - o)
        ui.placeText(f, "EMERGENCY INFORMATION", bold, Color.WHITE, 177, 1064, 533, originY = o)
        ui.placeText(f, "Get immediate help and important resources.", regular, Color.rgb(252, 225, 217), 176, 1100, 604, originY = o)
        ui.placeText(f, "Find help now", medium, Color.WHITE, 789, 1083, 922, originY = o)
        ui.hit(f, 27, 1040, 996, 1140, "Emergency Information. Find help now", 16, originY = o) { actions.openEmergency() }
        return f
    }

    /** Quote over the courthouse/cloud backdrop (mockup y 1152–1388); stretches on tall phones. */
    private fun footer(): View {
        val o = 1152
        val f = object : FrameLayout(context) {
            override fun onSizeChanged(w: Int, h: Int, oldw: Int, oldh: Int) {
                super.onSizeChanged(w, h, oldw, oldh)
                val shift = (h - ui.uf(FOOTER.toFloat())).coerceAtLeast(0f) * 0.42f
                for (i in 1 until childCount) getChildAt(i).translationY = shift
            }
        }
        f.addView(android.widget.ImageView(context).apply { setImageResource(R.drawable.ga_home_quote); scaleType = android.widget.ImageView.ScaleType.FIT_XY; importantForAccessibility = View.IMPORTANT_FOR_ACCESSIBILITY_NO }, FrameLayout.LayoutParams(-1, -1))
        ui.glowText(ui.placeText(f, "\u201CJustice is not a privilege. It\u2019s a right.\u201D", Typeface.create(Typeface.SERIF, Typeface.ITALIC), Color.rgb(250, 251, 253), 238, 1187, 789, originY = o), Color.BLACK, 10f)
        ui.placeSpaced(f, "GA.LAW.HELP", regular, Color.rgb(236, 241, 248), 438, 1243, 586, 1258, originY = o)
        f.addView(View(context).apply { background = ui.rounded(Color.rgb(83, 190, 250), 2) }, FrameLayout.LayoutParams(ui.u(84), ui.u(3).coerceAtLeast(2)).apply { leftMargin = ui.u(470); topMargin = ui.u(1279 - o) })
        ui.placeSpaced(f, "INFORMATION", regular, Color.rgb(112, 158, 208), 815, 1278, 969, 1291, originY = o)
        ui.placeSpaced(f, "EMPOWERS", regular, Color.rgb(140, 182, 228), 815, 1309, 941, 1322, originY = o)
        ui.placeSpaced(f, "PEOPLE", regular, Color.rgb(118, 163, 214), 814, 1341, 896, 1354, originY = o)
        return f
    }

    private companion object { val BG = Color.rgb(0, 8, 20); const val FOOTER = 1388 - 1152 }
}
