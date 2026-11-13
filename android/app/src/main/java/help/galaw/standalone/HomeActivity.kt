package help.galaw.standalone

import android.app.AlertDialog
import android.content.Intent
import android.graphics.Color
import android.graphics.Typeface
import android.graphics.drawable.GradientDrawable
import android.net.Uri
import android.os.Bundle
import android.view.Gravity
import android.view.View
import android.view.ViewGroup
import android.widget.*
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.appcompat.app.AppCompatDelegate
import androidx.core.os.LocaleListCompat
import org.json.JSONArray
import org.json.JSONObject
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import kotlin.concurrent.thread

class HomeActivity : AppCompatActivity() {
    private lateinit var api: ApiClient
    private lateinit var ui: GaUi
    private var onHome = true
    private var drawerView: View? = null
    private val navy = GaUi.NAVY
    private val panel = GaUi.CARD_SOLID
    private val blue = GaUi.BLUE
    private val muted = GaUi.MUTED
    private lateinit var docs: DocumentLibrary
    /** What to do with a document once it is saved in the shared library (read in AI Help, attach to a case...). */
    private var afterDocAdded: ((DocumentLibrary.Doc) -> Unit)? = null
    private val cameraPages = mutableListOf<Uri>()
    private var cameraUri: Uri? = null
    private val pickDocument = registerForActivityResult(ActivityResultContracts.OpenMultipleDocuments()) { uris -> if (uris.isNotEmpty()) addToLibrary(uris) else afterDocAdded = null }
    private val pickPhotos = registerForActivityResult(ActivityResultContracts.PickMultipleVisualMedia(DocumentLibrary.MAX_PAGES)) { uris -> if (uris.isNotEmpty()) addToLibrary(uris) else afterDocAdded = null }
    private val takePhoto = registerForActivityResult(ActivityResultContracts.TakePicture()) { ok ->
        val uri = cameraUri; cameraUri = null
        if (ok && uri != null) cameraPages += uri
        if (cameraPages.isEmpty()) { afterDocAdded = null; return@registerForActivityResult }
        AlertDialog.Builder(this).setTitle("Page ${cameraPages.size} saved").setMessage("Take a photo of the next page, or finish if that was the last page.")
            .setPositiveButton("Finish"){_,_-> val pages=cameraPages.toList(); cameraPages.clear(); addToLibrary(pages, "Scanned paper " + SimpleDateFormat("MMM d, h:mm a", Locale.US).format(Date()) + if (pages.size > 1) " (${pages.size} pages)" else "") }
            .setNeutralButton("Next page"){_,_-> if (cameraPages.size >= DocumentLibrary.MAX_PAGES) toast("That's the most pages for one document.") else launchCamera() }
            .setCancelable(false).show()
    }
    private fun launchCamera() { try { val u = docs.newCameraUri(); cameraUri = u; takePhoto.launch(u) } catch (e: Exception) { toast("The camera couldn't be opened. Choose a photo instead."); pickPhotos.launch(androidx.activity.result.PickVisualMediaRequest(ActivityResultContracts.PickVisualMedia.ImageOnly)) } }
    /** Camera, photos, or any file (Downloads, Drive, PDFs) — all land in the one shared document library. */
    private fun chooseNewDocument(then: ((DocumentLibrary.Doc) -> Unit)? = null) {
        afterDocAdded = then
        AlertDialog.Builder(this).setTitle("Add a document").setItems(arrayOf("Take a photo of a paper", "Choose photos", "Choose a file (PDF, Downloads, Drive…)")) { _, i -> when (i) {
            0 -> { cameraPages.clear(); launchCamera() }
            1 -> pickPhotos.launch(androidx.activity.result.PickVisualMediaRequest(ActivityResultContracts.PickVisualMedia.ImageOnly))
            else -> pickDocument.launch(arrayOf("application/pdf", "image/*", "text/*", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "*/*"))
        } }.setOnCancelListener { afterDocAdded = null }.show()
    }
    private fun addToLibrary(uris: List<Uri>, name: String? = null) {
        val then = afterDocAdded; afterDocAdded = null
        toast("Saving document…")
        thread { try { val d = docs.add(uris, name); runOnUiThread { if (then != null) then(d) else { toast("Saved to My Documents."); showDocuments() } } }
            catch (e: Exception) { runOnUiThread { showError(if (e is DocumentLibrary.DocumentException) e.message ?: "That file couldn't be saved." else "That file couldn't be saved on this phone (${e.javaClass.simpleName}). Try again.", { chooseNewDocument(then) }) } } }
    }
    private fun pickSavedDocument(title: String, onPick: (DocumentLibrary.Doc) -> Unit) {
        val list = docs.list()
        val labels = (listOf("＋ Add a new document (camera, photos, files)") + list.map { it.name }).toTypedArray()
        AlertDialog.Builder(this).setTitle(title).setItems(labels) { _, i -> if (i == 0) chooseNewDocument(onPick) else onPick(list[i - 1]) }.show()
    }
    private fun documentActions(d: DocumentLibrary.Doc) {
        val attached = if (d.caseIds.isEmpty()) "" else " (attached to ${d.caseIds.size} case${if (d.caseIds.size > 1) "s" else ""})"
        AlertDialog.Builder(this).setTitle(d.name + attached).setItems(arrayOf("Use in AI Help (read & explain it)", "Attach to a case", "Open", "Share", "Rename", "Delete from this phone")) { _, i -> when (i) {
            0 -> readInAiHelp(d)
            1 -> attachToCase(d)
            2 -> runCatching { startActivity(docs.viewIntent(d)) }.onFailure { toast("No app on this phone can open this file type.") }
            3 -> startActivity(docs.shareIntent(d))
            4 -> { val input = EditText(this).apply { setText(d.name) }; AlertDialog.Builder(this).setTitle("Rename").setView(input).setPositiveButton("Save") { _, _ -> docs.rename(d.id, input.text.toString().trim().ifBlank { d.name }); showDocuments() }.setNegativeButton("Cancel", null).show() }
            else -> AlertDialog.Builder(this).setTitle("Delete this document?").setMessage("This removes it from this phone. Copies already attached to a case stay in that case.").setPositiveButton("Delete") { _, _ -> docs.delete(d.id); showDocuments() }.setNegativeButton("Cancel", null).show()
        } }.show()
    }
    private fun attachToCase(d: DocumentLibrary.Doc, caseId: Int? = null) {
        val go = { id: Int -> runTask("Attaching to case…", { attachToCase(d, id) }) { api.uploadDocument(id, d); docs.markAttached(d.id, id); runOnUiThread { toast("Attached to the case."); showCaseDocuments(id) } } }
        if (caseId != null) return go(caseId)
        runTask("Loading your cases…", { attachToCase(d) }) { val cases = caseRows(api.cases()); casesCache = cases; runOnUiThread {
            if (cases.isEmpty()) { toast("Create a case first, then attach the document."); showCreateCase(); return@runOnUiThread }
            AlertDialog.Builder(this).setTitle("Attach to which case?").setItems(cases.map { it.title }.toTypedArray()) { _, i -> go(cases[i].id) }.show() } }
    }
    /** Open AI Help and have the AI read the document's pages, then keep chatting about it. */
    private fun readInAiHelp(d: DocumentLibrary.Doc, caseId: Int? = null) {
        val pages = docs.readablePages(d)
        if (pages.isEmpty()) return toast("AI Help can read photos and PDFs. Save this paper as a photo or PDF first.")
        showTalkToMe(); val c = chat ?: return
        val q = "Read my document \"${d.name}\" (${pages.size} page${if (pages.size > 1) "s" else ""}) and explain it."
        val line = talk.add(true, q, now()); c.user(line.text, line.time, line.id)
        runDocumentRead(c, d, pages, caseId)
    }
    private fun runDocumentRead(c: GaScreens.Chat, d: DocumentLibrary.Doc, pages: List<DocumentLibrary.Page>, caseId: Int?) {
        val stop = c.progress(listOf("Sending ${pages.size} page${if (pages.size > 1) "s" else ""}…") + LoadingLines.DOCUMENT_READ)
        thread { try { val r = api.readDocument(pages, "", caseId, paperTranslate); val answer = r.optString("answer"); val text = r.optString("extracted_text")
                docs.saveSummary(d.id, answer)
                // The text read from the paper stays in the chat context so follow-up questions can use it.
                val full = answer + if (text.isNotBlank()) "\n\nText read from the paper:\n" + text else ""
                // Automatic "Your Defense Plan" built from the facts on the paper (server: /documents/read).
                val plan = r.optJSONObject("defense_plan"); val planText = plan?.optString("answer").orEmpty(); val stage = plan?.optString("case_stage").orEmpty()
                runOnUiThread { stop(); val bot = talk.add(false, full, now(), ShareText.answer("Document: " + d.name, full)); if (chat === c) { c.bot(bot.text, bot.time, bot.id)
                    if (planText.isNotBlank()) { val pb = talk.add(false, planText, now(), ShareText.answer("Defense plan: " + d.name, planText)); c.bot(pb.text, pb.time, pb.id)
                        if (stage.isNotBlank() && MyCaseScreens.STAGES.any { it.first == stage }) c.attach(ui.secondaryButton("Open My Case: " + MyCaseScreens.STAGES.first { it.first == stage }.second + " ›") { showStage(stage, JSONObject().put("situation", (r.optString("document_type") + ": " + r.optString("summary")).take(2000))) })
                        c.followUps(TalkToMeController.followUps(plan!!)) { f -> sendTalk(f) }
                    } else c.followUps(listOf("What does this document mean?", "Is there a deadline in this document?", "What questions should I ask a lawyer about it?")) { f -> sendTalk(f) }
                    c.attach(buildDefenseButton(planText.isNotBlank()))
                    c.attach(ui.secondaryButton("Courtroom prep ›"){ showCourtroomPrep(plan?.optString("case_type")) })
                    c.attach(ui.secondaryButton("Share as PDF"){ sharePlanPdf(if(planText.isNotBlank()) "Your Defense Plan" else "Paper reading", if(planText.isNotBlank()) planText else full) })
                    if(ReadAloud.saved(this)!=ReadAloud.OFF) c.attach(ui.secondaryButton("Read aloud"){ maybeRead(if(planText.isNotBlank()) planText else full) })
                    if(!paperTranslate && r.optString("answer_es").isBlank()) c.attach(ui.secondaryButton("Translate to Spanish"){ translatePaperReading(c, r) })
                    } } }
            catch (e: Exception) { runOnUiThread { stop(); val msg = AiErrors.message(e); val bot = talk.add(false, msg, now(), inContext = false); if (chat === c) { c.bot(bot.text, bot.time, bot.id); c.retry { talk.delete(bot.id); c.remove(bot.id); runDocumentRead(c, d, pages, caseId) } } } } }
    }
    override fun onCreate(savedInstanceState: Bundle?) { super.onCreate(savedInstanceState); SystemBars.apply(this); api = ApiClient(this); docs = DocumentLibrary(this); ui = GaUi(this); showHome(); thread { runCatching { api.ensureSession() } } }
    override fun onStart() { super.onStart(); UsageAnalytics.onAppStart(this, api) }
    private var currentScreen = "home"
    private var askedFeedbackPrompt = false
    @Deprecated("Deprecated in Java") override fun onBackPressed() { if (drawerView != null) { closeDrawer(); return }; if (!onHome) showHome() else super.onBackPressed() }
    private fun dp(v: Int) = (v * resources.displayMetrics.density).toInt()
    private val homeActions = object : ApprovedHomeScreen.Actions {
        override fun openMenu()=showMenu(); override fun openAccount()=showAccount(); override fun ask(question:String)=askFromHome(question); override fun openCases()=showCases(); override fun openTalkToMe()=showTalkToMe(); override fun openLegalTools()=showLegalTools(); override fun openGeorgiaLaws()=showGeorgiaLaws(); override fun openCourtInfo()=showCourtInfo(); override fun openLegalForms()=showLegalForms(); override fun openCaseAnalysis()=showMyCase(); override fun openKnowYourRights()=showKnowYourRights(); override fun openResources()=showResources(); override fun openEmergency()=showEmergency(); override fun openHome()=showHome(); override fun openDocuments()=showDocuments(); override fun openFunnyLaws()=showFunnyLaws(); override fun openFeedback()=showFeedback()
    }
    private val nav = object : GaScreens.Nav {
        override fun menu()=showMenu(); override fun home()=showHome(); override fun laws()=showGeorgiaLaws(); override fun aiHelp()=showTalkToMe(); override fun documents()=showDocuments(); override fun account()=showAccount(); override fun more()=showMore(); override fun legalWork()=showMotionsHub(); override fun funny()=showFunnyLaws()
    }
    private fun showHome(){ closeDrawer(); onHome=true; currentScreen="home"; setContentView(ApprovedHomeScreen(this,homeActions).build()); maybeAskFeedback() }
    /** Every inner screen: mockup header (tap the wordmark to go Home), content, bottom nav. */
    private fun show(root:View){ closeDrawer(); onHome=false; root.findViewWithTag<View>("brand")?.apply{contentDescription="Back to Home";setOnClickListener{showHome()}}; setContentView(root) }
    private fun page(title:String,subtitle:String?=null,tab:GaScreens.Tab=GaScreens.Tab.HOME):LinearLayout{ val (root,body)=GaScreens.page(ui,nav,tab,title,subtitle); show(root); return body }
    private fun label(value:String,size:Float=16f,bold:Boolean=false)=TextView(this).apply{text=value;textSize=size;setTextColor(GaUi.TEXT);setPadding(0,dp(6),0,dp(6));setLineSpacing(0f,1.1f);if(bold){setTypeface(ui.sansBold);setTextColor(Color.WHITE)}}
    private fun input(hintText:String,multiLine:Boolean=false)=ui.input(hintText,multiLine).apply{if(multiLine)minLines=4}
    private fun addButton(root:LinearLayout,title:String,action:()->Unit){root.addView(ui.rowCard(null,title,null,glow=false){action()},LinearLayout.LayoutParams(-1,-2).apply{setMargins(0,dp(6),0,dp(6))})}
    private fun rounded(fill:Int,stroke:Int,width:Int,radius:Int)=GradientDrawable().apply{setColor(fill);cornerRadius=dp(radius).toFloat();if(width>0)setStroke(dp(width),stroke)}
    /** No login needed: ApiClient creates this device's anonymous session on the first request. */
    private fun requireSignedIn():Boolean = true
    private var funnyData: Pair<List<FunnyLaw>,List<FunnyCase>>? = null
    private fun funnyPrefs()=getSharedPreferences("ga_settings",MODE_PRIVATE)
    private fun showFunnyLaws(cases:Boolean=false){ UsageAnalytics.feature(api, "funny_laws"); currentScreen="funny";
        val prefs=funnyPrefs()
        val remembered=prefs.getBoolean("funny_view_remember",false)
        if(!remembered){
            FunnyViewChooser.show(this){useSwipe,remember->
                if(remember) prefs.edit().putBoolean("funny_view_remember",true).putString("funny_view_mode",if(useSwipe)"swipe" else "list").apply()
                openFunnyLaws(cases,useSwipe)
            }
        } else openFunnyLaws(cases, prefs.getString("funny_view_mode","swipe")!="list")
    }
    private fun openFunnyLaws(cases:Boolean, deckMode:Boolean){
        val data=funnyData?:FunnyGeorgiaData.parse(assets.open("funny_georgia.json").bufferedReader().use{it.readText()}).also{funnyData=it}
        val prefs=funnyPrefs()
        show(FunnyGeorgiaScreen(ui,data.first,data.second,{showMenu()},{url->openUrl(url)},cases,GaScreens.bottomNav(ui,nav,GaScreens.Tab.FUNNY),
            shareText={text->shareOut(text)}, initialDeckMode=deckMode,
            onModeChanged={swipe-> if(prefs.getBoolean("funny_view_remember",false)) prefs.edit().putString("funny_view_mode",if(swipe)"swipe" else "list").apply() },
            onAskNextTime={ prefs.edit().putBoolean("funny_view_remember",false).remove("funny_view_mode").apply() }
        ).build())
    }
    private fun showMenu(){ closeDrawer(); val items=HomeDrawerCatalog.items; val overlay=GaScreens.drawer(ui,items,BuildConfig.VERSION_NAME,{item->closeDrawer();onDrawerItem(item)},{closeDrawer()}); drawerView=overlay; addContentView(overlay,ViewGroup.LayoutParams(-1,-1)) }
    private fun closeDrawer(){ drawerView?.let{(it.parent as? ViewGroup)?.removeView(it)}; drawerView=null }
    private fun onDrawerItem(item:HomeDrawerItem){if(item.requiresSignIn&&!requireSignedIn())return;when(item.id){"home"->showHome();"mycase"->showMyCase();"cases"->showCases();"ai"->showTalkToMe();"laws"->showGeorgiaLaws();"loopholes"->showLoopholes();"charges"->showChargeCheck(null,null);"civil"->showCivilCheck(null,null);"motions"->showMotionsHub();"forms"->showLegalForms();"court"->showCourtInfo();"rights"->showKnowYourRights();"citizen"->showCitizenHelpHub();"resources"->showResources();"emergency"->showEmergency();"payments"->showPayment();"settings"->showSettings();"feedback"->showFeedback();"profile"->showAccount();"help"->showMore();"funny"->showFunnyLaws();"prep"->showCourtroomPrep();"paper"->showPaperReader()}}

