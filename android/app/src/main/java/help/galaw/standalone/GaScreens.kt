package help.galaw.standalone

import android.graphics.Color
import android.graphics.DashPathEffect
import android.graphics.Paint
import android.graphics.drawable.GradientDrawable
import android.graphics.drawable.ShapeDrawable
import android.graphics.drawable.shapes.RoundRectShape
import android.view.Gravity
import android.view.View
import android.widget.EditText
import android.widget.FrameLayout
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView

/**
 * Mockup-matched GA.LAW.HELP screens. Each builder is pure (Context + data + callbacks) so the
 * same code runs in HomeActivity and in screenshot tests. Lists come from the user's real data;
 * when there is none an empty state is shown instead of sample records.
 */
object GaScreens {
    interface Nav {
        fun menu(); fun home(); fun laws(); fun aiHelp(); fun documents(); fun account(); fun more(); fun legalWork()
    }

    enum class Tab { HOME, LAWS, AI, DOCUMENTS, ACCOUNT, MORE, LEGAL_WORK }

    fun bottomNav(ui: GaUi, nav: Nav, selected: Tab): View {
        val fourth = if (selected == Tab.LEGAL_WORK) GaUi.NavItem("legal_work", "Legal Work", R.drawable.ga_ic_description) { nav.legalWork() }
        else GaUi.NavItem("documents", "Documents", R.drawable.ga_ic_description) { nav.documents() }
        val fifth = if (selected == Tab.MORE) GaUi.NavItem("more", "More", R.drawable.ga_ic_menu) { nav.more() }
        else GaUi.NavItem("account", "Account", R.drawable.ga_ic_person) { nav.account() }
        val key = when (selected) { Tab.HOME -> "home"; Tab.LAWS -> "laws"; Tab.AI -> "ai"; Tab.DOCUMENTS -> "documents"; Tab.ACCOUNT -> "account"; Tab.MORE -> "more"; Tab.LEGAL_WORK -> "legal_work" }
        return ui.bottomNav(listOf(
            GaUi.NavItem("home", "Home", R.drawable.ga_ic_home) { nav.home() },
            GaUi.NavItem("laws", "Laws", R.drawable.ga_ic_balance) { nav.laws() },
            GaUi.NavItem("ai", "AI Help", R.drawable.ga_ic_sms) { nav.aiHelp() },
            fourth, fifth), key, large = true)
    }

    /** Header + title + subtitle + scrolling body + bottom nav. Returns (root view, body). */
    fun page(ui: GaUi, nav: Nav, tab: Tab, title: String, subtitle: String?): Pair<View, LinearLayout> {
        val (root, body) = ui.screen({ nav.menu() }, bottomNav(ui, nav, tab))
        body.addView(ui.title(title))
        if (!subtitle.isNullOrBlank()) body.addView(ui.subtitle(subtitle))
        return root to body
    }

    // ---------------- Drawer ----------------
    fun drawerIcon(id: String) = when (id) {
        "home" -> R.drawable.ga_ic_home; "cases" -> R.drawable.ga_ic_folder; "ai" -> R.drawable.ga_ic_sms
        "laws" -> R.drawable.ga_ic_balance; "motions" -> R.drawable.ga_ic_edit_square; "forms" -> R.drawable.ga_ic_description
        "court" -> R.drawable.ga_ic_account_balance; "rights" -> R.drawable.ga_ic_groups; "resources" -> R.drawable.ga_ic_support
        "emergency" -> R.drawable.ga_ic_warning; "payments" -> R.drawable.ga_ic_payments; "settings" -> R.drawable.ga_ic_settings
        "profile" -> R.drawable.ga_ic_person; "loopholes" -> R.drawable.ga_ic_search; "charges" -> R.drawable.ga_ic_error; "help" -> R.drawable.ga_ic_help; else -> R.drawable.ga_ic_info
    }

    fun drawer(ui: GaUi, items: List<HomeDrawerItem>, versionName: String, onSelect: (HomeDrawerItem) -> Unit, onClose: () -> Unit): View {
        val dp = ui::dp
        val overlay = FrameLayout(ui.context).apply { setBackgroundColor(Color.argb(150, 0, 0, 0)); isClickable = true; setOnClickListener { onClose() } }
        val panel = LinearLayout(ui.context).apply {
            orientation = LinearLayout.VERTICAL; isClickable = true
            background = android.graphics.drawable.LayerDrawable(arrayOf(ui.screenBackground(), GradientDrawable().apply { setColor(Color.TRANSPARENT); setStroke(dp(1), ui.withAlpha(GaUi.BLUE, 120)) }))
        }
        val head = FrameLayout(ui.context)
        head.addView(ui.icon(R.drawable.ga_ic_menu, GaUi.BLUE_BRIGHT, 30), FrameLayout.LayoutParams(dp(30), dp(30), Gravity.START or Gravity.TOP).apply { setMargins(dp(16), dp(18), 0, 0) })
        head.addView(ui.icon(R.drawable.ga_ic_close, GaUi.WHITE, 30).apply { contentDescription = "Close menu"; setOnClickListener { onClose() } }, FrameLayout.LayoutParams(dp(30), dp(30), Gravity.END or Gravity.TOP).apply { setMargins(0, dp(18), dp(16), 0) })
        val pw = ui.context.resources.displayMetrics.widthPixels * 0.86f
        head.addView(ui.ladyJustice(), FrameLayout.LayoutParams((pw * 0.56f).toInt(), (pw * 0.42f).toInt(), Gravity.CENTER_HORIZONTAL or Gravity.TOP).apply { topMargin = (pw * 0.03f).toInt() })
        head.addView(ui.brandLockup(), FrameLayout.LayoutParams((pw * 0.84f).toInt(), (pw * 0.84f * 178f / 796f).toInt(), Gravity.CENTER_HORIZONTAL or Gravity.TOP).apply { topMargin = (pw * 0.43f).toInt() })
        panel.addView(head, LinearLayout.LayoutParams(-1, (pw * 0.64f).toInt()))
        val list = LinearLayout(ui.context).apply { orientation = LinearLayout.VERTICAL; setPadding(dp(22), dp(10), dp(16), dp(16)) }
        items.forEach { item ->
            val red = item.id == "emergency"
            list.addView(LinearLayout(ui.context).apply {
                orientation = LinearLayout.HORIZONTAL; gravity = Gravity.CENTER_VERTICAL; isClickable = true; contentDescription = item.label
                setOnClickListener { onSelect(item) }
                addView(ui.icon(drawerIcon(item.id), if (red) Color.rgb(255, 82, 82) else GaUi.TEXT, 24), LinearLayout.LayoutParams(dp(24), dp(24)).apply { rightMargin = dp(20) })
                addView(ui.text(item.label, 16.5f, if (red) Color.rgb(255, 82, 82) else GaUi.TEXT))
            }, LinearLayout.LayoutParams(-1, dp(46)))
        }
        list.addView(ui.text("Version $versionName", 13f, GaUi.MUTED, null, Gravity.CENTER).apply { setPadding(0, dp(14), 0, 0) })
        panel.addView(ScrollView(ui.context).apply { addView(list) }, LinearLayout.LayoutParams(-1, 0, 1f))
        val width = (ui.context.resources.displayMetrics.widthPixels * 0.86f).toInt()
        overlay.addView(panel, FrameLayout.LayoutParams(width, -1, Gravity.START))
        return overlay
    }

