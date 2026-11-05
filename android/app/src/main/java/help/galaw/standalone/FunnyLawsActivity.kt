package help.galaw.standalone

import android.content.Intent
import android.os.Bundle
import android.text.Editable
import android.text.TextWatcher
import android.view.Gravity
import android.view.MotionEvent
import android.view.View
import android.view.animation.DecelerateInterpolator
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import org.json.JSONObject
import kotlin.math.abs
import kotlin.random.Random

/** Data loaded from assets/funny_georgia.json. Every entry carries a citation and stored full text when available. */
data class FunnyLaw(
    val title: String,
    val summary: String,
    val citation: String,
    val jurisdiction: String,
    val category: String,
    val sourceUrl: String,
    val status: String,
    val fullText: String = ""
)
data class FunnyCase(
    val name: String,
    val court: String,
    val year: Int,
    val citation: String,
    val summary: String,
    val sourceUrl: String,
    val fullText: String = ""
)

object FunnyGeorgiaData {
    val CATEGORIES = listOf("All", "State symbols", "Animals", "Food & drink", "Cars & roads", "Weird local rules", "Funny court cases")
    fun parse(json: String): Pair<List<FunnyLaw>, List<FunnyCase>> {
        val o = JSONObject(json)
        val laws = o.getJSONArray("laws").let { a ->
            (0 until a.length()).map { i ->
                a.getJSONObject(i).let {
                    FunnyLaw(
                        it.getString("title"), it.getString("summary"), it.getString("citation"),
                        it.getString("jurisdiction"), it.getString("category"), it.getString("source_url"),
                        it.optString("status"), it.optString("full_text")
                    )
                }
            }
        }
        val cases = o.getJSONArray("cases").let { a ->
            (0 until a.length()).map { i ->
                a.getJSONObject(i).let {
                    FunnyCase(
                        it.getString("name"), it.getString("court"), it.getInt("year"), it.getString("citation"),
                        it.getString("summary"), it.getString("source_url"), it.optString("full_text")
                    )
                }
            }
        }
        return laws to cases
    }
}

/**
 * Funny & Weird Georgia Laws — swipeable card deck (default) + classic list.
 * Dark navy / gold STANDALONE ASSISTANT styling; banner unchanged via GaUi.screen.
 */