    // ---------- Talk to Me ----------
    private val talk by lazy { ChatStore.open(this, ChatStore.TALK_KEY) }
    private var chat: GaScreens.Chat? = null
    private val greetingTime = now()
    private fun now():String = SimpleDateFormat("h:mm a", Locale.US).format(Date())
    private fun askFromHome(question:String){ showTalkToMe(); sendTalk(question) }
    private fun showTalkToMe(){ UsageAnalytics.feature(api, "chat"); currentScreen="ai"; val c=GaScreens.talkToMe(ui,nav,{q->sendTalk(q)},listOf(
        "Cite a law" to { chat?.input?.apply{setText("Which Georgia law applies to ");setSelection(text.length);requestFocus()} },
        "Read a document" to { pickSavedDocument("Which document should AI Help read?") { d -> readInAiHelp(d) } },
        "Find a form" to { showLegalForms() },
        "Explain in simple terms" to { if(!talk.hasAnswer()) toast("Ask a question first.") else sendTalk("Explain your last answer in simple terms.") }))
        chat=c; wireChatDelete(c,talk,"ai_help"){ sendTalk(it) }; show(c.root); c.bot("How can I help you today?",greetingTime); talk.messages.forEach{ if(it.mine) c.user(it.text,it.time,it.id) else c.bot(it.text,it.time,it.id) }; continuity(c.messages,0,"ai_help",false) }
    private fun sendTalk(q:String){ val c=chat?:return; if(q.length>4000)return toast("Message is too long. Use 4,000 characters or fewer."); c.input.setText(""); val history=talk.transcript(); val line=talk.add(true,q,now()); c.user(line.text,line.time,line.id); askTalk(c,q,history,line.id) }
    private fun askTalk(c:GaScreens.Chat,q:String,history:String,userId:Long){ val stop=c.progress()
        thread{ try{ val reply=TalkToMeController.reply(api,history,q,languageInstruction()); val text=reply.answer+(if(reply.authoritySummary.isNotBlank())"\n\n"+reply.authoritySummary else ""); runOnUiThread{ stop(); val st=ShareText.answer(q,text); val bot=talk.add(false,text,now(),st); talk.tagTurn(listOf(userId,bot.id),reply.turnId); if(chat===c){c.bot(bot.text,bot.time,bot.id);c.actions({shareOut(st)},{copyOut(st)},{sharePlanPdf("STANDALONE ASSISTANT",st)},{maybeRead(st)});c.findHelp{showFindHelp()};c.followUps(reply.followUps){f->sendTalk(f)};Glossary.button(ui,text)?.let{c.attach(it)};reply.helpResources.forEach{r->c.attach(ui.secondaryButton(r.name+" ›"){openUrl(r.url)}.apply{contentDescription="Open "+r.name});val tel=TalkToMeController.telUri(r.phone);if(tel.isNotEmpty())c.attach(ui.secondaryButton("Call "+r.phone){openUrl(tel)}.apply{contentDescription="Call "+r.name+" at "+r.phone})};if(HelpLovedOne.CUSTODY.containsMatchIn(q))c.attach(ui.secondaryButton("Help your loved one (money, calls, visits) ›"){HelpLovedOne.show(ui){u->openUrl(u)}});if(reply.caseStage.isNotBlank()&&MyCaseScreens.STAGES.any{it.first==reply.caseStage})c.attach(ui.secondaryButton("Open My Case: "+MyCaseScreens.STAGES.first{it.first==reply.caseStage}.second+" ›"){showStage(reply.caseStage,JSONObject().put("situation",situationFor(q)))});c.attach(buildDefenseButton(reply.planStatus=="built")); if(reply.planStatus=="built") c.attach(ui.secondaryButton("Courtroom prep ›"){ showCourtroomPrep() })} } }
        catch(e:Exception){ runOnUiThread{ stop(); val msg=AiErrors.message(e); val bot=talk.add(false,msg,now(),inContext=false); if(chat===c){c.bot(bot.text,bot.time,bot.id); if(AiErrors.isRetryable(e)) c.retry{ talk.delete(bot.id); c.remove(bot.id); askTalk(c,q,history,userId) } } } } } }
    /** "Build my defense": regenerates "Your Defense Plan" for this chat (the request carries the chat so far). */
    private fun buildDefenseButton(rebuild:Boolean)=ui.primaryButton(if(rebuild)"Rebuild my defense plan" else "Build my defense"){ val s=situationFor(talk.messages.lastOrNull{it.mine&&!it.text.startsWith("Build my defense",true)}?.text.orEmpty()); sendTalk(if(s.isBlank())"Build my defense plan" else "Build my defense plan for this: "+s) }.apply{contentDescription=if(rebuild)"Rebuild my defense plan" else "Build my defense plan for this chat"}
    private fun situationFor(q:String)=q.replace(Regex("^Build my defense plan for this:\\s*",RegexOption.IGNORE_CASE),"").take(2000)
    /** Free and low-cost Georgia legal help (URLs checked to load). */
    private val helpLinks=listOf("Georgia Legal Aid (Georgia Legal Services Program)" to "https://www.glsp.org/","Atlanta Legal Aid Society" to "https://atlantalegalaid.org/","Georgia Courts self-help (forms and court help)" to "https://georgiacourts.gov/a2j/","State Bar of Georgia — find a lawyer" to "https://www.gabar.org/public/find-a-lawyer")
    private fun showFindHelp(){ AlertDialog.Builder(this).setTitle("Find legal help").setItems(helpLinks.map{it.first}.toTypedArray()){_,i->openUrl(helpLinks[i].second)}.setNegativeButton("Close",null).show() }
    /** Opens a cited law inside the app (stored text; no external archive links). */
    private fun showLaw(citation:String){ toast("Opening $citation…")
        thread{ try{ val law=GuestPublicApi.law(BuildConfig.API_BASE_URL,citation); runOnUiThread{
                val body=LinearLayout(this).apply{orientation=LinearLayout.VERTICAL;setPadding(dp(20),dp(8),dp(20),dp(8))}
                val t=law.optString("title"); if(t.isNotBlank()&&t!="null")body.addView(label(t,16f,true))
                body.addView(label(law.optString("text").ifBlank{"No text is stored for this law yet."},14f).apply{setTextIsSelectable(true)})
                law.optString("note").takeIf{it.isNotBlank()&&it!="null"}?.let{body.addView(label("Note: "+it,12.5f).apply{setTextColor(GaUi.MUTED)})}
                AlertDialog.Builder(this).setTitle(law.optString("citation",citation)).setView(ScrollView(this).apply{addView(body)}).setPositiveButton("Close",null).show() } }
        catch(e:Exception){ runOnUiThread{ toast(if(e is ApiException&&e.statusCode==404)"That law isn't in STANDALONE ASSISTANT yet." else AiErrors.message(e)) } } } }
    /** One quiet continuity line (+ per-screen Start fresh) at [index] of [container], when there is something to continue. */
    private fun continuity(container:LinearLayout,index:Int,feature:String,showOwn:Boolean,onFresh:()->Unit={}){ thread{ val state=runCatching{api.conversation(feature)}.getOrNull(); val text=ContinuityNote.line(state,showOwn)?:return@thread
        runOnUiThread{ if(container.findViewWithTag<View>("continuity")!=null||container.parent==null)return@runOnUiThread; lateinit var v:View; v=ContinuityNote.view(ui,text){ thread{runCatching{api.startFresh(feature)}}; container.removeView(v); onFresh(); toast("Started fresh on this screen.") }; container.addView(v,minOf(index,container.childCount)) } } }
    private fun wireChatDelete(c:GaScreens.Chat,t:ChatTranscript,feature:String?=null,onAsk:((String)->Unit)?=null){ c.onLawTap={cite->showLaw(cite)}; c.onAsk=onAsk
        c.onMessageLongPress={id->val m=t.messages.firstOrNull{it.id==id}; if(m!=null) AlertDialog.Builder(this).setTitle(if(m.mine)"Your message" else "STANDALONE ASSISTANT answer").setItems(arrayOf("Copy","Share","Delete")){_,i->when(i){0->copyOut(m.shareText);1->shareOut(m.shareText);else->AlertDialog.Builder(this).setTitle("Delete this message?").setMessage("It will be removed from this chat and won't be sent to the AI again. This can't be undone.").setPositiveButton("Delete"){_,_->val turn=t.turnOf(id);t.delete(id);c.remove(id);if(turn>0)thread{runCatching{api.forgetTurn(turn)}};toast("Message deleted.")}.setNegativeButton("Cancel",null).show()}}.show()}
        c.onClearChat={ if(t.messages.isEmpty()&&feature==null) toast("This chat is already empty.") else AlertDialog.Builder(this).setTitle("Start fresh?").setMessage("This chat is cleared from this phone and the AI forgets its earlier questions on this screen. Other screens keep theirs. This can't be undone.").setPositiveButton("Start fresh"){_,_->t.clear();c.clearMessages();c.messages.findViewWithTag<View>("continuity")?.let{c.messages.removeView(it)};if(feature!=null)thread{runCatching{api.startFresh(feature)}};toast("Started fresh.")}.setNegativeButton("Cancel",null).show() } }
    private fun languageCode():String { val saved=getSharedPreferences("ga_settings",MODE_PRIVATE).getString("language","English")?:"English"; return when { saved.startsWith("Español")->"es"; saved.startsWith("中文")->"zh"; saved.startsWith("Français")->"fr"; saved.startsWith("العربية")->"ar"; saved.startsWith("Tiếng Việt")->"vi"; else->"en" } }
    private fun languageInstruction():String = when(languageCode()){
        "es"->"Respond in Spanish. Write every section heading in English exactly as required (for example 'Quick answer' and 'Questions to ask your lawyer'). Keep legal citations (O.C.G.A. sections, case names, court rule numbers, docket numbers and case numbers) exactly as written in the original. End with this disclaimer in Spanish: 'Esto es información legal, no asesoramiento jurídico.'"
        "zh"->"Respond in Simplified Chinese unless quoting an authority that should remain in its original language."
        "fr"->"Respond in French unless quoting an authority that should remain in its original language."
        "ar"->"Respond in Arabic unless quoting an authority that should remain in its original language."
        "vi"->"Respond in Vietnamese unless quoting an authority that should remain in its original language."
        else->"Respond in English."
    }