    // ---------------- Talk to Me ----------------
    class Chat(val root: View, val messages: LinearLayout, val input: EditText, private val ui: GaUi, private val scroll: ScrollView) {
        fun bot(text: String, time: String) = add(text, time, false)
        fun user(text: String, time: String) = add(text, time, true)
        /** Append an extra card (e.g. the lawyer take) under the latest answer. */
        fun attach(v: View) { messages.addView(v, ui.lp(8, 2)); scroll.post { scroll.fullScroll(View.FOCUS_DOWN) } }
        /** Share / Copy row under the latest answer. */
        fun actions(onShare: () -> Unit, onCopy: () -> Unit) { messages.addView(shareRow(ui, onShare, onCopy, indent = true)); scroll.post { scroll.fullScroll(View.FOCUS_DOWN) } }
        private fun add(text: String, time: String, mine: Boolean) {
            val dp = ui::dp
            val row = LinearLayout(ui.context).apply { orientation = LinearLayout.HORIZONTAL; gravity = if (mine) Gravity.END else Gravity.START }
            if (!mine) {
                val avatar = FrameLayout(ui.context).apply {
                    background = GradientDrawable().apply { shape = GradientDrawable.OVAL; colors = intArrayOf(Color.rgb(40, 140, 255), Color.rgb(12, 80, 200)); setStroke(dp(2), Color.rgb(120, 190, 255)) }
                    addView(ui.icon(R.drawable.ga_ic_support_agent, GaUi.WHITE, 22), FrameLayout.LayoutParams(dp(22), dp(22), Gravity.CENTER))
                }
                row.addView(avatar, LinearLayout.LayoutParams(dp(38), dp(38)).apply { rightMargin = dp(10) })
            }
            val bubble = ui.text(text, 15f, GaUi.TEXT).apply {
                setPadding(dp(14), dp(11), dp(14), dp(11)); setLineSpacing(0f, 1.15f); setTextIsSelectable(true)
                background = if (mine) ui.glowCard(Color.argb(235, 14, 34, 58), GaUi.STROKE_SOFT, 12, glow = false) else ui.glowCard(Color.argb(235, 12, 40, 72), GaUi.STROKE, 12, glow = false)
            }
            row.addView(bubble, LinearLayout.LayoutParams(0, -2, 1f).apply { if (mine) leftMargin = dp(56) })
            messages.addView(row, LinearLayout.LayoutParams(-1, -2).apply { topMargin = dp(10) })
            messages.addView(ui.text(time, 11f, GaUi.MUTED, null, if (mine) Gravity.END else Gravity.START).apply { setPadding(if (mine) 0 else dp(48), dp(4), dp(4), 0) })
            scroll.post { scroll.fullScroll(View.FOCUS_DOWN) }
        }
    }

    fun talkToMe(ui: GaUi, nav: Nav, onSend: (String) -> Unit, chips: List<Pair<String, () -> Unit>>): Chat =
        chatScreen(ui, nav, Tab.AI, "Talk to Me", "Get trusted legal information, case analysis, and step-by-step guidance.", "Type your question...", onSend, chips)

    /** Case Chat uses the same mockup chat layout as Talk to Me, scoped to one saved case. */
    fun caseChat(ui: GaUi, nav: Nav, caseTitle: String, onSend: (String) -> Unit, chips: List<Pair<String, () -> Unit>>): Chat =
        chatScreen(ui, nav, Tab.DOCUMENTS, "Case Chat", (if (caseTitle.isNotBlank()) "$caseTitle · " else "") + "Answers use your case file and verified Georgia authority only.", "Ask about this case...", onSend, chips)

    /** Share · Copy text actions (blue, small) used under answers and loophole results. */
    fun shareRow(ui: GaUi, onShare: () -> Unit, onCopy: () -> Unit, indent: Boolean = false): View = LinearLayout(ui.context).apply {
        orientation = LinearLayout.HORIZONTAL; gravity = Gravity.CENTER_VERTICAL; setPadding(if (indent) ui.dp(48) else 0, ui.dp(6), 0, ui.dp(2))
        fun action(label: String, f: () -> Unit) = ui.text(label, 13.5f, Color.rgb(60, 190, 255), ui.sansMedium).apply { setPadding(0, ui.dp(4), ui.dp(18), ui.dp(4)); isClickable = true; contentDescription = label; setOnClickListener { f() } }
        addView(action("Share") { onShare() }); addView(action("Copy") { onCopy() })
    }

    private fun chatScreen(ui: GaUi, nav: Nav, tab: Tab, title: String, subtitle: String, hintText: String, onSend: (String) -> Unit, chips: List<Pair<String, () -> Unit>>): Chat {
        val dp = ui::dp
        val shell = LinearLayout(ui.context).apply { orientation = LinearLayout.VERTICAL; background = ui.screenBackground() }
        shell.addView(ui.pageHeader { nav.menu() })
        val body = LinearLayout(ui.context).apply { orientation = LinearLayout.VERTICAL; setPadding(dp(18), dp(4), dp(18), dp(12)) }
        body.addView(ui.title(title))
        body.addView(ui.subtitle(subtitle))
        val messages = LinearLayout(ui.context).apply { orientation = LinearLayout.VERTICAL }
        body.addView(messages)
        val scroll = ScrollView(ui.context).apply { isFillViewport = true; addView(body) }
        shell.addView(scroll, LinearLayout.LayoutParams(-1, 0, 1f))
        val chipRow = LinearLayout(ui.context).apply { orientation = LinearLayout.HORIZONTAL; setPadding(dp(16), dp(6), dp(16), dp(8)) }
        chips.forEachIndexed { i, (label, action) ->
            chipRow.addView(ui.fit(ui.text(label, 13.5f, GaUi.TEXT, null, Gravity.CENTER).apply {
                background = ui.rounded(Color.argb(220, 10, 26, 45), 20, GaUi.STROKE_SOFT, 1.2f); setPadding(dp(10), dp(9), dp(10), dp(9)); isClickable = true; setOnClickListener { action() }
            }, 9, 13), LinearLayout.LayoutParams(-2, -2).apply { if (i > 0) leftMargin = dp(8) })
        }
        shell.addView(android.widget.HorizontalScrollView(ui.context).apply { isHorizontalScrollBarEnabled = false; addView(chipRow) })
        val inputRow = LinearLayout(ui.context).apply {
            orientation = LinearLayout.HORIZONTAL; background = ui.glowCard(Color.argb(220, 8, 22, 40), GaUi.STROKE, 10, glow = false)
        }
        val input = android.widget.EditText(ui.context).apply {
            hint = hintText; setHintTextColor(GaUi.MUTED); setTextColor(GaUi.WHITE); textSize = 15.5f; background = null
            setPadding(dp(16), dp(12), dp(8), dp(12)); maxLines = 4
        }
        inputRow.addView(input, LinearLayout.LayoutParams(0, -1, 1f))
        val send = FrameLayout(ui.context).apply {
            background = GradientDrawable(GradientDrawable.Orientation.TOP_BOTTOM, intArrayOf(Color.rgb(38, 132, 255), Color.rgb(13, 86, 214))).apply { cornerRadii = floatArrayOf(0f, 0f, ui.dpf(10f), ui.dpf(10f), ui.dpf(10f), ui.dpf(10f), 0f, 0f) }
            contentDescription = "Send"; isClickable = true
            addView(ui.icon(R.drawable.ga_ic_chevron_right, GaUi.WHITE, 34), FrameLayout.LayoutParams(dp(34), dp(34), Gravity.CENTER))
            setOnClickListener { val q = input.text.toString().trim(); if (q.isNotEmpty()) onSend(q) }
        }
        inputRow.addView(send, LinearLayout.LayoutParams(dp(56), -1))
        shell.addView(inputRow, LinearLayout.LayoutParams(-1, dp(54)).apply { setMargins(dp(16), 0, dp(16), dp(10)) })
        shell.addView(bottomNav(ui, nav, tab))
        return Chat(shell, messages, input, ui, scroll)
    }