class FunnyGeorgiaScreen(
    private val ui: GaUi,
    private val laws: List<FunnyLaw>,
    private val cases: List<FunnyCase>,
    private val onBack: () -> Unit,
    private val openSource: (String) -> Unit,
    startOnCases: Boolean = false,
    private val bottomNav: View? = null,
    private val shareText: (String) -> Unit = {},
    initialDeckMode: Boolean = true,
    private val onModeChanged: (deckMode: Boolean) -> Unit = {},
    private val onAskNextTime: () -> Unit = {}
) {
    private var showCases = startOnCases
    private var query = ""
    private var category = "All"
    private var deckMode = initialDeckMode
    private var index = 0
    private var flipped = false
    private var deckOrder: MutableList<Int> = mutableListOf()
    private lateinit var tabsHost: FrameLayout
    private lateinit var chipsHost: HorizontalScrollView
    private lateinit var chipsRow: LinearLayout
    private lateinit var modeToggle: LinearLayout
    private lateinit var list: LinearLayout
    private lateinit var deckHost: FrameLayout
    private lateinit var progress: TextView
    private lateinit var count: TextView
    private lateinit var body: LinearLayout

    fun build(): View {
        val (root, b) = ui.screen(onBack, bottomNav)
        body = b
        if (bottomNav == null) body.addView(ui.secondaryButton("← Back") { onBack() }.apply { contentDescription = "Back" }, ui.lp(4, 0))
        body.addView(ui.title("Funny & Weird Georgia Laws"))
        body.addView(ui.subtitle("Real Georgia laws and court cases that sound made up. Swipe the deck — or switch to the list. Every card shows its citation."))
        tabsHost = FrameLayout(ui.context); body.addView(tabsHost, ui.lp(0, 8, ui.dp(46)))
        chipsHost = HorizontalScrollView(ui.context).apply { isHorizontalScrollBarEnabled = false }
        chipsRow = LinearLayout(ui.context).apply { orientation = LinearLayout.HORIZONTAL; setPadding(0, ui.dp(2), 0, ui.dp(2)) }
        chipsHost.addView(chipsRow); body.addView(chipsHost, ui.lp(0, 6, ui.dp(42)))
        modeToggle = LinearLayout(ui.context).apply { orientation = LinearLayout.HORIZONTAL; gravity = Gravity.CENTER_VERTICAL }
        body.addView(modeToggle, ui.lp(0, 4))
        val (searchBox, search) = ui.searchField("Search funny laws and cases...", glowing = false, height = 50, showButton = false) { q ->
            query = q.trim().lowercase(); resetDeck(); render()
        }
        search.contentDescription = "Search funny laws and cases"
        search.addTextChangedListener(object : TextWatcher {
            override fun beforeTextChanged(s: CharSequence?, a: Int, b: Int, c: Int) {}
            override fun onTextChanged(s: CharSequence?, a: Int, b: Int, c: Int) {}
            override fun afterTextChanged(s: Editable?) { query = s?.toString()?.trim()?.lowercase() ?: ""; resetDeck(); render() }
        })
        body.addView(searchBox, ui.lp(0, 6, ui.dp(50)))
        progress = ui.text("", 14f, GaUi.GOLD, ui.sansMedium).apply { gravity = Gravity.CENTER_HORIZONTAL }
        body.addView(progress)
        count = ui.note(""); body.addView(count)
        deckHost = FrameLayout(ui.context).apply { minimumHeight = ui.dp(340) }
        body.addView(deckHost, LinearLayout.LayoutParams(-1, ui.dp(380)).apply { topMargin = ui.dp(4); bottomMargin = ui.dp(4) })
        list = LinearLayout(ui.context).apply { orientation = LinearLayout.VERTICAL }; body.addView(list)
        body.addView(ui.note("Legal-information note: laws can be amended, repealed, limited by courts, or apply only in one city. The official text controls. This is not legal advice."))
        // Preload stored full texts so Open source / flip works offline.
        laws.forEach { if (it.fullText.isNotBlank()) LawAccordion.preload(it.citation, it.title, it.fullText, it.status, it.sourceUrl) }
        cases.forEach { if (it.fullText.isNotBlank()) LawAccordion.preload(it.citation, it.name, it.fullText, null, it.sourceUrl) }
        resetDeck(); render(); return root
    }

    private fun matches(vararg f: String) = query.isEmpty() || f.any { it.lowercase().contains(query) }

    private fun filteredLaws(): List<FunnyLaw> {
        val base = laws.filter { matches(it.title, it.summary, it.citation, it.category, it.jurisdiction) }
        return when (category) {
            "All", "Funny court cases" -> if (category == "Funny court cases") emptyList() else base
            else -> base.filter { it.category == category }
        }
    }

    private fun filteredCases(): List<FunnyCase> {
        val base = cases.filter { matches(it.name, it.summary, it.court, it.citation) }
        return if (category == "All" || category == "Funny court cases") base else emptyList()
    }

    private fun deckItems(): List<Any> {
        return if (category == "Funny court cases" || showCases) filteredCases() else filteredLaws()
    }

    private fun resetDeck() {
        val n = deckItems().size
        deckOrder = (0 until n).toMutableList()
        index = 0; flipped = false
    }

    private fun shuffleDeck() {
        deckOrder.shuffle(Random.Default)
        index = 0; flipped = false
        renderDeckCard()
        toast("Shuffled")
    }

    private fun toast(msg: String) = Toast.makeText(ui.context, msg, Toast.LENGTH_SHORT).show()

    private fun shareCurrent() {
        val items = deckItems()
        if (items.isEmpty() || deckOrder.isEmpty()) return
        val i = deckOrder[index.coerceIn(0, deckOrder.lastIndex)]
        val text = when (val item = items[i]) {
            is FunnyLaw -> "${item.title}\n\n${item.summary}\n\n${item.citation} • ${item.jurisdiction}\n\nFrom STANDALONE ASSISTANT"
            is FunnyCase -> "${item.name} (${item.year})\n\n${item.summary}\n\n${item.citation} • ${item.court}\n\nFrom STANDALONE ASSISTANT"
            else -> return
        }
        shareText(text)
    }

    private fun render() {
        tabsHost.removeAllViews()
        tabsHost.addView(
            ui.tabs(listOf("Funny Laws (${laws.size})", "Funny Cases (${cases.size})"), if (showCases || category == "Funny court cases") 1 else 0, {
                showCases = it == 1
                if (showCases) category = "Funny court cases" else if (category == "Funny court cases") category = "All"
                resetDeck(); render()
            }),
            FrameLayout.LayoutParams(-1, -1)
        )
        chipsRow.removeAllViews()
        FunnyGeorgiaData.CATEGORIES.forEach { cat ->
            val on = category == cat
            val chip = ui.text(cat, 13f, if (on) GaUi.NAVY_DEEP else GaUi.WHITE, ui.sansMedium).apply {
                setPadding(ui.dp(12), ui.dp(8), ui.dp(12), ui.dp(8))
                background = ui.rounded(if (on) GaUi.GOLD else GaUi.CARD_SOLID, 18, if (on) GaUi.GOLD else GaUi.STROKE, 1.2f)
                isClickable = true; contentDescription = "Filter $cat"
                setOnClickListener {
                    category = cat
                    showCases = cat == "Funny court cases"
                    resetDeck(); render()
                }
            }
            chipsRow.addView(chip, LinearLayout.LayoutParams(-2, -2).apply { rightMargin = ui.dp(8) })
        }
        modeToggle.removeAllViews()
        fun modeBtn(label: String, on: Boolean, act: () -> Unit) =
            ui.text(label, 13.5f, if (on) GaUi.NAVY_DEEP else GaUi.WHITE, ui.sansBold).apply {
                setPadding(ui.dp(14), ui.dp(8), ui.dp(14), ui.dp(8))
                background = ui.rounded(if (on) GaUi.BLUE_BRIGHT else GaUi.CARD_SOLID, 12, GaUi.STROKE, 1f)
                isClickable = true; setOnClickListener { act() }
            }
        modeToggle.addView(modeBtn("Swipe", deckMode) {
            deckMode = true; flipped = false; onModeChanged(true); render()
        }, LinearLayout.LayoutParams(0, -2, 1f).apply { rightMargin = ui.dp(6) })
        modeToggle.addView(modeBtn("List", !deckMode) {
            deckMode = false; LawAccordion.collapse(); onModeChanged(false); render()
        }, LinearLayout.LayoutParams(0, -2, 1f).apply { rightMargin = ui.dp(6) })
        modeToggle.addView(ui.text("Ask next time", 12.5f, GaUi.MUTED).apply {
            setPadding(ui.dp(8), ui.dp(8), ui.dp(8), ui.dp(8))
            isClickable = true; contentDescription = "Ask List or Swipe next time"
            tag = "funny-ask-next"
            setOnClickListener { onAskNextTime(); Toast.makeText(ui.context, "We'll ask List or Swipe next time you open Funny.", Toast.LENGTH_SHORT).show() }
        })
        LawAccordion.collapse(); list.removeAllViews(); deckHost.removeAllViews()
        val items = deckItems()
        if (deckMode) {
            deckHost.visibility = View.VISIBLE; list.visibility = View.GONE
            if (deckOrder.size != items.size) resetDeck()
            count.text = if (showCases || category == "Funny court cases") "${items.size} funny Georgia court cases"
            else "${items.size} real laws" + if (category != "All") " · $category" else ""
            if (items.isEmpty()) {
                progress.text = "0 / 0"
                deckHost.addView(ui.note("No matches. Try another category or word."))
            } else {
                renderDeckCard()
            }
        } else {
            deckHost.visibility = View.GONE; list.visibility = View.VISIBLE
            progress.text = ""
            if (showCases || category == "Funny court cases") {
                val shown = filteredCases()
                count.text = "${shown.size} of ${cases.size} real Georgia court cases"
                shown.forEach { c -> list.addView(listEntry(c.name + " (${c.year})", c.summary, "${c.court} • ${c.citation}", null, c.citation)) }
            } else {
                val shown = filteredLaws()
                count.text = "${shown.size} of ${laws.size} real laws"
                var lastCat = ""
                shown.forEach { l ->
                    if (l.category != lastCat) { lastCat = l.category; list.addView(ui.sectionHeader(l.category)) }
                    list.addView(listEntry(l.title, l.summary, "${l.citation} • ${l.jurisdiction}", l.status.takeIf { !it.startsWith("In the current Georgia Code") }, l.citation))
                }
            }
            if (list.childCount == 0) list.addView(ui.note("No matches. Try another word."))
        }
    }

    private fun renderDeckCard() {
        val items = deckItems()
        if (items.isEmpty() || deckOrder.isEmpty()) return
        if (index !in deckOrder.indices) index = 0
        val real = deckOrder[index]
        val item = items[real]
        progress.text = "${index + 1} / ${items.size}"
        deckHost.removeAllViews()
        val card = LinearLayout(ui.context).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(ui.dp(18), ui.dp(16), ui.dp(18), ui.dp(14))
            background = ui.glowCard(glow = true)
            elevation = ui.dpf(8f)
        }
        when (item) {
            is FunnyLaw -> {
                card.addView(ui.text(item.category.uppercase(), 11.5f, GaUi.GOLD, ui.sansMedium))
                card.addView(ui.text(item.title, 20f, GaUi.WHITE, ui.sansBold).apply { setPadding(0, ui.dp(6), 0, ui.dp(6)) })
                if (!flipped) {
                    card.addView(ui.text(item.summary, 15f, GaUi.TEXT).apply { setLineSpacing(0f, 1.15f) })
                    card.addView(ui.text("⚖ ${item.citation} • ${item.jurisdiction}", 13f, GaUi.BLUE, ui.sansBold).apply { setPadding(0, ui.dp(10), 0, 0) })
                    card.addView(ui.text("Tap to read the full law ▾", 12.5f, GaUi.MUTED).apply { setPadding(0, ui.dp(10), 0, 0) })
                } else {
                    val body = ScrollView(ui.context).apply {
                        addView(ui.text(item.fullText.ifBlank { "Full text isn’t stored for this entry yet." }, 14f, GaUi.TEXT).apply {
                            setTextIsSelectable(true); setLineSpacing(0f, 1.15f)
                        })
                    }
                    card.addView(body, LinearLayout.LayoutParams(-1, ui.dp(180)))
                    card.addView(ui.text("⚖ ${item.citation}", 12.5f, GaUi.BLUE, ui.sansBold).apply { setPadding(0, ui.dp(8), 0, 0) })
                    card.addView(ui.text("Tap to flip back ▴", 12.5f, GaUi.MUTED).apply { setPadding(0, ui.dp(6), 0, 0) })
                }
            }
            is FunnyCase -> {
                card.addView(ui.text("FUNNY COURT CASE", 11.5f, GaUi.GOLD, ui.sansMedium))
                card.addView(ui.text(item.name, 20f, GaUi.WHITE, ui.sansBold).apply { setPadding(0, ui.dp(6), 0, ui.dp(6)) })
                if (!flipped) {
                    card.addView(ui.text(item.summary, 15f, GaUi.TEXT).apply { setLineSpacing(0f, 1.15f) })
                    card.addView(ui.text("⚖ ${item.citation} • ${item.court} (${item.year})", 13f, GaUi.BLUE, ui.sansBold).apply { setPadding(0, ui.dp(10), 0, 0) })
                    card.addView(ui.text("Tap to expand ▾", 12.5f, GaUi.MUTED).apply { setPadding(0, ui.dp(10), 0, 0) })
                } else {
                    val body = ScrollView(ui.context).apply {
                        addView(ui.text(item.fullText.ifBlank { item.summary }, 14f, GaUi.TEXT).apply {
                            setTextIsSelectable(true); setLineSpacing(0f, 1.15f)
                        })
                    }
                    card.addView(body, LinearLayout.LayoutParams(-1, ui.dp(180)))
                    card.addView(ui.text("Tap to flip back ▴", 12.5f, GaUi.MUTED).apply { setPadding(0, ui.dp(6), 0, 0) })
                }
            }
        }
        card.setOnClickListener { flipped = !flipped; renderDeckCard() }
        attachSwipe(card, items.size)
        deckHost.addView(card, FrameLayout.LayoutParams(-1, -1))

        val actions = LinearLayout(ui.context).apply {
            orientation = LinearLayout.HORIZONTAL; gravity = Gravity.CENTER
            setPadding(0, ui.dp(8), 0, 0)
        }
        fun act(label: String, cd: String, block: () -> Unit) =
            ui.secondaryButton(label) { block() }.apply { contentDescription = cd }
        actions.addView(act("⟵ Prev", "Previous card") { go(-1) }, LinearLayout.LayoutParams(0, ui.dp(44), 1f).apply { rightMargin = ui.dp(4) })
        actions.addView(act("Shuffle", "Shuffle deck") { shuffleDeck() }, LinearLayout.LayoutParams(0, ui.dp(44), 1f).apply { rightMargin = ui.dp(4) })
        actions.addView(act("Share", "Share this card") { shareCurrent() }, LinearLayout.LayoutParams(0, ui.dp(44), 1f).apply { rightMargin = ui.dp(4) })
        actions.addView(act("Next ⟶", "Next card") { go(1) }, LinearLayout.LayoutParams(0, ui.dp(44), 1f))
        // Put actions below card inside deckHost overlay area: use a vertical wrapper
        deckHost.removeAllViews()
        val wrap = LinearLayout(ui.context).apply { orientation = LinearLayout.VERTICAL }
        wrap.addView(card, LinearLayout.LayoutParams(-1, 0, 1f))
        wrap.addView(actions)
        deckHost.addView(wrap, FrameLayout.LayoutParams(-1, -1))
        attachSwipe(card, items.size)
    }

    private fun go(delta: Int) {
        val n = deckOrder.size
        if (n == 0) return
        index = (index + delta + n) % n
        flipped = false
        renderDeckCard()
    }

    private fun attachSwipe(card: View, n: Int) {
        var downX = 0f; var downY = 0f; var dragging = false
        card.setOnTouchListener { v, e ->
            when (e.actionMasked) {
                MotionEvent.ACTION_DOWN -> { downX = e.rawX; downY = e.rawY; dragging = false; v.parent.requestDisallowInterceptTouchEvent(true); true }
                MotionEvent.ACTION_MOVE -> {
                    val dx = e.rawX - downX; val dy = e.rawY - downY
                    if (!dragging && abs(dx) > abs(dy) && abs(dx) > ui.dp(8)) dragging = true
                    if (dragging) {
                        v.translationX = dx
                        v.rotation = dx / 40f
                        v.alpha = (1f - abs(dx) / (ui.dp(280).toFloat())).coerceIn(0.4f, 1f)
                    }
                    true
                }
                MotionEvent.ACTION_UP, MotionEvent.ACTION_CANCEL -> {
                    v.parent.requestDisallowInterceptTouchEvent(false)
                    val dx = e.rawX - downX
                    if (dragging && abs(dx) > ui.dp(96)) {
                        val dir = if (dx < 0) 1 else -1
                        v.animate().translationX(if (dx < 0) -ui.dp(420).toFloat() else ui.dp(420).toFloat()).alpha(0f).setDuration(180)
                            .setInterpolator(DecelerateInterpolator()).withEndAction {
                                v.translationX = 0f; v.rotation = 0f; v.alpha = 1f; go(dir)
                            }.start()
                    } else if (!dragging && abs(dx) < ui.dp(12) && abs(e.rawY - downY) < ui.dp(12)) {
                        v.animate().translationX(0f).rotation(0f).alpha(1f).setDuration(120).start()
                        v.performClick()
                    } else {
                        v.animate().translationX(0f).rotation(0f).alpha(1f).setDuration(160).setInterpolator(DecelerateInterpolator()).start()
                    }
                    true
                }
                else -> false
            }
        }
    }

    private fun refreshLabels() {
        for (i in 0 until list.childCount) {
            val v = list.getChildAt(i) as? LinearLayout ?: continue
            val c = (v.tag as? String)?.takeIf { it.startsWith("funny:") }?.removePrefix("funny:") ?: continue
            (v.getChildAt(v.childCount - 1) as? TextView)?.text = if (LawAccordion.isOpen(c)) "Close source ▴" else "Open source ▾"
        }
    }

    private fun listEntry(title: String, summary: String, cite: String, status: String?, citation: String) = LinearLayout(ui.context).apply {
        orientation = LinearLayout.VERTICAL; setPadding(ui.dp(14), ui.dp(12), ui.dp(14), ui.dp(12)); background = ui.glowCard(glow = false)
        layoutParams = ui.lp(5, 5)
        addView(ui.text(title, 16f, GaUi.WHITE, ui.sansBold))
        addView(ui.text(summary, 14f, GaUi.TEXT).apply { setPadding(0, ui.dp(4), 0, ui.dp(4)) })
        addView(ui.text("⚖ $cite", 12.5f, GaUi.BLUE, ui.sansBold))
        if (status != null) addView(ui.text("⚠ Status: $status", 12.5f, GaUi.GOLD).apply { setPadding(0, ui.dp(4), 0, 0) })
        val toggleLabel = ui.text("Open source ▾", 12.5f, GaUi.MUTED).apply { setPadding(0, ui.dp(4), 0, 0) }; addView(toggleLabel)
        contentDescription = "$title. $cite. Open source"
        tag = "funny:$citation"
        setOnClickListener { LawAccordion.toggle(this, citation, showSourceLink = false); refreshLabels() }
    }
}

class FunnyLawsActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState); SystemBars.apply(this)
        val prefs = getSharedPreferences("ga_settings", MODE_PRIVATE)
        val remember = prefs.getBoolean("funny_view_remember", false)
        val deck = if (remember) prefs.getString("funny_view_mode", "swipe") != "list" else true
        if (!remember) {
            // Navy placeholder behind the chooser so the window isn't blank.
            setContentView(android.widget.FrameLayout(this).apply { setBackgroundColor(GaUi.NAVY) })
            FunnyViewChooser.show(this) { useSwipe, rememberChoice ->
                if (rememberChoice) prefs.edit().putBoolean("funny_view_remember", true).putString("funny_view_mode", if (useSwipe) "swipe" else "list").apply()
                showFunny(useSwipe)
            }
        } else showFunny(deck)
    }

    private fun showFunny(deckMode: Boolean) {
        val prefs = getSharedPreferences("ga_settings", MODE_PRIVATE)
        val (laws, cases) = FunnyGeorgiaData.parse(assets.open("funny_georgia.json").bufferedReader().use { it.readText() })
        setContentView(
            FunnyGeorgiaScreen(
                GaUi(this), laws, cases, { finish() }, { }, intent.getBooleanExtra("cases", false),
                shareText = { text ->
                    startActivity(Intent.createChooser(Intent(Intent.ACTION_SEND).setType("text/plain").putExtra(Intent.EXTRA_TEXT, text), "Share funny Georgia law"))
                },
                initialDeckMode = deckMode,
                onModeChanged = { swipe ->
                    if (prefs.getBoolean("funny_view_remember", false))
                        prefs.edit().putString("funny_view_mode", if (swipe) "swipe" else "list").apply()
                },
                onAskNextTime = { prefs.edit().putBoolean("funny_view_remember", false).remove("funny_view_mode").apply() }
            ).build()
        )
    }
}