    // ---------- Charge Check ----------
    private fun showChargeCheck(caseId:Int?,caseTitle:String?,prefill:String?=null){ UsageAnalytics.feature(api, "case_check"); currentScreen="charges"; if(!requireSignedIn())return; lateinit var form:GaScreens.ChargeCheckForm; form=GaScreens.chargeCheck(ui,nav,caseTitle){t->runChargeCheck(form,t,caseId)}; show(form.root); (form.results.parent as? LinearLayout)?.let{continuity(it,2,"charge_check",prefill.isNullOrBlank())}; if(!prefill.isNullOrBlank()){form.situation.setText(prefill);runChargeCheck(form,prefill,caseId)} }
    private fun options(arr:JSONArray?,labelKey:String?)=(0 until (arr?.length()?:0)).mapNotNull{i->arr!!.optJSONObject(i)?.let{o->GaScreens.ChargeOption(labelKey?.let{k->clean(o.optString(k))}?.ifBlank{null},o.optString("title"),o.optString("explanation"),cites(o.optJSONArray("citations")))}}
    private fun runChargeCheck(form:GaScreens.ChargeCheckForm,raw:String,caseId:Int?){ val situation=raw.trim(); if(situation.isEmpty()&&caseId==null)return toast("Describe what happened."); if(situation.length>4000)return toast("Description is too long. Use 4,000 characters or fewer."); GaScreens.loopholesLoading(ui,form.results, LoadingLines.CHARGE)
        thread{ try{ val r=api.chargeCheck(situation,caseId); val ch=r.optJSONArray("charges")
            val charges=(0 until (ch?.length()?:0)).mapNotNull{i->ch!!.optJSONObject(i)?.let{o->val c=o.optJSONObject("citation")?:return@let null;GaScreens.ChargeItem(o.optString("charge"),o.optString("level_label"),clean(o.optString("penalty")).ifBlank{null},clean(o.optString("penalty_note")).ifBlank{null},o.optString("why"),GaScreens.LoopholeCite(c.optString("citation"),clean(c.optString("title")),clean(c.optString("source_url")).ifBlank{null}))}}
            val em=r.optJSONObject("emergency")?.optJSONArray("resources"); val emergency=(0 until (em?.length()?:0)).mapNotNull{i->em!!.optJSONObject(i)?.let{o->o.optString("label") to o.optString("contact")}}
            val result=GaScreens.ChargeCheckResult(charges,options(r.optJSONArray("defenses"),"kind_label"),options(r.optJSONArray("lowest_outcome"),null),lawyerTake(r),clean(r.optString("message")).ifBlank{null},r.optBoolean("refused"),r.optString("estimate_note"),r.optString("rights_reminder"),r.optString("disclaimer",GaScreens.CHARGE_DISCLAIMER),emergency,if(r.isNull("case_id"))null else r.optInt("case_id"))
            val shareText=ShareText.chargeCheck(situation,result)
            runOnUiThread{ GaScreens.renderChargeCheck(ui,form.results,result,{shareOut(shareText)} to {copyOut(shareText)},{n->dial(n)}){c->showLaw(c.citation.replace(Regex("\\s*\\(text as of[^)]*\\)"),""))} }
        }catch(e:Exception){ runOnUiThread{ form.results.removeAllViews(); form.results.addView(ui.emptyCard(R.drawable.ga_ic_error,"Couldn’t check charges",AiErrors.message(e)),ui.lp(4,4)); if(AiErrors.isRetryable(e)) form.results.addView(ui.primaryButton("Retry"){runChargeCheck(form,raw,caseId)},ui.lp(6,6)) } } } }

    // ---------- Civil Case Check ----------
    private fun showCivilCheck(caseId:Int?,caseTitle:String?){ UsageAnalytics.feature(api, "case_check"); currentScreen="civil"; if(!requireSignedIn())return; lateinit var form:GaScreens.ChargeCheckForm; form=GaScreens.civilCheck(ui,nav,caseTitle){t->runCivilCheck(form,t,caseId)}; show(form.root); (form.results.parent as? LinearLayout)?.let{continuity(it,2,"civil_check",true)} }
    private fun noAsOf(s:String)=s.replace(Regex("\\s*\\(text as of[^)]*\\)"),"").trim()
    private fun cite1(o:JSONObject?)=o?.let{c->GaScreens.LoopholeCite(noAsOf(c.optString("citation")),clean(c.optString("title")),clean(c.optString("source_url")).ifBlank{null})}
    private fun runCivilCheck(form:GaScreens.ChargeCheckForm,raw:String,caseId:Int?){ val situation=raw.trim(); if(situation.isEmpty()&&caseId==null)return toast("Describe the dispute."); if(situation.length>4000)return toast("Description is too long. Use 4,000 characters or fewer."); GaScreens.loopholesLoading(ui,form.results, LoadingLines.CIVIL)
        thread{ try{ val r=api.civilCheck(situation,caseId)
            fun arr(k:String)=r.optJSONArray(k)?.let{a->(0 until a.length()).mapNotNull{a.optJSONObject(it)}}?:emptyList()
            val claims=arr("claims").mapNotNull{o->cite1(o.optJSONObject("citation"))?.let{c->GaScreens.CivilClaim(o.optString("side_label"),o.optString("claim"),o.optString("why"),c)}}
            val court=r.optJSONObject("court")?.let{o->GaScreens.CivilCourt(o.optString("court_label"),clean(o.optString("why")),clean(o.optString("limit")).ifBlank{null},clean(o.optString("note")).ifBlank{null},cite1(o.optJSONObject("citation")))}
            val deadlines=arr("deadlines").mapNotNull{o->cite1(o.optJSONObject("citation"))?.let{c->GaScreens.CivilDeadline(o.optString("title"),o.optString("quote"),c)}}
            val evidence=r.optJSONArray("evidence")?.let{a->(0 until a.length()).map{a.optString(it)}.filter{it.isNotBlank()}}?:emptyList()
            val help=arr("help_resources").map{GaScreens.HelpLink(it.optString("title"),it.optString("url"))}.filter{it.url.startsWith("https://")}
            val em=r.optJSONObject("emergency")?.optJSONArray("resources"); val emergency=(0 until (em?.length()?:0)).mapNotNull{i->em!!.optJSONObject(i)?.let{o->o.optString("label") to o.optString("contact")}}
            val result=GaScreens.CivilCheckResult(claims,court,deadlines,evidence,options(r.optJSONArray("weak_spots"),"side_label"),options(r.optJSONArray("low_cost_paths"),null),help,lawyerTake(r),clean(r.optString("message")).ifBlank{null},r.optBoolean("refused"),r.optString("estimate_note"),r.optString("disclaimer",GaScreens.CIVIL_DISCLAIMER),emergency,if(r.isNull("case_id"))null else r.optInt("case_id"))
            val shareText=ShareText.civilCheck(situation,result)
            runOnUiThread{ GaScreens.renderCivilCheck(ui,form.results,result,{shareOut(shareText)} to {copyOut(shareText)},{n->dial(n)},{u->openUrl(u)}){c->showLaw(c.citation.replace(Regex("\\s*\\(text as of[^)]*\\)"),""))} }
        }catch(e:Exception){ runOnUiThread{ form.results.removeAllViews(); form.results.addView(ui.emptyCard(R.drawable.ga_ic_error,"Couldn’t check that",AiErrors.message(e)),ui.lp(4,4)); if(AiErrors.isRetryable(e)) form.results.addView(ui.primaryButton("Retry"){runCivilCheck(form,raw,caseId)},ui.lp(6,6)) } } } }