    // ---------------- My Cases ----------------
    data class CaseRow(val id: Int, val title: String, val county: String, val type: String, val stage: String)

    fun isClosed(stage: String) = Regex("closed|dismiss|resolved|acquit|complete", RegexOption.IGNORE_CASE).containsMatchIn(stage)

    fun myCases(ui: GaUi, nav: Nav, cases: List<CaseRow>?, filter: Int, query: String, onFilter: (Int) -> Unit, onQuery: (String) -> Unit, onOpen: (Int) -> Unit, onAdd: () -> Unit): View {
        val dp = ui::dp
        val (root, body) = page(ui, nav, Tab.LAWS, "My Cases", "Manage and track all your cases in one place.")
        val searchRow = LinearLayout(ui.context).apply { orientation = LinearLayout.HORIZONTAL; gravity = Gravity.CENTER_VERTICAL }
        val (search, field) = ui.searchField("Search cases...", glowing = false, height = 50, showButton = false) { onQuery(it) }
        field.setText(query)
        searchRow.addView(search, LinearLayout.LayoutParams(0, dp(50), 1f))
        searchRow.addView(FrameLayout(ui.context).apply {
            background = ui.glowCard(Color.argb(200, 8, 22, 40), GaUi.STROKE_SOFT, 12, glow = false); contentDescription = "Filter"; isClickable = true; setOnClickListener { onQuery(field.text.toString()) }
            addView(ui.icon(R.drawable.ga_ic_filter_alt, GaUi.TEXT, 24), FrameLayout.LayoutParams(dp(24), dp(24), Gravity.CENTER))
        }, LinearLayout.LayoutParams(dp(50), dp(50)).apply { leftMargin = dp(10) })
        body.addView(searchRow)
        body.addView(ui.tabs(listOf("All", "Active", "Closed", "Favorites"), filter, onFilter, underline = true), ui.lp(14, 10, dp(48)))
        when {
            cases == null -> body.addView(ui.note("Loading your cases…"))
            else -> {
                val q = query.trim().lowercase()
                val shown = cases.filter { c ->
                    (q.isEmpty() || listOf(c.title, c.county, c.type, c.stage).any { it.lowercase().contains(q) }) && when (filter) {
                        1 -> !isClosed(c.stage); 2 -> isClosed(c.stage); 3 -> false; else -> true
                    }
                }
                if (shown.isEmpty()) body.addView(ui.emptyCard(R.drawable.ga_ic_folder,
                    when { filter == 3 -> "No favorite cases yet"; cases.isEmpty() -> "No cases yet"; else -> "No matching cases" },
                    when { filter == 3 -> "Favorites are coming soon."; cases.isEmpty() -> "Tap Add New Case to create your first case file."; else -> "Try a different search or filter." }), ui.lp(6, 6))
                shown.forEach { c ->
                    val card = LinearLayout(ui.context).apply {
                        orientation = LinearLayout.HORIZONTAL; gravity = Gravity.CENTER_VERTICAL; setPadding(dp(16), dp(14), dp(12), dp(14))
                        background = ui.glowCard(GaUi.CARD, GaUi.STROKE_SOFT, 12, glow = false); isClickable = true; setOnClickListener { onOpen(c.id) }
                        addView(ui.icon(R.drawable.ga_ic_description, GaUi.GOLD, 30), LinearLayout.LayoutParams(dp(30), dp(30)).apply { rightMargin = dp(16) })
                        val col = LinearLayout(ui.context).apply { orientation = LinearLayout.VERTICAL }
                        col.addView(ui.text(c.title, 17f, GaUi.WHITE, ui.sansMedium))
                        val meta = listOf(c.county.ifBlank { "County not set" }, c.type.replaceFirstChar { it.uppercase() }).filter { it.isNotBlank() }.joinToString("  |  ")
                        col.addView(ui.text(meta, 14f, Color.rgb(120, 175, 235)).apply { setPadding(0, dp(3), 0, 0) })
                        if (c.stage.isNotBlank()) col.addView(ui.text("Stage: ${c.stage}", 14f, Color.rgb(120, 175, 235)).apply { setPadding(0, dp(2), 0, 0) })
                        addView(col, LinearLayout.LayoutParams(0, -2, 1f))
                        addView(ui.icon(R.drawable.ga_ic_chevron_right, GaUi.TEXT, 24))
                    }
                    body.addView(card, ui.lp(6, 6))
                }
            }
        }
        body.addView(ui.primaryButton("+  Add New Case") { onAdd() }.apply { textSize = 18f }, ui.lp(14, 4))
        return root
    }

    // ---------------- Documents ----------------
    data class DocRow(val caseId: Int, val caseTitle: String, val name: String, val mediaType: String, val date: String, val size: String)

