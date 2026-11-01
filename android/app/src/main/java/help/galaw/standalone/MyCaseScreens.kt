package help.galaw.standalone

import android.graphics.Color
import android.view.Gravity
import android.view.View
import android.widget.EditText
import android.widget.LinearLayout
import org.json.JSONArray
import org.json.JSONObject

/** 'My Case' hub: one guided flow for the whole case (criminal stages, civil, or just ask). */
object MyCaseScreens {
    val STAGES = listOf(
        "arrested" to "Arrested / bond", "pretrial" to "Charged / pretrial", "plea" to "Plea offer", "trial" to "Trial",
        "sentenced" to "Sentenced", "appeal" to "Appeal", "prison" to "In prison – get out or reduce time",
        "probation" to "Probation / parole", "record" to "Clear a record")
    private val HINTS = mapOf(
        "arrested" to "Where and when was the arrest? What are the charges? Has bond been set?",
        "pretrial" to "What are the charges? Court and county? Has there been an arraignment? Any search or self-defense issues?",
        "plea" to "What is the charge, and what is the offer? Any prior record?",
        "trial" to "What is the charge and trial date? Any evidence or witness problems?",
        "sentenced" to "Charge, sentence, plea or trial, court and county. Any problems with the lawyer or the case?",
        "appeal" to "Charge, sentence date, plea or trial. Was a notice of appeal filed?",
        "prison" to "Charge, sentence, plea or trial, court and county, time served. Issues like a bad lawyer, new evidence, an illegal sentence?",
        "probation" to "What are the probation or parole terms? What violation is alleged?",
        "record" to "What's on the record? Arrests, dismissed charges, First Offender, convictions?")
    val CHARGE_STAGES = setOf("arrested", "pretrial", "plea", "trial")

    class StageForm(val root: View, val situation: EditText, val dates: Map<String, EditText>, val results: LinearLayout)

    private fun choice(ui: GaUi, title: String, sub: String?, highlight: Boolean, onTap: () -> Unit) = LinearLayout(ui.context).apply {
        orientation = LinearLayout.VERTICAL; setPadding(ui.dp(16), ui.dp(14), ui.dp(16), ui.dp(14)); isClickable = true; contentDescription = title
        background = if (highlight) ui.glowCard(Color.argb(235, 22, 30, 44), GaUi.GOLD, 14, glow = true) else ui.glowCard(GaUi.CARD, GaUi.STROKE_SOFT, 12, glow = false)
        addView(ui.text(title + "  ›", 16.5f, if (highlight) GaUi.GOLD else GaUi.WHITE, ui.sansMedium))
        if (sub != null) addView(ui.text(sub, 13.5f, GaUi.MUTED).apply { setPadding(0, ui.dp(4), 0, 0) })
        setOnClickListener { onTap() }
    }

    fun hub(ui: GaUi, nav: GaScreens.Nav, saved: List<JSONObject>, onKind: (String) -> Unit, onSaved: (JSONObject) -> Unit, onDeleteSaved: (JSONObject) -> Unit): View {
        val (root, body) = GaScreens.page(ui, nav, GaScreens.Tab.LAWS, "My Case", "Step-by-step help through a whole case – yours or someone else's: what to do next, deadlines, and the Georgia laws that apply.")
        body.addView(ui.sectionHeader("1. What kind of case?"))
        body.addView(choice(ui, "Criminal", "Arrest, charges, plea, trial, sentence, prison, probation, record", true) { onKind("criminal") }, ui.lp(4, 6))
        body.addView(choice(ui, "Civil", "Landlord, deposit, debt, money owed, family, contracts", false) { onKind("civil") }, ui.lp(4, 6))
        body.addView(choice(ui, "Not sure – just ask", "Describe it in your own words in Talk to Me", false) { onKind("ask") }, ui.lp(4, 6))
        if (saved.isNotEmpty()) {
            body.addView(ui.sectionHeader("Saved cases"))
            saved.forEach { s ->
                val stageLabel = STAGES.firstOrNull { it.first == s.optString("stage") }?.second ?: "Civil"
                body.addView(choice(ui, s.optString("name", "My case"), "$stageLabel • saved ${s.optString("saved_at")}", false) { onSaved(s) }.apply {
                    setOnLongClickListener { onDeleteSaved(s); true }
                }, ui.lp(4, 6))
            }
            body.addView(ui.note("Saved on this phone only. Long-press a saved case to delete it."))
        }
        body.addView(ui.note("General legal information, not legal advice."))
        return root
    }

    fun stages(ui: GaUi, nav: GaScreens.Nav, onStage: (String) -> Unit): View {
        val (root, body) = GaScreens.page(ui, nav, GaScreens.Tab.LAWS, "Criminal case", "What stage is the case in?")
        STAGES.forEach { (k, label) -> body.addView(choice(ui, label, null, k == "prison") { onStage(k) }, ui.lp(3, 5)) }
        return root
    }

    fun stageForm(ui: GaUi, nav: GaScreens.Nav, stage: String, prefill: JSONObject?, onRun: () -> Unit): StageForm {
        val label = STAGES.first { it.first == stage }.second
        val (root, body) = GaScreens.page(ui, nav, GaScreens.Tab.LAWS, label, "Tell us what you know. Skip anything you don't know.")
        val situation = ui.input(HINTS[stage] ?: "Describe your case", true).apply { minLines = 4; setText(prefill?.optString("situation") ?: "") }
        body.addView(situation, ui.lp(8, 6))
        val fields = when (stage) {
            "arrested" -> listOf("arrest_date" to "Arrest date (YYYY-MM-DD)")
            "pretrial", "plea", "trial" -> listOf("arraignment_date" to "Arraignment date (YYYY-MM-DD)")
            "sentenced", "appeal", "prison", "probation" -> listOf("sentence_date" to "Sentence date (YYYY-MM-DD)", "final_date" to "Appeal finished / conviction final (optional)")
            else -> emptyList()
        }
        val dates = fields.associate { (k, h) -> k to ui.input(h).apply { setText(prefill?.optString(k) ?: ""); inputType = android.text.InputType.TYPE_CLASS_DATETIME } }
        dates.values.forEach { body.addView(it, ui.lp(2, 4)) }
        body.addView(ui.primaryButton("Show next steps") { onRun() }, ui.lp(6, 8))
        val results = LinearLayout(ui.context).apply { orientation = LinearLayout.VERTICAL }
        body.addView(results)
        return StageForm(root, situation, dates, results)
    }