    // ---------- Legal Loopholes ----------
    private val loopholeChips = listOf("Self-defense","Landlord security deposits","DUI","Traffic stops","Expungement","Eviction notice")
    private fun showLoopholes(prefill:String?=null){ if(!requireSignedIn())return; lateinit var form:GaScreens.LoopholesForm; form=GaScreens.loopholes(ui,nav,loopholeChips){t->analyzeLoopholes(form,t)}; show(form.root); (form.results.parent as? LinearLayout)?.let{continuity(it,2,"loopholes",prefill.isNullOrBlank())}; if(!prefill.isNullOrBlank()){val t=prefill.take(300);form.topic.setText(t);analyzeLoopholes(form,t)} }
    // ---------------- My Case hub ----------------
    private fun savedCases():List<JSONObject> = runCatching{ val a=JSONArray(getSharedPreferences("ga_settings",MODE_PRIVATE).getString("my_cases","[]")); (0 until a.length()).map{a.getJSONObject(it)} }.getOrDefault(emptyList())
    private fun storeCases(list:List<JSONObject>){ getSharedPreferences("ga_settings",MODE_PRIVATE).edit().putString("my_cases",JSONArray(list).toString()).apply() }
    private fun showMyCase(){ UsageAnalytics.feature(api, "case_check"); currentScreen="mycase"; show(MyCaseScreens.hub(ui,nav,savedCases(),{k->when(k){"criminal"->showStages();"civil"->showCivilCheck(null,null);else->showTalkToMe()}},{s->showStage(s.optString("stage"),s.optJSONObject("details"))},{s->AlertDialog.Builder(this).setTitle("Delete saved case?").setPositiveButton("Delete"){_,_->storeCases(savedCases().filter{it.optString("id")!=s.optString("id")});showMyCase()}.setNegativeButton("Cancel",null).show()})) }
    private fun showStages(){ show(MyCaseScreens.stages(ui,nav){st->showStage(st,null)}) }
    private fun showStage(stage:String,prefill:JSONObject?){ lateinit var form:MyCaseScreens.StageForm; form=MyCaseScreens.stageForm(ui,nav,stage,prefill){runGuide(form,stage)}; show(form.root); if(prefill!=null&&(prefill.optString("situation").isNotBlank()||prefill.length()>1))runGuide(form,stage) }
    private val guideAnswers=JSONObject()
    private fun runGuide(form:MyCaseScreens.StageForm,stage:String){ val details=JSONObject().put("situation",form.situation.text.toString().trim().take(2000)); form.dates.forEach{(k,v)->val d=v.text.toString().trim(); if(d.isNotBlank())details.put(k,d)}
        GaScreens.loopholesLoading(ui,form.results, LoadingLines.LOOPHOLES)
        thread{ try{ val g=GuestPublicApi.caseGuide(BuildConfig.API_BASE_URL,stage,details,guideAnswers); runOnUiThread{ MyCaseScreens.render(ui,form.results,g,stage,MyCaseScreens.Callbacks(
                {showChargeCheck(null,null,details.optString("situation").ifBlank{null})},{showLoopholes(details.optString("situation").ifBlank{MyCaseScreens.STAGES.first{it.first==stage}.second})},{saveCase(stage,details)},{u->openUrl(u)},
                {id,v->guideAnswers.put(id,v);runGuide(form,stage)},{key,title->showDraft(key,title,details)},{title,due->remindDeadline(title,due)})) } }
        catch(e:Exception){ runOnUiThread{ form.results.removeAllViews(); toast(AiErrors.message(e)) } } } }
    private fun showDraft(key:String,title:String,details:JSONObject){ toast("Preparing a draft…")
        thread{ try{ val d=GuestPublicApi.motionDraft(BuildConfig.API_BASE_URL,key,details); val text=d.optString("text"); runOnUiThread{
                val (root,body)=GaScreens.page(ui,nav,GaScreens.Tab.LAWS,title,"Fill-in-the-blank template. Review with a lawyer before filing.")
                body.addView(ui.text(text,13f,GaUi.TEXT).apply{typeface=android.graphics.Typeface.MONOSPACE;setTextIsSelectable(true);setPadding(dp(12),dp(12),dp(12),dp(12));background=ui.glowCard(GaUi.CARD,GaUi.STROKE_SOFT,12,glow=false)},ui.lp(6,8))
                body.addView(ui.primaryButton("Share as PDF"){runCatching{MotionDrafts.sharePdf(this,title,text)}.onFailure{toast("Couldn't create the PDF.")}},ui.lp(4,4))
                body.addView(ui.secondaryButton("Share as text"){MotionDrafts.shareText(this,title,text)},ui.lp(4,4))
                body.addView(ui.secondaryButton("Copy"){copyOut(text)},ui.lp(4,8))
                show(root) } }
        catch(e:Exception){ runOnUiThread{ toast(AiErrors.message(e)) } } } }
    private fun remindDeadline(title:String,due:String){ if(android.os.Build.VERSION.SDK_INT>=33&&checkSelfPermission(android.Manifest.permission.POST_NOTIFICATIONS)!=android.content.pm.PackageManager.PERMISSION_GRANTED)requestPermissions(arrayOf(android.Manifest.permission.POST_NOTIFICATIONS),41)
        val n=DeadlineReminders.schedule(this,title,due); toast(if(n>0)"Reminders set for $due (7 days before, 1 day before and that day)." else "That date has already passed.") }
    private fun saveCase(stage:String,details:JSONObject){ val name=details.optString("situation").take(40).ifBlank{MyCaseScreens.STAGES.first{it.first==stage}.second}; val id=System.currentTimeMillis().toString()
        storeCases(listOf(JSONObject().put("id",id).put("name",name).put("stage",stage).put("details",details).put("saved_at",java.text.SimpleDateFormat("MMM d, yyyy",java.util.Locale.US).format(java.util.Date())))+savedCases().take(19)); toast("Case saved on this phone.") }
    private fun cites(arr:JSONArray?)=(0 until (arr?.length()?:0)).mapNotNull{i->arr!!.optJSONObject(i)?.let{o->GaScreens.LoopholeCite(noAsOf(o.optString("citation")),clean(o.optString("title")),clean(o.optString("source_url")).ifBlank{null})}}
    private fun lawyerTake(r:JSONObject)=r.optJSONObject("lawyer_take")?.let{o->GaScreens.LawyerTake(o.optString("label","If I Was Your Lawyer, I Would Say"),o.optString("text"),o.optString("disclaimer","Not legal advice — this app is not your lawyer."),cites(o.optJSONArray("citations")))}?.takeIf{it.text.isNotBlank()}
    private fun analyzeLoopholes(form:GaScreens.LoopholesForm,raw:String){ val topic=raw.trim(); if(topic.isEmpty())return toast("Enter a Georgia legal topic."); if(topic.length>300)return toast("Topic is too long. Use 300 characters or fewer."); GaScreens.loopholesLoading(ui,form.results, LoadingLines.LOOPHOLES)
        thread{ try{ val r=api.loopholes(topic); val arr=r.optJSONArray("findings"); val findings=(0 until (arr?.length()?:0)).mapNotNull{i->arr!!.optJSONObject(i)?.let{o->GaScreens.LoopholeFinding(o.optString("type_label"),o.optString("title"),o.optString("explanation"),cites(o.optJSONArray("citations")))}}
            val lt=lawyerTake(r)
            val msg=clean(r.optString("message")).ifBlank{null}
            val refused=r.optBoolean("refused"); val shareText=ShareText.loopholes(topic,findings,lt)
            runOnUiThread{ GaScreens.renderLoopholes(ui,form.results,findings,msg,lt,refused,{shareOut(shareText)} to {copyOut(shareText)}){c->showLaw(c.citation.replace(Regex("\\s*\\(text as of[^)]*\\)"),""))} } }
        catch(e:Exception){ runOnUiThread{ form.results.removeAllViews(); form.results.addView(ui.emptyCard(R.drawable.ga_ic_error,"Couldn’t analyze that",e.message?:"Something went wrong. Please try again."),ui.lp(4,4)) } } } }

    // ---------- My Cases ----------
    private var casesFilter = 0
    private var casesQuery = ""
    private var casesCache: List<GaScreens.CaseRow>? = null
    private fun caseRows(cases:JSONArray)=(0 until cases.length()).mapNotNull{i->cases.optJSONObject(i)?.let{o->val id=o.optInt("id");GaScreens.CaseRow(id,o.optString("title","Case #$id"),clean(o.optString("county")),clean(o.optString("case_type")),clean(o.optString("stage")))}}
    private fun clean(v:String)=if(v=="null")"" else v.trim()
    private fun showCases(){if(!requireSignedIn())return; UsageAnalytics.feature(api, "case_check"); currentScreen="cases"; renderCases(); runTask("Loading cases…",{showCases()}){val rows=caseRows(api.cases());runOnUiThread{casesCache=rows;renderCases()}}}
    private fun renderCases(){ show(GaScreens.myCases(ui,nav,casesCache,casesFilter,casesQuery,{casesFilter=it;renderCases()},{casesQuery=it;renderCases()},{showCase(it)},{showCreateCase()})) }

    // ---------- Documents ----------
    private var docsTab = 0
    private var docsSortByName = false
    private var docsCache: List<GaScreens.DocRow>? = null
    private fun localDocRows()=docs.list().map{d->GaScreens.DocRow(-1,"",d.name,d.mime,SimpleDateFormat("MMM d, yyyy",Locale.US).format(Date(d.addedAt)),humanSize(d.bytes)+(if(d.pages.size>1)" • ${d.pages.size} pages" else "")+(if(d.caseIds.isNotEmpty())" • in case" else ""),d.id)}
    private fun showDocuments(){if(!requireSignedIn())return; UsageAnalytics.feature(api, "uploads"); currentScreen="documents"; val local=localDocRows(); docsCache=local; renderDocuments(); thread{try{val cases=caseRows(api.cases());casesCache=cases;val server=cases.flatMap{c->val ev=api.evidence(c.id);(0 until ev.length()).mapNotNull{i->ev.optJSONObject(i)?.let{o->GaScreens.DocRow(c.id,c.title,o.optString("filename","Document"),clean(o.optString("media_type")),shortDate(clean(o.optString("uploaded_at"))),humanSize(o.optLong("bytes",o.optLong("size_bytes",-1)))+" • "+c.title)}}};runOnUiThread{docsCache=local+server;renderDocuments()}}catch(e:Exception){runOnUiThread{if(local.isEmpty())toast(AiErrors.message(e))}}}}
    private fun renderDocuments(){ val rows=docsCache?.let{ if(docsSortByName) it.sortedBy{d->d.name.lowercase()} else it }; show(GaScreens.documents(ui,nav,docsTab,rows,{docsTab=it;renderDocuments()},{chooseNewDocument()},{docsSortByName=!docsSortByName;toast(if(docsSortByName)"Sorted by name" else "Sorted by case");renderDocuments()},{d->if(d.docId!=null)docs.get(d.docId)?.let{documentActions(it)} else showCaseDocuments(d.caseId)})) }
    private fun shortDate(iso:String):String = runCatching{ SimpleDateFormat("MMM d, yyyy",Locale.US).format(SimpleDateFormat("yyyy-MM-dd",Locale.US).parse(iso.take(10))!!) }.getOrDefault("")
    private fun humanSize(bytes:Long):String = when{ bytes<0->""; bytes<1024->"$bytes B"; bytes<1024*1024->"${bytes/1024} KB"; else->String.format(Locale.US,"%.1f MB",bytes/1048576.0) }