/** Styled List vs Swipe picker shown when Funny opens (unless the user asked us to remember). */
object FunnyViewChooser {
    fun show(activity: android.app.Activity, onPick: (useSwipe: Boolean, remember: Boolean) -> Unit) {
        val ui = GaUi(activity)
        val box = LinearLayout(activity).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(ui.dp(20), ui.dp(8), ui.dp(20), ui.dp(4))
            setBackgroundColor(GaUi.NAVY)
        }
        box.addView(ui.text("How do you want to browse?", 18f, GaUi.WHITE, ui.sansBold))
        box.addView(ui.text("People love to swipe — or stick with the classic list. You can switch anytime on the Funny screen.", 14f, GaUi.MUTED).apply { setPadding(0, ui.dp(6), 0, ui.dp(12)) })
        val remember = android.widget.CheckBox(activity).apply {
            text = "Remember my choice"
            setTextColor(GaUi.TEXT)
            buttonTintList = android.content.res.ColorStateList.valueOf(GaUi.GOLD)
            contentDescription = "Remember my choice"
        }
        val holder = arrayOfNulls<android.app.AlertDialog>(1)
        fun option(title: String, blurb: String, swipe: Boolean) = LinearLayout(activity).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(ui.dp(14), ui.dp(12), ui.dp(14), ui.dp(12))
            background = ui.glowCard(glow = true)
            addView(ui.text(title, 17f, GaUi.GOLD, ui.sansBold))
            addView(ui.text(blurb, 13.5f, GaUi.TEXT).apply { setPadding(0, ui.dp(4), 0, 0) })
            isClickable = true; contentDescription = title
            setOnClickListener { holder[0]?.dismiss(); onPick(swipe, remember.isChecked) }
            layoutParams = ui.lp(6, 6)
        }
        box.addView(option("Swipe", "Card deck — swipe left/right, tap to flip the full law.", true))
        box.addView(option("List", "Classic scrollable list with Open source accordion.", false))
        box.addView(remember, LinearLayout.LayoutParams(-1, -2).apply { topMargin = ui.dp(8) })
        val dlg = android.app.AlertDialog.Builder(activity, android.R.style.Theme_DeviceDefault_Dialog_NoActionBar)
            .setView(box)
            .setCancelable(true)
            .create()
        holder[0] = dlg
        dlg.setOnCancelListener { onPick(true, false) }
        dlg.show()
        dlg.window?.setBackgroundDrawable(android.graphics.drawable.ColorDrawable(GaUi.NAVY))
        dlg.window?.setLayout((activity.resources.displayMetrics.widthPixels * 0.92f).toInt(), android.view.ViewGroup.LayoutParams.WRAP_CONTENT)
    }
}