    fun documents(ui: GaUi, nav: Nav, tab: Int, docs: List<DocRow>?, onTab: (Int) -> Unit, onUpload: () -> Unit, onSort: () -> Unit, onDoc: (DocRow) -> Unit): View {
        val dp = ui::dp
        val (root, body) = page(ui, nav, Tab.DOCUMENTS, "Documents", "Upload, organize, and manage your legal files.")
        body.addView(ui.tabs(listOf("My Documents", "Shared", "Templates"), tab, onTab), ui.lp(0, 14, dp(46)))
        if (tab != 0) {
            body.addView(ui.emptyCard(if (tab == 1) R.drawable.ga_ic_groups else R.drawable.ga_ic_library_books,
                if (tab == 1) "Shared documents — coming soon" else "Templates — coming soon",
                if (tab == 1) "Sharing files with an attorney or helper is not available yet." else "Court-ready templates are not available yet. Use Legal Forms for official Georgia forms."), ui.lp(4, 4))
            return root
        }
        val upload = LinearLayout(ui.context).apply {
            orientation = LinearLayout.VERTICAL; gravity = Gravity.CENTER; setPadding(dp(12), dp(22), dp(12), dp(22)); isClickable = true; setOnClickListener { onUpload() }
            contentDescription = "Tap to Upload Documents"
            background = ShapeDrawable(RoundRectShape(FloatArray(8) { ui.dpf(12f) }, null, null)).apply {
                paint.color = GaUi.BLUE; paint.style = Paint.Style.STROKE; paint.strokeWidth = ui.dpf(1.4f); paint.pathEffect = DashPathEffect(floatArrayOf(ui.dpf(6f), ui.dpf(5f)), 0f)
            }
            addView(ui.icon(R.drawable.ga_ic_cloud_upload, GaUi.BLUE_BRIGHT, 64))
            addView(ui.text("Tap to Upload Documents", 18f, GaUi.BLUE_BRIGHT, ui.sansMedium, Gravity.CENTER).apply { setPadding(0, dp(6), 0, dp(6)) })
            addView(ui.text("Supports PDF, DOC, DOCX, JPG, PNG, etc.", 14f, GaUi.MUTED, null, Gravity.CENTER))
        }
        body.addView(upload, LinearLayout.LayoutParams(-1, -2).apply { setMargins(dp(2), 0, dp(2), dp(8)) })
        val head = LinearLayout(ui.context).apply { orientation = LinearLayout.HORIZONTAL; gravity = Gravity.CENTER_VERTICAL }
        head.addView(ui.sectionHeader("My Documents"), LinearLayout.LayoutParams(0, -2, 1f))
        head.addView(LinearLayout(ui.context).apply {
            orientation = LinearLayout.HORIZONTAL; gravity = Gravity.CENTER_VERTICAL; isClickable = true; setOnClickListener { onSort() }
            addView(ui.icon(R.drawable.ga_ic_swap_vert, GaUi.BLUE_BRIGHT, 20)); addView(ui.text(" Sort", 15f, GaUi.BLUE_BRIGHT))
        })
        body.addView(head)
        when {
            docs == null -> body.addView(ui.note("Loading your documents…"))
            docs.isEmpty() -> body.addView(ui.emptyCard(R.drawable.ga_ic_description, "No documents yet", "Upload a PDF, photo or document to keep it with your case."), ui.lp(4, 4))
            else -> docs.forEach { d ->
                val isImage = d.mediaType.startsWith("image/")
                val isPdf = d.mediaType.contains("pdf") || d.name.lowercase().endsWith(".pdf")
                body.addView(LinearLayout(ui.context).apply {
                    orientation = LinearLayout.HORIZONTAL; gravity = Gravity.CENTER_VERTICAL; setPadding(dp(14), dp(12), dp(6), dp(12))
                    background = ui.glowCard(GaUi.CARD, GaUi.STROKE_SOFT, 12, glow = false); isClickable = true; setOnClickListener { onDoc(d) }
                    addView(ui.icon(if (isImage) R.drawable.ga_ic_image else R.drawable.ga_ic_description, if (isPdf) Color.rgb(240, 80, 80) else GaUi.BLUE_BRIGHT, 30), LinearLayout.LayoutParams(dp(30), dp(30)).apply { rightMargin = dp(14) })
                    val col = LinearLayout(ui.context).apply { orientation = LinearLayout.VERTICAL }
                    col.addView(ui.text(d.name, 16f, GaUi.WHITE).apply { maxLines = 1; ellipsize = android.text.TextUtils.TruncateAt.MIDDLE })
                    col.addView(ui.text(listOf(d.date, d.size).filter { it.isNotBlank() }.joinToString(" • "), 13.5f, GaUi.MUTED).apply { setPadding(0, dp(2), 0, 0) })
                    addView(col, LinearLayout.LayoutParams(0, -2, 1f))
                    addView(ui.icon(R.drawable.ga_ic_more_vert, GaUi.TEXT, 24))
                }, ui.lp(5, 5))
            }
        }
        return root
    }

    // ---------------- Emergency ----------------
    data class Row(val icon: Int, val title: String, val subtitle: String, val action: () -> Unit)

    fun emergency(ui: GaUi, nav: Nav, on911: () -> Unit, rows: List<Row>): View {
        val dp = ui::dp
        val (root, body) = page(ui, nav, Tab.MORE, "Emergency Information", "Get immediate help and important resources.")
        val card = LinearLayout(ui.context).apply {
            orientation = LinearLayout.HORIZONTAL; gravity = Gravity.CENTER_VERTICAL; setPadding(dp(18), dp(14), dp(12), dp(14)); isClickable = true; setOnClickListener { on911() }
            contentDescription = "Call 911"
            val fill = GradientDrawable(GradientDrawable.Orientation.LEFT_RIGHT, intArrayOf(Color.rgb(160, 20, 28), Color.rgb(110, 12, 20))).apply { cornerRadius = ui.dpf(12f); setStroke(dp(1), Color.rgb(255, 100, 104)) }
            background = android.graphics.drawable.LayerDrawable(arrayOf(ui.rounded(Color.TRANSPARENT, 15, ui.withAlpha(GaUi.RED, 90), 3f), fill)).apply { setLayerInset(1, dp(3), dp(3), dp(3), dp(3)) }
            addView(ui.icon(R.drawable.ga_ic_call, Color.rgb(255, 200, 200), 34), LinearLayout.LayoutParams(dp(34), dp(34)).apply { rightMargin = dp(12) })
            addView(ui.text("911", 30f, GaUi.WHITE, ui.sansBold).apply { setPadding(0, 0, dp(16), 0) })
            val col = LinearLayout(ui.context).apply { orientation = LinearLayout.VERTICAL }
            col.addView(ui.text("EMERGENCY", 17f, GaUi.WHITE, ui.sansBold)); col.addView(ui.text("Police, Fire, Medical", 14f, Color.rgb(250, 214, 216)))
            addView(col, LinearLayout.LayoutParams(0, -2, 1f))
            addView(ui.icon(R.drawable.ga_ic_chevron_right, GaUi.WHITE, 24))
        }
        body.addView(card, ui.lp(0, 6))
        rows.forEach { body.addView(ui.rowCard(it.icon, it.title, it.subtitle, GaUi.BLUE_BRIGHT, action = it.action), ui.lp(5, 5)) }
        body.addView(ui.note("GA.LAW.HELP provides legal information, not emergency dispatch or attorney representation."))
        return root
    }

    // ---------------- Motions & Legal Work ----------------
    fun motions(ui: GaUi, nav: Nav, rows: List<Row>): View {
        val (root, body) = page(ui, nav, Tab.LEGAL_WORK, "Motions & Legal Work", "Get help with motions, legal documents, and case strategy.")
        val tints = listOf(Color.rgb(236, 120, 200), Color.rgb(200, 130, 240), Color.rgb(160, 140, 255), Color.rgb(64, 170, 255))
        rows.forEachIndexed { i, r -> body.addView(ui.rowCard(r.icon, r.title, r.subtitle, tints[i % tints.size], iconSize = 40, action = r.action), ui.lp(6, 6)) }
        return root
    }