    // ---------- Georgia Laws ----------
    private var lawsTab = 0
    private var lawsTitle: Int? = null
    private var lawsChapter: Int? = null
    private fun recentSearches():List<String> = runCatching{ val a=JSONArray(getSharedPreferences("ga_settings",MODE_PRIVATE).getString("law_recent","[]")); (0 until a.length()).map{a.getString(it)} }.getOrDefault(emptyList())
    private fun rememberSearch(q:String){ val list=(listOf(q)+recentSearches().filter{it!=q}).take(5); getSharedPreferences("ga_settings",MODE_PRIVATE).edit().putString("law_recent",JSONArray(list).toString()).apply() }
    private fun showGeorgiaLaws(){ val titleLabel=lawsTitle?.let{n->"Title $n · "+(GeorgiaLawTitles.codeTitles.firstOrNull{it.first==n}?.second?:"")}?:"All Titles"; val chapterLabel=lawsChapter?.let{"Chapter $it"}?:"All Chapters"
        lateinit var form:GaScreens.LawsForm
        form=GaScreens.georgiaLaws(ui,nav,lawsTab,titleLabel,chapterLabel,recentSearches(),{lawsTab=it;showGeorgiaLaws()},{pickTitle()},{pickChapter()},{runLawSearch(form)},{r->form.search.setText(r);form.keyword.setText("");runLawSearch(form)})
        show(form.root) }
    private fun pickTitle(){ val opts=listOf("All Titles")+GeorgiaLawTitles.codeTitles.map{"Title ${it.first} · ${it.second}"}; AlertDialog.Builder(this).setTitle("Title").setItems(opts.toTypedArray()){_,i->lawsTitle=if(i==0)null else GeorgiaLawTitles.codeTitles[i-1].first;lawsChapter=null;showGeorgiaLaws()}.show() }
    private fun pickChapter(){ if(lawsTitle==null)return toast("Choose a title first."); val opts=listOf("All Chapters")+(1..60).map{"Chapter $it"}; AlertDialog.Builder(this).setTitle("Chapter").setItems(opts.toTypedArray()){_,i->lawsChapter=if(i==0)null else i;showGeorgiaLaws()}.show() }
    private fun runLawSearch(form:GaScreens.LawsForm){ val q=listOf(form.search.text.toString().trim(),form.keyword.text.toString().trim()).filter{it.isNotBlank()}.joinToString(" "); val kind=when(lawsTab){1->"case_law";2->"court_rules";else->"statutes"}; val title=if(lawsTab==0)lawsTitle?.toString().orEmpty() else ""; val chapter=if(lawsTab==0&&lawsTitle!=null)lawsChapter?.toString().orEmpty() else ""
        if(q.isBlank()&&title.isBlank())return toast("Enter a keyword or choose a title.")
        GaScreens.renderLawResults(ui,form.results,null,"Searching Georgia law…"){}
        thread{ try{ val res=GuestPublicApi.lawSearch(BuildConfig.API_BASE_URL,kind,q,title,chapter); val items=res.optJSONArray("items")?:JSONArray(); val hits=(0 until items.length()).mapNotNull{i->items.optJSONObject(i)?.let{o->GaScreens.LawHit(o.optString("citation"),clean(o.optString("title")),o.optString("record_type"),clean(o.optString("excerpt")),clean(o.optString("source_url")).takeIf{it.startsWith("https://")},o.optLong("id").takeIf{it>0})}}
            runOnUiThread{ if(q.isNotBlank())rememberSearch(q); GaScreens.renderLawResults(ui,form.results,hits,res.optString("coverage_notice").takeIf{it.isNotBlank()}){h->if(h.sourceUrl!=null)openUrl(h.sourceUrl) else toast("No official link is stored for this record.")} } }
        catch(e:Exception){ runOnUiThread{ GaScreens.renderLawResults(ui,form.results,null,e.message?:"Something went wrong. Please try again."){} } } } }

    // ---------- Emergency ----------
    private fun showEmergency(){ show(GaScreens.emergency(ui,nav,{dial("911")},listOf(
        GaScreens.Row(R.drawable.ga_ic_location_on,"Find someone in jail or prison","GDC + county jail lookups"){showCitizenFeature("inmate_lookup")},
        GaScreens.Row(R.drawable.ga_ic_person,"Ask for a public defender","How to request appointed counsel"){showCitizenFeature("public_defender")},
        GaScreens.Row(R.drawable.ga_ic_volunteer_activism,"Victim Resources","Support and services"){openUrl("https://cjcc.georgia.gov/victims-compensation")},
        GaScreens.Row(R.drawable.ga_ic_monitor_heart,"Mental Health Support","24/7 crisis help — call or text 988"){dial("988")},
        GaScreens.Row(R.drawable.ga_ic_error,"Report a Rights Violation","File a complaint"){openUrl("https://civilrights.justice.gov/")},
        GaScreens.Row(R.drawable.ga_ic_warning,"Other Emergency Resources","Food, shelter, and more — dial 211"){dial("211")}))) }
    private fun dial(number:String){ runCatching{startActivity(Intent(Intent.ACTION_DIAL,Uri.parse("tel:$number")))}.onFailure{toast("Dial $number from your phone.")} }

    // ---------- Motions & Legal Work ----------
    private fun showMotionsHub(){ UsageAnalytics.feature(api, "motion_maker"); currentScreen="motions"; if(!requireSignedIn())return; show(GaScreens.motions(ui,nav,listOf(
        GaScreens.Row(R.drawable.ga_ic_description,"Generate a Motion","Create customized legal motions"){chooseCase("Generate a Motion"){showMotionScreen(it)}},
        GaScreens.Row(R.drawable.ga_ic_library_books,"Motion filing coach","Fee waiver, e-file links, mail & prison path"){showCitizenFeature("filing_coach")},
        GaScreens.Row(R.drawable.ga_ic_library_books,"Motion Library","Browse common motions"){startActivity(Intent(this,InternalLegalSearchActivity::class.java).putExtra("mode","motions").putExtra("title","Motion Library"))},
        GaScreens.Row(R.drawable.ga_ic_edit_square,"Legal Writing Help","Improve or review your drafts"){comingSoon("Legal Writing Help","Draft review is not available yet. You can ask Talk to Me about a specific issue in the meantime.",GaScreens.Tab.LEGAL_WORK){showMotionsHub()}},
        GaScreens.Row(R.drawable.ga_ic_sms,"Ask STANDALONE ASSISTANT\nabout my situation","Get personalized guidance"){showTalkToMe()}))) }
    private fun chooseCase(title:String,then:(Int)->Unit){ runTask("Loading cases…",{showMotionsHub()}){val cases=caseRows(api.cases());runOnUiThread{ if(cases.isEmpty()){toast("Create a case first.");showCreateCase()} else if(cases.size==1)then(cases[0].id) else AlertDialog.Builder(this).setTitle(title).setItems(cases.map{it.title}.toTypedArray()){_,i->then(cases[i].id)}.show() }} }
    private fun comingSoon(title:String,body:String,tab:GaScreens.Tab=GaScreens.Tab.MORE,back:()->Unit={showHome()}){ show(GaScreens.comingSoon(ui,nav,tab,title,body,back)) }

    // ---------- Account / Profile ----------
    private fun showAccount(){if(api.isAnonymous)return showAnonymousAccount(); val prefs=getSharedPreferences("ga_settings",MODE_PRIVATE); renderProfile(prefs.getString("profile_email","").orEmpty()); runTask("Loading account…",{showAccount()}){val me=api.me();val email=me.optString("email");prefs.edit().putString("profile_email",email).apply();runOnUiThread{renderProfile(email)}}}
    /** Account tab without an account: what is saved, optional sign-in, and delete-my-data. */
    private fun showAnonymousAccount(){ val root=page("Account","No sign-in needed. STANDALONE ASSISTANT is ready to use.",GaScreens.Tab.ACCOUNT)
        root.addView(label("You're using STANDALONE ASSISTANT without an account. Your cases, Case Chat, Charge Check results and documents are saved to this phone's private anonymous ID. No name, email or phone number is required.",15f))
        addButton(root,"Sign in or create an account (optional)"){startActivity(Intent(this,AuthActivity::class.java))}
        addButton(root,"My Cases"){showCases()}
        addButton(root,"Privacy Policy"){openUrl(privacyUrl())}
        addButton(root,"Delete my data"){confirmDeleteAccount()}
        root.addView(ui.note("Signing in to an account is separate from this device's anonymous data. Uninstalling the app or clearing its storage loses access to the anonymous data; use Delete my data first if you want it removed from our server.")) }
    private fun renderProfile(email:String){ val prefs=getSharedPreferences("ga_settings",MODE_PRIVATE); show(GaScreens.profile(ui,nav,prefs.getString("profile_name","").orEmpty(),email,prefs.getString("profile_phone","").orEmpty(),{toast("Profile photos are coming soon.")}){name,phone->prefs.edit().putString("profile_name",name).putString("profile_phone",phone).apply();toast("Profile saved on this device.")}) }

    // ---------- Payment (free launch) ----------
    private fun showPayment(){ show(GaScreens.payment(ui,nav,"Free Launch","\$0 — free during launch",listOf("Full access to all features","Georgia law search & Talk to Me","Private cases & documents (sign-in)","Case analysis tools"),
        {toast("Paid plans aren’t offered during the free launch. Everything is free.")},{toast("No payment method is needed during the free launch.")},{toast("No billing history — you have not been charged.")})) }


    private fun maybeAskFeedback(){
        if(askedFeedbackPrompt||!UsageAnalytics.promptDue(this))return
        askedFeedbackPrompt=true
        AlertDialog.Builder(this)
            .setTitle("How's the app so far?")
            .setMessage("A 10-second rating helps us improve STANDALONE ASSISTANT. You can skip this.")
            .setPositiveButton("Rate the app"){_,_->UsageAnalytics.markPromptSeen(this);showFeedback()}
            .setNegativeButton("Not now"){_,_->UsageAnalytics.markPromptSeen(this)}
            .setOnCancelListener{UsageAnalytics.markPromptSeen(this)}
            .show()
    }
    private fun showFeedback(){
        currentScreen="feedback"
        val root=page("Help us improve","Tell us about the app itself — a bug, the design, or an idea. Legal questions still go to Talk to Me.",GaScreens.Tab.MORE)
        var rating:Int?=null
        val stars=LinearLayout(this).apply{orientation=LinearLayout.HORIZONTAL;gravity=Gravity.CENTER_VERTICAL}
        val starViews=mutableListOf<TextView>()
        fun paint(){starViews.forEachIndexed{i,v->v.setTextColor(if(rating!=null&&rating!!>i)GaUi.GOLD else GaUi.MUTED)}}
        repeat(5){n->
            val star=TextView(this).apply{text="★";textSize=28f;setPadding(dp(6),dp(8),dp(6),dp(8));setTextColor(GaUi.MUTED);setOnClickListener{rating=n+1;paint()};contentDescription="${n+1} star${if(n==0)"" else "s"}"}
            starViews+=star;stars.addView(star)
        }
        root.addView(label("How is the app overall? (optional)",14f))
        root.addView(stars)
        val group=RadioGroup(this)
        UsageAnalytics.CATEGORIES.forEach{(id,title)->
            group.addView(RadioButton(this).apply{this.id=View.generateViewId();text=title;tag=id;setTextColor(Color.WHITE);if(id=="idea")isChecked=true})
        }
        root.addView(label("What's this about?",14f))
        root.addView(group)
        val comment=input("What could be better?",true)
        val email=input("Email if you want a reply (optional)")
        root.addView(comment);root.addView(email)
        val status=label("",14f).apply{setTextColor(GaUi.GOLD)}
        root.addView(status)
        addButton(root,"Send feedback"){
            val cat=(group.findViewById<RadioButton>(group.checkedRadioButtonId)?.tag as? String)?:"other"
            val err=UsageAnalytics.validateFeedback(rating,cat,comment.text.toString(),email.text.toString())
            if(err!=null){status.text=err;return@addButton}
            status.text="Sending…"
            thread{
                try{
                    api.sendFeedback(rating,cat,comment.text.toString(),email.text.toString(),currentScreen)
                    UsageAnalytics.markFeedbackSent(this@HomeActivity)
                    runOnUiThread{toast("Thank you. Your feedback helps us improve STANDALONE ASSISTANT.");showHome()}
                }catch(e:Exception){runOnUiThread{status.text=e.message?:"Feedback could not be sent. Please try again."}}
            }
        }
    }