    private fun cites(arr: JSONArray?) = (0 until (arr?.length() ?: 0)).mapNotNull { arr!!.optJSONObject(it) }.map { GaScreens.LoopholeCite(it.optString("citation"), it.optString("title"), null) }

    fun render(ui: GaUi, box: LinearLayout, g: JSONObject, stage: String, onCharges: () -> Unit, onDefenses: () -> Unit, onSave: () -> Unit, onLink: (String) -> Unit) {
        val dp = ui::dp
        box.removeAllViews()
        fun card(gold: Boolean = false) = LinearLayout(ui.context).apply {
            orientation = LinearLayout.VERTICAL; setPadding(dp(14), dp(12), dp(14), dp(12))
            background = if (gold) ui.glowCard(Color.argb(235, 22, 30, 44), GaUi.GOLD, 14, glow = true) else ui.glowCard(GaUi.CARD, GaUi.STROKE_SOFT, 12, glow = false)
        }
        val tips = g.optJSONArray("family_tips")
        box.addView(ui.sectionHeader("Next steps"))
        box.addView(card().apply { val a = g.optJSONArray("next_steps"); for (i in 0 until (a?.length() ?: 0)) addView(ui.text("• " + a!!.optString(i), 14.5f, GaUi.TEXT).apply { setPadding(0, dp(2), 0, dp(2)) }) }, ui.lp(2, 6))
        if (tips != null && tips.length() > 0) {
            box.addView(ui.sectionHeader("Family and friends can help"))
            box.addView(card().apply { for (i in 0 until tips.length()) addView(ui.text("• " + tips.optString(i), 14.5f, GaUi.TEXT).apply { setPadding(0, dp(2), 0, dp(2)) }) }, ui.lp(2, 6))
        }
        val tl = g.optJSONArray("timeline")
        if (tl != null && tl.length() > 0) {
            box.addView(ui.sectionHeader("Deadline timeline"))
            box.addView(card(true).apply {
                for (i in 0 until tl.length()) { val t = tl.getJSONObject(i); val passed = t.optBoolean("passed")
                    addView(ui.text("${t.optString("due")}  •  ${t.optString("title")}", 14.5f, GaUi.WHITE, ui.sansMedium).apply { setPadding(0, dp(4), 0, 0) })
                    addView(ui.text(t.optString("label"), 13f, if (passed) Color.rgb(245, 150, 150) else GaUi.GOLD)) }
                addView(ui.note("Dates are estimates from what you entered. Confirm every deadline with a lawyer."))
            }, ui.lp(2, 6))
        }
        box.addView(ui.sectionHeader("Motions & filings that may apply"))
        val opts = g.optJSONArray("options") ?: JSONArray()
        for (i in 0 until opts.length()) { val o = opts.getJSONObject(i)
            box.addView(card(o.optBoolean("highlight")).apply {
                if (o.optBoolean("highlight")) addView(ui.text("MATCHES THE DESCRIPTION", 11f, GaUi.GOLD, ui.sansBold))
                addView(ui.text(o.optString("title"), 16f, GaUi.WHITE, ui.sansMedium))
                addView(ui.text(o.optString("what"), 14f, GaUi.TEXT).apply { setPadding(0, dp(4), 0, 0) })
                o.optString("deadline").takeIf { it.isNotBlank() && it != "null" }?.let { d ->
                    val st = o.optJSONObject("deadline_status")
                    addView(ui.text("⏰ Deadline: $d" + (st?.let { "  (${it.optString("label")})" } ?: ""), 13.5f, if (st?.optBoolean("passed") == true) Color.rgb(245, 150, 150) else GaUi.GOLD, ui.sansMedium).apply { setPadding(0, dp(6), 0, 0) }) }
                o.optString("where").takeIf { it.isNotBlank() && it != "null" }?.let { addView(ui.text("Where to file: $it", 13.5f, GaUi.MUTED).apply { setPadding(0, dp(4), 0, 0) }) }
                GaScreens.citeViews(ui, this, cites(o.optJSONArray("citations"))) {}
            }, ui.lp(4, 5)) }
        if (stage in CHARGE_STAGES) box.addView(ui.secondaryButton("Check possible charges") { onCharges() }, ui.lp(8, 4))
        box.addView(ui.secondaryButton("Defenses & motions") { onDefenses() }, ui.lp(4, 4))
        box.addView(ui.primaryButton("Save this case") { onSave() }, ui.lp(8, 6))
        box.addView(ui.sectionHeader("Free and low-cost help"))
        val rs = g.optJSONArray("resources") ?: JSONArray()
        for (i in 0 until rs.length()) { val r = rs.getJSONObject(i)
            box.addView(ui.text(r.optString("title") + " ›", 14.5f, GaUi.BLUE_BRIGHT).apply { setPadding(0, dp(5), 0, dp(5)); isClickable = true; setOnClickListener { onLink(r.optString("url")) } }) }
        box.addView(ui.note(g.optString("disclaimer")))
    }
}