    // ---------------- Profile ----------------
    fun profile(ui: GaUi, nav: Nav, name: String, email: String, phone: String, onEditPhoto: () -> Unit, onUpdate: (String, String) -> Unit): View {
        val dp = ui::dp
        val (root, body) = page(ui, nav, Tab.ACCOUNT, "Profile", "Manage your account information.")
        val avatar = FrameLayout(ui.context).apply {
            background = android.graphics.drawable.LayerDrawable(arrayOf(
                GradientDrawable().apply { shape = GradientDrawable.OVAL; setColor(Color.TRANSPARENT); setStroke(dp(4), ui.withAlpha(GaUi.BLUE, 70)) },
                GradientDrawable().apply { shape = GradientDrawable.OVAL; setColor(Color.rgb(8, 24, 44)); setStroke(dp(2), GaUi.BLUE_BRIGHT) })).apply { setLayerInset(1, dp(3), dp(3), dp(3), dp(3)) }
            addView(ui.icon(R.drawable.ga_ic_person, GaUi.BLUE_BRIGHT, 64), FrameLayout.LayoutParams(dp(64), dp(64), Gravity.CENTER))
            isClickable = true; setOnClickListener { onEditPhoto() }
        }
        body.addView(avatar, LinearLayout.LayoutParams(dp(112), dp(112)).apply { gravity = Gravity.CENTER_HORIZONTAL; topMargin = dp(4) })
        body.addView(ui.text("Edit Photo", 13f, GaUi.BLUE_BRIGHT, null, Gravity.CENTER).apply { setPadding(0, dp(4), 0, dp(10)); setOnClickListener { onEditPhoto() } })
        val (nameBox, nameField) = ui.labeledInput("Full Name", "Your name", name)
        val (emailBox, emailField) = ui.labeledInput("Email", "Email", email)
        emailField.isEnabled = false; emailField.setTextColor(GaUi.TEXT)
        val (phoneBox, phoneField) = ui.labeledInput("Phone Number", "Optional", phone)
        phoneField.inputType = android.text.InputType.TYPE_CLASS_PHONE
        listOf(nameBox, emailBox, phoneBox).forEach { body.addView(it, ui.lp(6, 6)) }
        body.addView(ui.primaryButton("Update Profile") { onUpdate(nameField.text.toString().trim(), phoneField.text.toString().trim()) }, ui.lp(14, 4))
        body.addView(ui.note("Name and phone are saved only on this device. Your sign-in email is managed by your GA.LAW.HELP account."))
        return root
    }

    // ---------------- Settings ----------------
    fun settings(ui: GaUi, nav: Nav, darkMode: Boolean, onRow: (Int) -> Unit): View {
        val (root, body) = page(ui, nav, Tab.MORE, "Settings", "Customize your app experience.")
        body.addView(ui.settingsList(listOf(
            Triple(R.drawable.ga_ic_language, "Language", null),
            Triple(R.drawable.ga_ic_dark_mode, "Dark Mode", ui.toggle(darkMode)),
            Triple(R.drawable.ga_ic_notifications, "Notifications", null),
            Triple(R.drawable.ga_ic_lock, "Privacy & Security", null),
            Triple(R.drawable.ga_ic_delete, "Clear App Data", null),
            Triple(R.drawable.ga_ic_info, "About GA.LAW.HELP", null)), onRow), ui.lp(2, 8))
        return root
    }

    // ---------------- Payment & Subscription ----------------
    fun payment(ui: GaUi, nav: Nav, planName: String, priceLine: String, features: List<String>, onManage: () -> Unit, onPayment: () -> Unit, onHistory: () -> Unit): View {
        val dp = ui::dp
        val (root, body) = page(ui, nav, Tab.ACCOUNT, "Payment & Subscription", "Manage your plan and billing.")
        val card = LinearLayout(ui.context).apply { orientation = LinearLayout.VERTICAL; setPadding(dp(20), dp(16), dp(18), dp(18)); background = ui.glowCard(Color.argb(235, 12, 32, 56), GaUi.STROKE, 14) }
        val top = LinearLayout(ui.context).apply { orientation = LinearLayout.HORIZONTAL; gravity = Gravity.TOP }
        val col = LinearLayout(ui.context).apply { orientation = LinearLayout.VERTICAL }
        col.addView(ui.text("Current Plan", 14f, GaUi.MUTED))
        col.addView(ui.text(planName, 26f, GaUi.BLUE_BRIGHT, ui.sansBold))
        col.addView(ui.text(priceLine, 18f, GaUi.BLUE_BRIGHT, ui.sansMedium).apply { setPadding(0, dp(2), 0, dp(8)) })
        top.addView(col, LinearLayout.LayoutParams(0, -2, 1f))
        top.addView(ui.text("Active", 14f, GaUi.WHITE, ui.sansMedium, Gravity.CENTER).apply { background = ui.rounded(Color.rgb(22, 120, 70), 16, GaUi.GREEN, 1f); setPadding(dp(16), dp(5), dp(16), dp(5)) })
        card.addView(top)
        features.forEach { f ->
            card.addView(LinearLayout(ui.context).apply {
                orientation = LinearLayout.HORIZONTAL; gravity = Gravity.CENTER_VERTICAL; setPadding(0, dp(4), 0, dp(4))
                addView(ui.icon(R.drawable.ga_ic_check, GaUi.GREEN, 22), LinearLayout.LayoutParams(dp(22), dp(22)).apply { rightMargin = dp(12) })
                addView(ui.text(f, 15f, GaUi.TEXT))
            })
        }
        body.addView(card, ui.lp(2, 10))
        body.addView(ui.primaryButton("Manage Subscription") { onManage() }, ui.lp(6, 4))
        body.addView(ui.secondaryButton("Update Payment Method") { onPayment() }, ui.lp(6, 4))
        body.addView(ui.secondaryButton("View Billing History") { onHistory() }, ui.lp(6, 4))
        return root
    }

    // ---------------- More ----------------
    fun more(ui: GaUi, nav: Nav, onRow: (Int) -> Unit, onSignOut: (() -> Unit)?): View {
        val (root, body) = page(ui, nav, Tab.MORE, "More", "Additional tools and information.")
        body.addView(ui.settingsList(listOf(
            Triple(R.drawable.ga_ic_diversity_3, "Legal Aid Organizations", null),
            Triple(R.drawable.ga_ic_location_on, "Court Locations", null),
            Triple(R.drawable.ga_ic_help, "Frequently Asked Questions", null),
            Triple(R.drawable.ga_ic_info, "App Tutorial", null),
            Triple(R.drawable.ga_ic_description, "Terms of Service", null),
            Triple(R.drawable.ga_ic_privacy_tip, "Privacy Policy", null),
            Triple(R.drawable.ga_ic_support_agent, "Contact Support", null)), onRow), ui.lp(2, 8))
        if (onSignOut != null) body.addView(ui.primaryButton("Sign Out") { onSignOut() }.apply { textSize = 18f }, ui.lp(16, 4))
        return root
    }