    private fun translatePaperReading(c:GaScreens.Chat, original:org.json.JSONObject){
        val stop=c.progress(listOf("Translating to Spanish…"))
        thread { try {
            val r=api.translateDocument(original)
            val answer=r.optString("answer")
            runOnUiThread {
                stop()
                val bot=talk.add(false, answer, now(), ShareText.answer("Spanish translation", answer))
                if(chat===c){ c.bot(bot.text, bot.time, bot.id)
                    c.attach(ui.secondaryButton("Share as PDF"){ sharePlanPdf("Traducción del papel", answer) })
                    if(ReadAloud.saved(this)!=ReadAloud.OFF) c.attach(ui.secondaryButton("Read aloud"){ ReadAloud.speak(this, answer, "es") })
                    c.attach(buildDefenseButton(true))
                    c.attach(ui.secondaryButton("Courtroom prep ›"){ showCourtroomPrep(r.optJSONObject("defense_plan")?.optString("case_type")) })
                }
            }
        } catch(e:Exception){ runOnUiThread { stop(); toast(AiErrors.message(e)) } } }
    }

    // ---------- Settings ----------
    private fun showSettings(){ show(GaScreens.settings(ui,nav,true,voiceLabel()){row->when(row){0->pickLanguage();1->pickVoice();2->toast("STANDALONE ASSISTANT uses the dark navy theme.");3->showCitizenFeature("court_dates");4->showPrivacy();5->confirmClearData();6->showFeedback();else->AlertDialog.Builder(this).setTitle("About STANDALONE ASSISTANT").setMessage("Version ${BuildConfig.VERSION_NAME}\n\nClear answers. A stronger Georgia.\n\nSTANDALONE ASSISTANT provides general legal information, not legal advice, and does not create an attorney-client relationship. Questions sent to AI features may be processed by third-party AI providers; some free providers may use them to improve their models, so do not enter sensitive personal information.\n\nContact: davidgoldberg6060@gmail.com\n\n© 2026 Treyvon Pattillo. All rights reserved.").setPositiveButton("OK",null).show()}}) }
    private fun privacyUrl()=BuildConfig.API_BASE_URL.trimEnd('/')+"/privacy"
    private fun showPrivacy(){ val root=page("Privacy & Security","How this app protects your information.",GaScreens.Tab.MORE); root.addView(label("Your sign-in session is stored with Android encrypted storage on this device. My Cases, Documents and case analysis require sign-in, and your uploads are stored in your private case workspace with an integrity hash. Guest questions do not require an account.",15f)); addButton(root,"Read the Privacy Policy"){openUrl(privacyUrl())}; if(api.isAnonymous){ addButton(root,"Delete my data"){confirmDeleteAccount()} } else { addButton(root,"Sign out of this device"){logOutFromDrawer()}; addButton(root,"Delete Account"){confirmDeleteAccount()} } }
    private fun confirmDeleteAccount(){ val anon=api.isAnonymous; val box=LinearLayout(this).apply{orientation=LinearLayout.VERTICAL;setPadding(dp(20),dp(4),dp(20),0)}; val pw=EditText(this).apply{hint="Your password";inputType=android.text.InputType.TYPE_CLASS_TEXT or android.text.InputType.TYPE_TEXT_VARIATION_PASSWORD}; val word=EditText(this).apply{hint="Type DELETE to confirm"}; if(!anon)box.addView(pw); box.addView(word)
        AlertDialog.Builder(this).setTitle(if(anon)"Delete my data?" else "Delete your account?").setMessage(if(anon)"This permanently deletes this device's anonymous record and all of its cases, notes, analyses and uploaded files from STANDALONE ASSISTANT. This cannot be undone." else "This permanently deletes your account, all of your cases, notes, timeline events, analyses and uploaded files from STANDALONE ASSISTANT. This cannot be undone.").setView(box).setPositiveButton("Delete forever"){_,_->
            if(word.text.toString().trim().uppercase()!="DELETE")return@setPositiveButton toast("Type DELETE to confirm."); val password=pw.text.toString(); if(!anon&&password.isEmpty())return@setPositiveButton toast("Enter your password.")
            thread{ try{ api.deleteAccount(password); ChatStore.wipeAll(this); runOnUiThread{ getSharedPreferences("ga_settings",MODE_PRIVATE).edit().clear().apply(); toast(if(anon)"Your data was deleted." else "Your account and data were deleted."); showHome() } } catch(e:Exception){ runOnUiThread{ toast(e.message?:"Account could not be deleted. Please try again.") } } } }.setNegativeButton("Cancel",null).show() }
    private fun voiceLabel():String = when(ReadAloud.saved(this)){ ReadAloud.BUTLER->"The Butler"; ReadAloud.NANNY->"The Nanny"; else->"Off" }
    private fun pickVoice(){
        val opts=arrayOf("Off","The Butler — a refined, warm, older British voice (original)","The Nanny — a chatty, warm New York voice (original)")
        val ids=arrayOf(ReadAloud.OFF, ReadAloud.BUTLER, ReadAloud.NANNY)
        AlertDialog.Builder(this).setTitle("Read aloud voice").setItems(opts){_,i->
            ReadAloud.save(this, ids[i]); toast(if(ids[i]==ReadAloud.OFF) "Read aloud is off." else "Read aloud voice: "+voiceLabel()+". These are original device voices, not a copy of any person or character.")
        }.setMessage("Uses the free voices already on this phone. Legal wording stays the same, and the not-legal-advice notice is always read.").show()
    }
    private fun sharePlanPdf(title:String,text:String){ runCatching{ MotionDrafts.sharePdf(this,title,planPdfText(title,text)) }.onFailure{ toast("Couldn't create the PDF.") } }
    private fun planPdfText(title:String,text:String):String {
        val notice=if(languageCode()=="es") ReadAloud.NOTICE_ES else ReadAloud.NOTICE_EN
        var out="STANDALONE ASSISTANT\nGeorgia legal information\n$title\n\n"+text.trim()
        if(!out.contains(notice)) out+="\n\n"+notice
        return out+"\nThis document is for personal use. It is not a court filing.\n"
    }
    private fun maybeRead(text:String){ if(ReadAloud.saved(this)==ReadAloud.OFF) toast("Turn on a Read aloud voice in Settings first.") else ReadAloud.speak(this,text,languageCode()) }
    private fun courtroomJson():String = assets.open("courtroom_prep.json").bufferedReader().use{it.readText()}
    private fun showCourtroomPrep(caseType:String?=null){
        UsageAnalytics.feature(api,"find_legal_help"); currentScreen="prep"
        val pack=CourtroomPrep.prepFor(courtroomJson(), caseType, languageCode())
        val types=CourtroomPrep.typeIds(courtroomJson())
        val root=page(pack.title, pack.quick)
        addButton(root, "Choose a case type"){
            AlertDialog.Builder(this).setTitle("Case type").setItems(types.map{it.second}.toTypedArray()){_,i->showCourtroomPrep(types[i].first.ifBlank{null})}.show()
        }
        pack.sections.forEach{ sec ->
            root.addView(label(sec.title,18f,true))
            root.addView(label(sec.items.joinToString("\n"){ "• $it" },14f))
        }
        addButton(root,"Share as PDF"){ sharePlanPdf(pack.title, CourtroomPrep.asText(pack)) }
        if(ReadAloud.saved(this)!=ReadAloud.OFF) addButton(root,"Read aloud"){ maybeRead(CourtroomPrep.asText(pack)) }
        addButton(root,"Build my defense"){ showTalkToMe(); sendTalk(if(pack.caseType.isNullOrBlank()) "Build my defense plan" else "Build my defense plan for a "+pack.label+" case") }
        root.addView(label(pack.disclaimer+"\n\n"+pack.notice,12f).apply{setTextColor(muted)})
    }
    private var paperTranslate=false
    private fun showPaperReader(){
        UsageAnalytics.feature(api,"uploads"); currentScreen="paper"
        val root=page("Paper reader","Photograph or upload a citation, warrant, summons, eviction notice or court order. We pull out the charge, dates, case number and court in plain language.")
        addButton(root,"Take a photo of a paper"){ paperTranslate=false; chooseNewDocument{ d->readInAiHelp(d) } }
        addButton(root,"Photograph and translate to Spanish"){ paperTranslate=true; chooseNewDocument{ d->readInAiHelp(d) } }
        addButton(root,"Choose a photo or PDF"){ paperTranslate=false; chooseNewDocument{ d->readInAiHelp(d) } }
        root.addView(label("A Spanish translation is for understanding only. The original English document is what counts in court.\n\nThis is legal information, not legal advice.",13f).apply{setTextColor(muted)})
    }

    private fun pickLanguage(){ val opts=arrayOf("English","Español (Spanish)","中文 (Chinese)","Français (French)","العربية (Arabic)","Tiếng Việt (Vietnamese)"); AlertDialog.Builder(this).setTitle("Language").setItems(opts){_,i->val language=opts[i];getSharedPreferences("ga_settings",MODE_PRIVATE).edit().putString("language",language).apply();val tag=when(i){1->"es";2->"zh-CN";3->"fr";4->"ar";5->"vi";else->"en"};AppCompatDelegate.setApplicationLocales(LocaleListCompat.forLanguageTags(tag));toast("Language preference saved: $language.")}.show() }
    private fun confirmClearData(){ AlertDialog.Builder(this).setTitle("Clear app data?").setMessage("This signs you out and removes saved settings, recent searches and profile details from this device. Your cases on the server are not deleted.").setPositiveButton("Clear"){_,_->thread{runCatching{api.logout()};runOnUiThread{getSharedPreferences("ga_settings",MODE_PRIVATE).edit().clear().apply();getSharedPreferences("ga_law_help",MODE_PRIVATE).edit().clear().apply();showHome()}}}.setNegativeButton("Cancel",null).show() }