    // ---------------- Coming soon ----------------
    fun comingSoon(ui: GaUi, nav: Nav, tab: Tab, title: String, body: String, onBack: () -> Unit): View {
        val (root, content) = page(ui, nav, tab, title, null)
        content.addView(ui.emptyCard(R.drawable.ga_ic_info, "Coming soon", body), ui.lp(8, 12))
        content.addView(ui.secondaryButton("Go back") { onBack() }, ui.lp(4, 4))
        return root
    }

    // ---------------- Georgia Laws ----------------
    class LawsForm(val root: View, val search: EditText, val keyword: EditText, val results: LinearLayout)

    fun georgiaLaws(ui: GaUi, nav: Nav, tab: Int, titleLabel: String, chapterLabel: String, recent: List<String>,
                    onTab: (Int) -> Unit, onTitle: () -> Unit, onChapter: () -> Unit, onSearch: () -> Unit, onRecent: (String) -> Unit): LawsForm {
        val dp = ui::dp
        val (root, body) = page(ui, nav, Tab.LAWS, "Georgia Laws", "Search Georgia statutes, rules, and case law.")
        body.addView(ui.tabs(listOf("Statutes", "Case Law", "Court Rules"), tab, onTab), ui.lp(0, 12, dp(46)))
        val (searchBox, search) = ui.searchField(when (tab) { 1 -> "Search Georgia case law..."; 2 -> "Search Georgia court rules..."; else -> "Search Georgia statutes..." }, glowing = false, height = 50, showButton = false) { onSearch() }
        body.addView(searchBox, ui.lp(0, 12, dp(50)))
        if (tab == 0) {
            val labels = LinearLayout(ui.context).apply { orientation = LinearLayout.HORIZONTAL }
            labels.addView(ui.text("Title", 14f, GaUi.TEXT), LinearLayout.LayoutParams(0, -2, 1f))
            labels.addView(ui.text("Chapter", 14f, GaUi.TEXT).apply { setPadding(dp(10), 0, 0, 0) }, LinearLayout.LayoutParams(0, -2, 1f))
            body.addView(labels)
            val drops = LinearLayout(ui.context).apply { orientation = LinearLayout.HORIZONTAL }
            drops.addView(ui.dropdown(titleLabel) { onTitle() }, LinearLayout.LayoutParams(0, dp(46), 1f).apply { rightMargin = dp(6) })
            drops.addView(ui.dropdown(chapterLabel) { onChapter() }, LinearLayout.LayoutParams(0, dp(46), 1f).apply { leftMargin = dp(6) })
            body.addView(drops, ui.lp(6, 10))
        }
        body.addView(ui.text("Keyword (optional)", 14f, GaUi.TEXT))
        val keyword = ui.input("Enter keyword...")
        body.addView(keyword, ui.lp(6, 12, dp(48)))
        body.addView(ui.primaryButton("Search Laws") { onSearch() }, ui.lp(2, 8))
        val results = LinearLayout(ui.context).apply { orientation = LinearLayout.VERTICAL }
        body.addView(results)
        if (recent.isNotEmpty()) {
            body.addView(ui.sectionHeader("Recent Searches"))
            recent.forEach { r ->
                body.addView(LinearLayout(ui.context).apply {
                    orientation = LinearLayout.HORIZONTAL; gravity = Gravity.CENTER_VERTICAL; setPadding(dp(16), dp(12), dp(14), dp(12))
                    background = ui.glowCard(GaUi.CARD, GaUi.STROKE_SOFT, 10, glow = false); isClickable = true; setOnClickListener { onRecent(r) }
                    addView(ui.text(r, 15f, GaUi.TEXT).apply { maxLines = 1; ellipsize = android.text.TextUtils.TruncateAt.END }, LinearLayout.LayoutParams(0, -2, 1f))
                    addView(ui.text("Search again", 15f, Color.rgb(60, 190, 255)))
                }, ui.lp(4, 4))
            }
        }
        return LawsForm(root, search, keyword, results)
    }

    data class LawHit(val citation: String, val title: String, val type: String, val excerpt: String, val sourceUrl: String?)

    fun renderLawResults(ui: GaUi, container: LinearLayout, hits: List<LawHit>?, message: String?, onOpen: (LawHit) -> Unit) {
        val dp = ui::dp
        container.removeAllViews()
        if (message != null) container.addView(ui.note(message))
        if (hits == null) return
        container.addView(ui.sectionHeader("Results (${hits.size})"))
        if (hits.isEmpty()) container.addView(ui.emptyCard(R.drawable.ga_ic_search, "No matching Georgia law found", "Try other words, or a citation such as 16-11-131. GA.LAW.HELP never invents a citation."), ui.lp(4, 4))
        hits.forEach { h ->
            container.addView(LinearLayout(ui.context).apply {
                orientation = LinearLayout.VERTICAL; setPadding(dp(14), dp(12), dp(14), dp(12)); background = ui.glowCard(GaUi.CARD, GaUi.STROKE_SOFT, 12, glow = false)
                isClickable = true; setOnClickListener { onOpen(h) }
                addView(ui.text(when (h.type.lowercase()) { "statute" -> "GEORGIA STATUTE"; "regulation" -> "GEORGIA REGULATION"; "court_rule" -> "COURT RULE"; "case_law", "case", "opinion" -> "GEORGIA CASE"; else -> h.type.uppercase() }, 11f, GaUi.BLUE_BRIGHT, ui.sansBold))
                addView(ui.text(h.citation, 15f, GaUi.GOLD, ui.sansMedium).apply { setPadding(0, dp(3), 0, dp(2)) })
                if (h.title.isNotBlank() && h.title != h.citation) addView(ui.text(h.title.removePrefix(h.citation).trimStart('.', ' '), 15f, GaUi.WHITE))
                if (h.excerpt.isNotBlank()) addView(ui.text(h.excerpt, 13f, GaUi.MUTED).apply { maxLines = 4; ellipsize = android.text.TextUtils.TruncateAt.END; setPadding(0, dp(4), 0, 0) })
                if (h.sourceUrl != null) addView(ui.text("Open official source ›", 13.5f, Color.rgb(60, 190, 255)).apply { setPadding(0, dp(6), 0, 0) })
            }, ui.lp(5, 5))
        }
    }

    // ---------------- Legal Loopholes ----------------
    class LoopholesForm(val root: View, val topic: EditText, val results: LinearLayout)
    data class LoopholeCite(val citation: String, val title: String, val sourceUrl: String?)
    data class LoopholeFinding(val typeLabel: String, val title: String, val explanation: String, val citations: List<LoopholeCite>)
    data class LawyerTake(val label: String, val text: String, val disclaimer: String, val citations: List<LoopholeCite>)

    const val LOOPHOLE_DISCLAIMER = "This is legal information, not legal advice; talk to a Georgia attorney."

    fun loopholes(ui: GaUi, nav: Nav, chips: List<String>, onAnalyze: (String) -> Unit): LoopholesForm {
        val dp = ui::dp
        val (root, body) = page(ui, nav, Tab.LAWS, "Legal Loopholes", "Find contradictions, gaps, unclear wording and exceptions in Georgia law, cited to verified sources.")
        val (box, topic) = ui.searchField("Enter a topic, e.g. self-defense...", glowing = true, height = 52, showButton = false) { onAnalyze(it) }
        body.addView(box, ui.lp(0, 10, dp(52)))
        val chipRow = LinearLayout(ui.context).apply { orientation = LinearLayout.HORIZONTAL; setPadding(0, dp(2), 0, dp(8)) }
        chips.forEachIndexed { i, label ->
            chipRow.addView(ui.text(label, 13.5f, GaUi.TEXT, null, Gravity.CENTER).apply {
                background = ui.rounded(Color.argb(220, 10, 26, 45), 20, GaUi.STROKE_SOFT, 1.2f); setPadding(dp(12), dp(9), dp(12), dp(9)); isClickable = true
                setOnClickListener { topic.setText(label); onAnalyze(label) }
            }, LinearLayout.LayoutParams(-2, -2).apply { if (i > 0) leftMargin = dp(8) })
        }
        body.addView(android.widget.HorizontalScrollView(ui.context).apply { isHorizontalScrollBarEnabled = false; addView(chipRow) })
        body.addView(ui.primaryButton("Analyze the Law") { onAnalyze(topic.text.toString()) }, ui.lp(4, 8))
        val results = LinearLayout(ui.context).apply { orientation = LinearLayout.VERTICAL }
        body.addView(results)
        body.addView(ui.note(LOOPHOLE_DISCLAIMER))
        return LoopholesForm(root, topic, results)
    }

    fun loopholesLoading(ui: GaUi, container: LinearLayout) {
        container.removeAllViews()
        container.addView(LinearLayout(ui.context).apply {
            orientation = LinearLayout.HORIZONTAL; gravity = Gravity.CENTER_VERTICAL; setPadding(ui.dp(14), ui.dp(14), ui.dp(14), ui.dp(14))
            background = ui.glowCard(GaUi.CARD, GaUi.STROKE_SOFT, 12, glow = false)
            addView(android.widget.ProgressBar(ui.context).apply { indeterminateTintList = android.content.res.ColorStateList.valueOf(GaUi.GOLD) }, LinearLayout.LayoutParams(ui.dp(26), ui.dp(26)).apply { rightMargin = ui.dp(12) })
            addView(ui.text("Comparing verified Georgia laws and cases…", 14.5f, GaUi.TEXT))
        }, ui.lp(6, 6))
    }

    private fun citeViews(ui: GaUi, card: LinearLayout, cites: List<LoopholeCite>, onCite: (LoopholeCite) -> Unit) {
        cites.forEach { c ->
            card.addView(ui.text("${c.citation} ›", 13.5f, Color.rgb(60, 190, 255)).apply {
                setPadding(0, ui.dp(6), 0, 0); isClickable = true; contentDescription = "Open ${c.citation}"; setOnClickListener { onCite(c) }
            })
        }
    }

    const val COVERAGE_HINT = "GA.LAW.HELP is still adding Georgia laws and court opinions to its library, so more topics will have results soon. Try again later or try a related topic."

    fun renderLoopholes(ui: GaUi, container: LinearLayout, findings: List<LoopholeFinding>, message: String?, lawyer: LawyerTake?, refused: Boolean = false, share: Pair<() -> Unit, () -> Unit>? = null, onCite: (LoopholeCite) -> Unit) {
        val dp = ui::dp
        container.removeAllViews()
        container.addView(ui.sectionHeader("Findings (${findings.size})"))
        if (findings.isEmpty()) {
            val base = message ?: "No findings could be supported by verified Georgia sources. GA.LAW.HELP never invents a citation."
            if (refused) container.addView(ui.emptyCard(R.drawable.ga_ic_error, "Can’t help with that", base), ui.lp(4, 4))
            else container.addView(ui.emptyCard(R.drawable.ga_ic_search, "Nothing found yet", if (base.contains("still adding")) base else base + "\n\n" + COVERAGE_HINT), ui.lp(4, 4))
        }
        findings.forEach { f ->
            container.addView(LinearLayout(ui.context).apply {
                orientation = LinearLayout.VERTICAL; setPadding(dp(14), dp(12), dp(14), dp(12)); background = ui.glowCard(GaUi.CARD, GaUi.STROKE_SOFT, 12, glow = false)
                addView(ui.text(f.typeLabel.uppercase(), 11f, GaUi.BLUE_BRIGHT, ui.sansBold))
                addView(ui.text(f.title, 15.5f, GaUi.GOLD, ui.sansMedium).apply { setPadding(0, dp(3), 0, dp(3)) })
                addView(ui.text(f.explanation, 14f, GaUi.TEXT).apply { setLineSpacing(0f, 1.12f); setTextIsSelectable(true) })
                citeViews(ui, this, f.citations, onCite)
            }, ui.lp(5, 5))
        }
        if (lawyer != null) container.addView(lawyerCard(ui, lawyer, onCite), ui.lp(10, 6))
        if (share != null && (findings.isNotEmpty() || lawyer != null)) container.addView(shareRow(ui, share.first, share.second))
    }

    /** Gold "If I Was Your Lawyer, I Would Say" card shared by Legal Loopholes and Case Chat. */
    fun lawyerCard(ui: GaUi, lawyer: LawyerTake, onCite: (LoopholeCite) -> Unit): LinearLayout {
        val dp = ui::dp
        return LinearLayout(ui.context).apply {
            orientation = LinearLayout.VERTICAL; setPadding(dp(16), dp(14), dp(16), dp(14))
            background = ui.glowCard(Color.argb(235, 22, 30, 44), GaUi.GOLD, 14, glow = true)
            addView(ui.text(lawyer.label, 18f, GaUi.GOLD, ui.serifBold))
            addView(ui.text(lawyer.text, 14.5f, GaUi.WHITE).apply { setPadding(0, dp(8), 0, dp(4)); setLineSpacing(0f, 1.15f); setTextIsSelectable(true) })
            citeViews(ui, this, lawyer.citations, onCite)
            addView(ui.text(lawyer.disclaimer, 12.5f, GaUi.MUTED, ui.sansMedium).apply { setPadding(0, dp(10), 0, 0) })
        }
    }

    // ---------------- Charge Check ----------------
    class ChargeCheckForm(val root: View, val situation: EditText, val results: LinearLayout)
    data class ChargeItem(val charge: String, val levelLabel: String, val penalty: String?, val penaltyNote: String?, val why: String, val cite: LoopholeCite)
    data class ChargeOption(val label: String?, val title: String, val explanation: String, val citations: List<LoopholeCite>)
    data class ChargeCheckResult(
        val charges: List<ChargeItem>, val defenses: List<ChargeOption>, val lowest: List<ChargeOption>, val lawyer: LawyerTake?,
        val message: String?, val refused: Boolean, val estimateNote: String, val rightsReminder: String, val disclaimer: String,
        val emergency: List<Pair<String, String>>, val caseId: Int?
    )