    // ---------- More ----------
    private fun showMore(){ show(GaScreens.more(ui,nav,{row->when(row){0->openUrl("https://www.georgialegalaid.org/");1->openUrl("https://georgiacourts.gov/georgia-courts-directory/");2->comingSoon("Frequently Asked Questions","Answers to common questions are coming soon."){showMore()};3->comingSoon("App Tutorial","A guided tour of STANDALONE ASSISTANT is coming soon."){showMore()};4->comingSoon("Terms of Service","The full Terms of Service will be published here."){showMore()};5->openUrl(privacyUrl());6->showFeedback();else->openUrl("mailto:davidgoldberg6060@gmail.com?subject=STANDALONE ASSISTANT%20support")}}, if(!api.isAnonymous) ({logOutFromDrawer()}) else null)) }

    // ---------- Case workspace and research tools ----------
    private fun showLegalToolsMenu(){val root=page("Legal Tools","Public research tools stay available without an account. Saved cases stay login-only.");addButton(root,"Georgia Laws"){showGeorgiaLaws()};addButton(root,"Court Info"){showCourtInfo()};addButton(root,"Courtroom prep"){showCourtroomPrep()};addButton(root,"Paper reader"){showPaperReader()};addButton(root,"Legal Forms"){showLegalForms()};addButton(root,"Know Your Rights"){showKnowYourRights()};addButton(root,"Case Analysis"){if(requireSignedIn())showCaseAnalysis()};addButton(root,"Documents"){if(requireSignedIn())showDocuments()}}
    private fun showDarkMode(){getSharedPreferences("ga_law_help", MODE_PRIVATE).edit().putBoolean("navy_gold_dark", true).apply();toast("Dark mode keeps the navy and gold STANDALONE ASSISTANT theme.");showHome()}
    private fun logOutFromDrawer(){if(api.isAnonymous){toast("You're not signed in to an account.");showHome();return};thread{runCatching{api.logout()};runCatching{api.ensureSession()};runOnUiThread{toast("Signed out. You can keep using STANDALONE ASSISTANT without an account.");showHome()}}}
    private fun showCreateCase(){val root=page("Add Case","Create the case file first; evidence and analysis can be added afterward.");val title=input("Case title");val county=input("Georgia county");val stage=input("Stage (pretrial, appeal, etc.)");val narrative=input("What happened?",true);val typeGroup=RadioGroup(this).apply{orientation=RadioGroup.HORIZONTAL;addView(RadioButton(this@HomeActivity).apply{id=View.generateViewId();text="Criminal";setTextColor(Color.WHITE);isChecked=true;tag="criminal"});addView(RadioButton(this@HomeActivity).apply{id=View.generateViewId();text="Civil";setTextColor(Color.WHITE);tag="civil"});contentDescription="Case type"};root.addView(label("Case type",14f).apply{setTextColor(muted)});root.addView(typeGroup);listOf(title,county,stage,narrative).forEach{root.addView(it,LinearLayout.LayoutParams(-1,-2).apply{setMargins(0,dp(5),0,dp(5))})};addButton(root,"Save Case"){if(title.text.toString().trim().isBlank())return@addButton toast("Enter a case title.");runTask("Creating case…",{showCreateCase()}){val caseType=(typeGroup.findViewById<RadioButton>(typeGroup.checkedRadioButtonId)?.tag as? String)?:"criminal";val created=api.createCase(title.text.toString().trim(),county.text.toString().trim(),stage.text.toString().trim(),narrative.text.toString().trim(),caseType);val id=created.optInt("id");runOnUiThread{if(id>0)showCase(id)else showCases()}}}}
    private fun showCase(caseId:Int){val root=page("Case","Case workspace");root.addView(GaScreens.loadingNote(ui, LoadingLines.CASE_WORK, "Loading case"));runTask("Loading case…",{showCase(caseId)}){val detail=api.caseDetail(caseId);runOnUiThread{root.removeViews(2,root.childCount-2);root.addView(label(detail.optString("title","Case #$caseId"),23f,true));val summary=listOf(detail.optString("county"),detail.optString("stage"),detail.optString("narrative")).filter{it.isNotBlank()}.joinToString("\n\n");if(summary.isNotBlank())root.addView(label(summary,14f).apply{setTextColor(muted)});addButton(root,"Case Timeline"){showTimeline(caseId)};addButton(root,"Documents & Evidence"){showCaseDocuments(caseId)};addButton(root,"Innocence & Motion Review"){showInnocenceAnalysis(caseId)};addButton(root,"Case Chat"){showCaseChat(caseId,detail.optString("title"))};addButton(root,"Charge Check: What Could I Be Charged With?"){showChargeCheck(caseId,detail.optString("title"))};addButton(root,"Civil Case Check: Claims, Court & Deadlines"){showCivilCheck(caseId,detail.optString("title"))};addButton(root,"Verified Motion Screen"){showMotionScreen(caseId)};addButton(root,"Run General Case Analysis"){runCaseAnalysis(caseId)};addButton(root,"Why / Explain the Case"){showCaseJson("Why this matters",{api.why(caseId)})};addButton(root,"Red-Team Review"){showCaseJson("Red-Team Review",{api.redTeam(caseId)})};addButton(root,"Second Look"){showCaseJson("Second Look",{api.secondLook(caseId)})}}}}
    // ---------- Case Chat (mockup chat layout, scoped to one case) ----------
    private fun showCaseChat(caseId:Int,caseTitle:String=""){ val t=ChatStore.open(this,ChatStore.caseKey(caseId)); lateinit var c:GaScreens.Chat
        c=GaScreens.caseChat(ui,nav,clean(caseTitle),{q->sendCaseChat(c,caseId,t,q)},listOf(
            "Explain in simple terms" to { if(!t.hasAnswer()) toast("Ask a question first.") else sendCaseChat(c,caseId,t,"Explain your last answer in simple terms.") },
            "What deadlines apply?" to { sendCaseChat(c,caseId,t,"What deadlines could apply to this case? Cite only verified Georgia authority.") },
            "Back to case" to { showCase(caseId) }))
        wireChatDelete(c,t){ q -> sendCaseChat(c,caseId,t,q) }; show(c.root); continuity(c.messages,0,"case_chat",false); c.bot("Ask anything about this case. Answers use your case file, recent messages, and verified Georgia authority only. Confirm deadlines and strategy with qualified Georgia counsel.",now()); t.messages.forEach{ if(it.mine) c.user(it.text,it.time,it.id) else c.bot(it.text,it.time,it.id) } }
    private fun sendCaseChat(c:GaScreens.Chat,caseId:Int,t:ChatTranscript,raw:String){ val text=raw.trim(); if(text.isBlank())return toast("Enter a question first."); if(text.length>4000)return toast("Message is too long. Use 4,000 characters or fewer."); c.input.setText("")
        val history=JSONArray(); t.roleHistory(20).forEach{(r,m)->history.put(JSONObject().put("role",r).put("content",m))}
        val mine=t.add(true,text,now()); c.user(text,mine.time,mine.id); askCaseChat(c,caseId,t,text,history) }
    private fun askCaseChat(c:GaScreens.Chat,caseId:Int,t:ChatTranscript,text:String,history:JSONArray){ val stop=c.progress(listOf("Reviewing your case","Looking up Georgia law","Writing your answer","Almost done — thanks for waiting"))
        thread{ try{ val result=api.caseChat(caseId,text,history); val answer=GroundedLegalResult.answer(result).ifBlank{"No grounded case analysis was returned. Add specific facts and try again."}; val authorities=GroundedLegalResult.authoritySummary(result); val lt=lawyerTake(result)
            runOnUiThread{ stop(); val full=answer+(if(authorities.isNotBlank())"\n\n"+authorities else ""); val st=ShareText.answer(text,full,lt); val bot=t.add(false,full,now(),st)
                c.bot(full,bot.time,bot.id); if(lt!=null)c.attach(GaScreens.lawyerCard(ui,lt){x->showLaw(x.citation.replace(Regex("\\s*\\(text as of[^)]*\\)"),""))}); c.actions({shareOut(st)},{copyOut(st)},{sharePlanPdf("STANDALONE ASSISTANT",st)},{maybeRead(st)}); c.findHelp{showFindHelp()}; c.followUps(TalkToMeController.followUps(result)){f->sendCaseChat(c,caseId,t,f)} } }
        catch(e:Exception){ runOnUiThread{ stop(); val bot=t.add(false,AiErrors.message(e),now(),inContext=false); c.bot(bot.text,bot.time,bot.id); if(AiErrors.isRetryable(e)) c.retry{ t.delete(bot.id); c.remove(bot.id); askCaseChat(c,caseId,t,text,history) } } } } }
    private fun showTimeline(caseId:Int){val root=page("Case Timeline","Events from first to latest.");runTask("Loading timeline…",{showTimeline(caseId)}){val items=api.timeline(caseId);runOnUiThread{renderJsonArray(root,items,"No timeline events yet.")}}}
    private fun showCaseAnalysis(){if(!requireSignedIn())return; val root=page("Case Analysis","Choose a case, then tell STANDALONE ASSISTANT details that may matter to innocence, reasonable doubt, motions, or post-conviction review.");runTask("Loading cases…",{showCaseAnalysis()}){val cases=api.cases();runOnUiThread{if(cases.length()==0)root.addView(label("Create a case first.",14f).apply{setTextColor(muted)});for(i in 0 until cases.length()){val item=cases.optJSONObject(i)?:continue;val id=item.optInt("id");addButton(root,item.optString("title","Case #$id")){showInnocenceAnalysis(id)}}}}}
    private fun showInnocenceAnalysis(caseId:Int){val root=page("Innocence & Motion Review","Tell the app what happened, what evidence exists, what seems wrong, and anything that may show innocence or reasonable doubt. The app will look for issues and verified Georgia authority without assuming guilt or innocence.");val facts=input("Add case details: alibi, witnesses, identification, video, DNA, statements, searches, withheld evidence, changed testimony, missing proof, or new evidence…",true).apply{minLines=8};root.addView(facts,LinearLayout.LayoutParams(-1,-2).apply{setMargins(0,dp(6),0,dp(8))});root.addView(label("Important: describe facts as accurately as possible. The analysis separates affirmative innocence evidence from reasonable-doubt or insufficiency issues.",13f).apply{setTextColor(muted)});addButton(root,"Analyze Case Details"){val additional=facts.text.toString().trim();runTask("Analyzing case details…",{showInnocenceAnalysis(caseId)}){val result=api.innocenceAnalysis(caseId,additional);runOnUiThread{renderInnocenceResult(root,result,caseId)}}};addButton(root,"Back to Case"){showCase(caseId)}}
    private fun renderInnocenceResult(root:LinearLayout,result:JSONObject,caseId:Int){val review=result.optJSONObject("innocence_review");val motion=result.optJSONObject("motion_and_remedy_review");root.addView(label("Analysis Results",22f,true));if(review!=null){val interpretation=review.optString("interpretation");if(interpretation.isNotBlank())root.addView(label(interpretation,14f).apply{setTextColor(muted)});val signals=review.optJSONArray("issue_signals")?:JSONArray();root.addView(label("Potential Issues",18f,true));renderJsonArray(root,signals,"No specific innocence/doubt signal was identified from the supplied details. Add more facts or records rather than treating this as a negative conclusion.");val questions=review.optJSONArray("follow_up_questions")?:JSONArray();root.addView(label("Questions to Investigate",18f,true));renderJsonArray(root,questions,"No additional questions generated.")};if(motion!=null){root.addView(label("Motions / Remedies to Research",18f,true));val analysis=motion.optString("analysis");if(analysis.isNotBlank())root.addView(label(analysis,14f));val coverage=motion.optJSONObject("authority_coverage");if(coverage!=null)root.addView(label("Verified-authority coverage\n${coverage.toString(2)}",13f).apply{setTextColor(muted)})};root.addView(label(result.optString("notice","Verify facts, current authority, deadlines, and filing requirements before relying on this analysis."),12f).apply{setTextColor(muted)});addButton(root,"Analyze More Details"){showInnocenceAnalysis(caseId)};addButton(root,"Back to Case"){showCase(caseId)}}
    private fun runCaseAnalysis(caseId:Int){val root=page("Case Analysis","Running a fresh general case review.");root.addView(label("Analyzing…",14f).apply{setTextColor(muted)});runTask("Running case analysis…",{runCaseAnalysis(caseId)}){val result=api.runAnalysis(caseId);runOnUiThread{root.removeViews(2,root.childCount-2);root.addView(label(pretty(result),14f));addButton(root,"Innocence & Motion Review"){showInnocenceAnalysis(caseId)};addButton(root,"Back to Case"){showCase(caseId)}}}}
    private fun showMotionScreen(caseId:Int){ UsageAnalytics.feature(api, "motion_maker"); currentScreen="motion_screen";val root=page("Verified Motion Screen","Login-only screening for this saved case. This is not a filing and does not certify current Georgia law.");val facts=input("Additional facts for motion screening",true);root.addView(facts);addButton(root,"Run motion screen"){runTask("Screening motions…",{showMotionScreen(caseId)}){val result=api.motionScreen(caseId, facts.text.toString().trim());runOnUiThread{while(root.childCount>4)root.removeViewAt(root.childCount-1);val analysis=result.optString("analysis").ifBlank{result.optString("answer")}.ifBlank{pretty(result)};root.addView(label(analysis,14f));root.addView(label("Do not treat unverified citations as current Georgia law. Confirm the official source, deadlines, and procedural posture before relying on this screen.",13f).apply{setTextColor(muted)})}}}}
    private fun showCaseJson(title:String,loader:()->JSONObject){val root=page(title,"Case review output");runTask("Loading…",{showHome()}){val result=loader();runOnUiThread{root.addView(label(pretty(result),14f))}}}
    private fun showCourtInfo(){val root=page("Court Info","Official Georgia court information and self-help resources.");addButton(root,"Courtroom prep"){showCourtroomPrep()};addButton(root,"Georgia Courts"){openUrl("https://georgiacourts.gov/")};addButton(root,"Find a Court"){openUrl("https://georgiacourts.gov/georgia-courts-directory/")};root.addView(label("Court dates, filing rules and deadlines can vary by court. Confirm case-specific requirements with the court or qualified counsel.",14f).apply{setTextColor(muted)})}
    private fun showLegalForms(){ UsageAnalytics.feature(api, "motion_maker"); currentScreen="forms";val root=page("Legal Forms","Official starting points for criminal, civil, and family matters. Form text is not stored here.");addButton(root,"Criminal — public defender council"){openUrl("https://gapubdef.org/")};addButton(root,"Civil — Georgia Courts self-help"){openUrl("https://georgiacourts.gov/a2j/")};addButton(root,"Family — Georgia Legal Aid"){openUrl("https://www.georgialegalaid.org/")};root.addView(label("Confirm a form is current and accepted by the court before filing. These links are not Lexis annotations and are not a filing.",14f).apply{setTextColor(muted)})}
    private fun showLegalTools(){if(!requireSignedIn())return; val root=page("Legal Tools","Case analysis, legal research, forms and court resources.");addButton(root,"Case Analysis"){showCaseAnalysis()};addButton(root,"Georgia Laws"){showGeorgiaLaws()};addButton(root,"Legal Forms"){showLegalForms()};addButton(root,"Court Info"){showCourtInfo()};addButton(root,"Courtroom prep"){showCourtroomPrep()};addButton(root,"Paper reader"){showPaperReader()};addButton(root,"Know Your Rights"){showKnowYourRights()}}
    private fun showKnowYourRights(){val root=page("Know Your Rights","Guest information only. Do not resist, lie, or destroy evidence.");listOf("Arrest" to "If arrested, do not resist or run. You may state that you are remaining silent and want a lawyer.","Police encounter / traffic stop" to "Keep your hands visible. You may ask whether you are free to leave and state that you do not consent to a search. Do not physically interfere.","Traffic stop card (fuller guide)" to "Open the traffic-stop rights card for a longer plain-language checklist.","Court" to "Court dates and filing rules vary. Do not ignore a court date. Ask the court or a lawyer before relying on a deadline.","Jail" to "Calls and common areas may be recorded. Do not discuss case facts there. You may ask for a lawyer.","Constitutional rights" to "You may clearly invoke the right to remain silent and the right to a lawyer. This screen is not a substitute for a licensed Georgia attorney.","Voting after a felony" to "Voting rights restore automatically when the sentence is complete — see the voting guide.").forEach{(title,body)->addButton(root,title){if(title.startsWith("Traffic stop card"))showCitizenFeature("traffic_stop") else if(title.startsWith("Voting"))showCitizenFeature("voting") else {val topic=page(title,"General information. Guest rights stay on /public/rights-assistant.");topic.addView(label(body,15f));addButton(topic,"Ask without signing in"){showTalkToMe()}}}};root.addView(label("Do not resist, lie, or destroy evidence. Private cases stay login-only.\n\n"+CitizenHelp.DISCLAIMER,13f).apply{setTextColor(muted)})}
    private fun showResources(){ UsageAnalytics.feature(api, "find_legal_help"); currentScreen="resources";val root=page("Resources","Georgia courts, legal aid and citizen-help guides.");addButton(root,"Citizen Help (all guides)"){showCitizenHelpHub()};CitizenHelp.FEATURES.forEach{f->addButton(root,f.title){showCitizenFeature(f.id)}};addButton(root,"Georgia Legal Aid"){openUrl("https://www.georgialegalaid.org/")};addButton(root,"Georgia Courts"){openUrl("https://georgiacourts.gov/")};addButton(root,"Georgia Public Defender Council"){openUrl("https://gapubdef.org/")};addButton(root,"988 Crisis & Suicide Lifeline"){openUrl("https://988lifeline.org/")};root.addView(label(CitizenHelp.DISCLAIMER,12f).apply{setTextColor(muted)})}
    private fun showCitizenHelpHub(){ UsageAnalytics.feature(api, "find_legal_help"); currentScreen="citizen";val root=page("Citizen Help","Free guides for filing, records, fines, court dates, reentry and more.");root.addView(label(CitizenHelp.DISCLAIMER,12f).apply{setTextColor(muted)});CitizenHelp.FEATURES.forEach{f->addButton(root,f.title+" — "+f.blurb){showCitizenFeature(f.id)}}}
    private fun showCitizenFeature(id:String){val f=CitizenHelp.feature(id)?:return toast("That guide is not available.");val root=page(f.title,f.blurb);root.addView(label(CitizenHelp.DISCLAIMER,12f).apply{setTextColor(muted)});f.sections.forEach{sec->root.addView(label(sec.title,18f,true));root.addView(label(sec.body,14f));sec.links.forEach{link->addButton(root,link.label){openCitizenLink(link.url)}}};addButton(root,"All Citizen Help guides"){showCitizenHelpHub()}}
    private fun openCitizenLink(url:String){when{url=="app:motions"->showMotionsHub();url=="app:talk"->showTalkToMe();url=="app:civil_check"->showCivilCheck(null,null);url=="app:help_loved_one"->HelpLovedOne.show(ui){openUrl(it)};url=="app:court_date_form"->showCourtDateForm();url.startsWith("tel:")->dial(url.removePrefix("tel:"));else->openUrl(url)}}
    private fun showCourtDateForm(){val box=LinearLayout(this).apply{orientation=LinearLayout.VERTICAL;setPadding(dp(20),dp(8),dp(20),0)};val title=EditText(this).apply{hint="What is the deadline? (example: Arraignment)"};val due=EditText(this).apply{hint="Date YYYY-MM-DD";inputType=android.text.InputType.TYPE_CLASS_DATETIME};box.addView(title);box.addView(due);box.addView(TextView(this).apply{text="Reminders stay on this phone. You will get notices 7 days before, 1 day before and on that morning at 9:00 a.m. Missing court can lead to a warrant. For traffic tickets, Failure to Appear can suspend a license — see DDS.";setTextColor(muted);textSize=13f;setPadding(0,dp(8),0,0)});AlertDialog.Builder(this).setTitle("Court date reminder").setView(box).setPositiveButton("Set reminders"){_,_->val t=title.text.toString().trim().ifBlank{"Court date"};val d=due.text.toString().trim();if(!Regex("^\\d{4}-\\d{2}-\\d{2}$").matches(d))return@setPositiveButton toast("Use a date like 2026-12-01.");remindDeadline(t,d)}.setNegativeButton("Cancel",null).show()}
    private fun showCaseDocuments(caseId:Int){val root=page("Documents","Evidence and files attached to this case.");addButton(root,"+ Add from My Documents"){pickSavedDocument("Attach which document?"){d->attachToCase(d,caseId)}};addButton(root,"Read a paper with AI Help"){pickSavedDocument("Which document should AI Help read?"){d->readInAiHelp(d,caseId)}};runTask("Loading documents…",{showCaseDocuments(caseId)}){val items=api.evidence(caseId);runOnUiThread{renderJsonArray(root,items,"No documents attached yet.")}}}
    private fun pretty(obj:JSONObject):String{val preferred=listOf("title","citation","summary","analysis","answer","detail","description","status","county","stage","issue","kind","note");val lines=preferred.mapNotNull{key->obj.optString(key).takeIf{it.isNotBlank()}?.let{"$key: $it"}};return if(lines.isNotEmpty())lines.joinToString("\n\n")else obj.toString(2)}
    private fun openUrl(url:String){runCatching{startActivity(Intent(Intent.ACTION_VIEW,Uri.parse(url)))}.onFailure{toast("No browser is available for this link.")}}
    private fun renderJsonArray(root:LinearLayout,items:JSONArray,emptyMessage:String){if(items.length()==0){root.addView(label(emptyMessage,14f).apply{setTextColor(muted)});return};for(i in 0 until items.length()){val item=items.opt(i);val text=when(item){is JSONObject->pretty(item);else->item?.toString().orEmpty()};root.addView(label(text,14f).apply{setPadding(dp(14),dp(12),dp(14),dp(12));background=ui.glowCard(GaUi.CARD,GaUi.STROKE_SOFT,12,glow=false)},LinearLayout.LayoutParams(-1,-2).apply{setMargins(0,dp(5),0,dp(5))})}}
    private fun runTask(message:String,retry:()->Unit,work:()->Unit){thread{try{work()}catch(e:Exception){runOnUiThread{showError(e.message?:"Something went wrong. Please try again.",retry)}}}}
    private fun showError(message:String,retry:()->Unit){val root=page("Couldn’t complete that","Your app is still usable. You can retry or return Home.");root.addView(label(message,15f));addButton(root,"Retry"){retry()};addButton(root,"Home"){showHome()}}
    private fun shareOut(text:String){ runCatching{startActivity(Intent.createChooser(Intent(Intent.ACTION_SEND).setType("text/plain").putExtra(Intent.EXTRA_SUBJECT,"STANDALONE ASSISTANT").putExtra(Intent.EXTRA_TEXT,text),"Share"))}.onFailure{toast("No app is available to share with.")} }
    private fun copyOut(text:String){ (getSystemService(CLIPBOARD_SERVICE) as android.content.ClipboardManager).setPrimaryClip(android.content.ClipData.newPlainText("STANDALONE ASSISTANT",text)); toast("Copied with citations.") }
    private fun toast(message:String)=Toast.makeText(this,message,Toast.LENGTH_SHORT).show()
}