    const val CHARGE_DISCLAIMER = "This is legal information, not legal advice. Talk to a Georgia criminal defense lawyer or public defender before you decide anything."

    fun chargeCheck(ui: GaUi, nav: Nav, caseTitle: String?, onCheck: (String) -> Unit): ChargeCheckForm {
        val (root, body) = page(ui, nav, Tab.LAWS, "Charge Check", "Describe what happened. See what Georgia charges could apply, possible defenses, and lawful ways to get the lowest outcome.")
        if (!caseTitle.isNullOrBlank()) body.addView(ui.text("Case: $caseTitle", 13.5f, GaUi.GOLD, ui.sansMedium), ui.lp(2, 4))
        val situation = ui.input("What happened? Where, when, what police said or found…", true).apply { minLines = 5 }
        body.addView(situation, ui.lp(8, 8))
        body.addView(ui.primaryButton("Check Possible Charges") { onCheck(situation.text.toString()) }, ui.lp(4, 8))
        body.addView(ui.note("Don’t talk to police about the case without a lawyer. If anyone is in danger, call 911."))
        val results = LinearLayout(ui.context).apply { orientation = LinearLayout.VERTICAL }
        body.addView(results)
        body.addView(ui.note(CHARGE_DISCLAIMER))
        return ChargeCheckForm(root, situation, results)
    }

    fun chargeCheckLoading(ui: GaUi, container: LinearLayout) {
        loopholesLoading(ui, container)
        ((container.getChildAt(0) as? LinearLayout)?.getChildAt(1) as? TextView)?.text = "Looking up Georgia Code sections…"
    }

    private fun optionCard(ui: GaUi, o: ChargeOption, onCite: (LoopholeCite) -> Unit) = LinearLayout(ui.context).apply {
        val dp = ui::dp
        orientation = LinearLayout.VERTICAL; setPadding(dp(14), dp(12), dp(14), dp(12)); background = ui.glowCard(GaUi.CARD, GaUi.STROKE_SOFT, 12, glow = false)
        if (!o.label.isNullOrBlank()) addView(ui.text(o.label.uppercase(), 11f, GaUi.BLUE_BRIGHT, ui.sansBold))
        addView(ui.text(o.title, 15.5f, GaUi.GOLD, ui.sansMedium).apply { setPadding(0, dp(3), 0, dp(3)) })
        addView(ui.text(o.explanation, 14f, GaUi.TEXT).apply { setLineSpacing(0f, 1.12f); setTextIsSelectable(true) })
        citeViews(ui, this, o.citations, onCite)
    }

    fun renderChargeCheck(ui: GaUi, container: LinearLayout, r: ChargeCheckResult, share: Pair<() -> Unit, () -> Unit>?, onDial: (String) -> Unit, onCite: (LoopholeCite) -> Unit) {
        val dp = ui::dp
        container.removeAllViews()
        if (r.emergency.isNotEmpty()) {
            container.addView(LinearLayout(ui.context).apply {
                orientation = LinearLayout.VERTICAL; setPadding(dp(14), dp(12), dp(14), dp(12)); background = ui.glowCard(Color.argb(235, 70, 16, 22), Color.rgb(255, 90, 90), 12, glow = true)
                addView(ui.text("If anyone is in danger right now, call 911.", 16f, GaUi.WHITE, ui.sansBold))
                r.emergency.forEach { (label, contact) ->
                    addView(ui.text("$label: $contact", 14f, GaUi.WHITE).apply { setPadding(0, dp(6), 0, 0); isClickable = true; setOnClickListener { onDial(contact.filter { it.isDigit() }) } })
                }
            }, ui.lp(6, 6))
        }
        if (r.refused) { container.addView(ui.emptyCard(R.drawable.ga_ic_error, "Can’t help with that", r.message ?: ""), ui.lp(4, 4)); return }
        container.addView(ui.note(r.estimateNote))
        container.addView(ui.sectionHeader("Likely Charges (${r.charges.size})"))
        if (r.charges.isEmpty()) container.addView(ui.emptyCard(R.drawable.ga_ic_search, "No verified match yet", (r.message ?: "") + "\n\n" + COVERAGE_HINT), ui.lp(4, 4))
        r.charges.forEach { c ->
            container.addView(LinearLayout(ui.context).apply {
                orientation = LinearLayout.VERTICAL; setPadding(dp(14), dp(12), dp(14), dp(12)); background = ui.glowCard(GaUi.CARD, GaUi.STROKE_SOFT, 12, glow = false)
                addView(ui.text(c.levelLabel.uppercase(), 11f, if (c.levelLabel.startsWith("Felony")) Color.rgb(255, 120, 120) else GaUi.BLUE_BRIGHT, ui.sansBold))
                addView(ui.text(c.charge, 15.5f, GaUi.GOLD, ui.sansMedium).apply { setPadding(0, dp(3), 0, dp(3)) })
                if (c.why.isNotBlank()) addView(ui.text(c.why, 14f, GaUi.TEXT).apply { setLineSpacing(0f, 1.12f); setTextIsSelectable(true) })
                addView(ui.text(c.penalty?.let { "Penalty (from the law): “$it”" } ?: (c.penaltyNote ?: ""), 13.5f, GaUi.MUTED).apply { setPadding(0, dp(6), 0, 0); setTextIsSelectable(true) })
                citeViews(ui, this, listOf(c.cite), onCite)
            }, ui.lp(5, 5))
        }
        if (r.defenses.isNotEmpty()) { container.addView(ui.sectionHeader("Possible Defenses & Weak Spots")); r.defenses.forEach { container.addView(optionCard(ui, it, onCite), ui.lp(5, 5)) } }
        if (r.lowest.isNotEmpty()) { container.addView(ui.sectionHeader("Ways to Get the Lowest Outcome")); r.lowest.forEach { container.addView(optionCard(ui, it, onCite), ui.lp(5, 5)) } }
        if (r.lawyer != null) container.addView(lawyerCard(ui, r.lawyer, onCite), ui.lp(10, 6))
        container.addView(LinearLayout(ui.context).apply {
            orientation = LinearLayout.VERTICAL; setPadding(dp(14), dp(12), dp(14), dp(12)); background = ui.glowCard(GaUi.CARD, GaUi.GOLD, 12, glow = false)
            addView(ui.text("Your Rights", 15.5f, GaUi.GOLD, ui.sansBold))
            addView(ui.text(r.rightsReminder, 14f, GaUi.TEXT).apply { setPadding(0, dp(4), 0, 0) })
        }, ui.lp(8, 6))
        if (r.caseId != null) container.addView(ui.note("Saved to your case notes."))
        if (share != null && (r.charges.isNotEmpty() || r.lawyer != null)) container.addView(shareRow(ui, share.first, share.second))
    }
}
