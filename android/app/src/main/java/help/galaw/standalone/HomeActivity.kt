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
    private var pendingUploadCaseId: Int? = null
    private val navy = GaUi.NAVY
    private val panel = GaUi.CARD_SOLID
    private val blue = GaUi.BLUE
    private val muted = GaUi.MUTED
    private val pickDocument = registerForActivityResult(ActivityResultContracts.OpenDocument()) { uri ->
        val caseId = pendingUploadCaseId; pendingUploadCaseId = null
        if (uri == null || caseId == null) return@registerForActivityResult
        runTask("Uploading document…", { showDocuments() }) { api.upload(caseId, uri); runOnUiThread { toast("Document uploaded securely."); showDocuments() } }
    }
    override fun onCreate(savedInstanceState: Bundle?) { super.onCreate(savedInstanceState); SystemBars.apply(this); api = ApiClient(this); ui = GaUi(this); showHome(); thread { runCatching { api.ensureSession() } } }
    @Deprecated("Deprecated in Java") override fun onBackPressed() { if (drawerView != null) { closeDrawer(); return }; if (!onHome) showHome() else super.onBackPressed() }
    private fun dp(v: Int) = (v * resources.displayMetrics.density).toInt()
    private val homeActions = object : ApprovedHomeScreen.Actions {
        override fun openMenu()=showMenu(); override fun openAccount()=showAccount(); override fun ask(question:String)=askFromHome(question); override fun openCases()=showCases(); override fun openTalkToMe()=showTalkToMe(); override fun openLegalTools()=showLegalTools(); override fun openGeorgiaLaws()=showGeorgiaLaws(); override fun openCourtInfo()=showCourtInfo(); override fun openLegalForms()=showLegalForms(); override fun openCaseAnalysis()=showMyCase(); override fun openKnowYourRights()=showKnowYourRights(); override fun openResources()=showResources(); override fun openEmergency()=showEmergency(); override fun openHome()=showHome(); override fun openDocuments()=showDocuments(); override fun openFunnyLaws()=showFunnyLaws()
    }
    private val nav = object : GaScreens.Nav {
        override fun menu()=showMenu(); override fun home()=showHome(); override fun laws()=showGeorgiaLaws(); override fun aiHelp()=showTalkToMe(); override fun documents()=showDocuments(); override fun account()=showAccount(); override fun more()=showMore(); override fun legalWork()=showMotionsHub(); override fun funny()=showFunnyLaws()
    }
    private fun showHome(){ closeDrawer(); onHome=true; setContentView(ApprovedHomeScreen(this,homeActions).build()) }
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
    private fun showFunnyLaws(cases:Boolean=false){ val data=funnyData?:FunnyGeorgiaData.parse(assets.open("funny_georgia.json").bufferedReader().use{it.readText()}).also{funnyData=it}; show(FunnyGeorgiaScreen(ui,data.first,data.second,{showMenu()},{url->openUrl(url)},cases,GaScreens.bottomNav(ui,nav,GaScreens.Tab.FUNNY)).build()) }
    private fun showMenu(){ closeDrawer(); val items=HomeDrawerCatalog.items; val overlay=GaScreens.drawer(ui,items,BuildConfig.VERSION_NAME,{item->closeDrawer();onDrawerItem(item)},{closeDrawer()}); drawerView=overlay; addContentView(overlay,ViewGroup.LayoutParams(-1,-1)) }
    private fun closeDrawer(){ drawerView?.let{(it.parent as? ViewGroup)?.removeView(it)}; drawerView=null }
    private fun onDrawerItem(item:HomeDrawerItem){if(item.requiresSignIn&&!requireSignedIn())return;when(item.id){"home"->showHome();"mycase"->showMyCase();"cases"->showCases();"ai"->showTalkToMe();"laws"->showGeorgiaLaws();"loopholes"->showLoopholes();"charges"->showChargeCheck(null,null);"civil"->showCivilCheck(null,null);"motions"->showMotionsHub();"forms"->showLegalForms();"court"->showCourtInfo();"rights"->showKnowYourRights();"resources"->showResources();"emergency"->showEmergency();"payments"->showPayment();"settings"->showSettings();"profile"->showAccount();"help"->showMore();"funny"->showFunnyLaws()}}

    // ---------- Talk to Me ----------
    private val talk by lazy { ChatStore.open(this, ChatStore.TALK_KEY) }
    private var chat: GaScreens.Chat? = null
    private val greetingTime = now()
    private fun now():String = SimpleDateFormat("h:mm a", Locale.US).format(Date())
    private fun askFromHome(question:String){ showTalkToMe(); sendTalk(question) }
    private fun showTalkToMe(){ val c=GaScreens.talkToMe(ui,nav,{q->sendTalk(q)},listOf(
        "Cite a law" to { chat?.input?.apply{setText("Which Georgia law applies to ");setSelection(text.length);requestFocus()} },
        "Find a form" to { showLegalForms() },
        "Explain in simple terms" to { if(!talk.hasAnswer()) toast("Ask a question first.") else sendTalk("Explain your last answer in simple terms.") }))
        chat=c; wireChatDelete(c,talk); show(c.root); c.bot("How can I help you today?",greetingTime); talk.messages.forEach{ if(it.mine) c.user(it.text,it.time,it.id) else c.bot(it.text,it.time,it.id) } }
    private fun sendTalk(q:String){ val c=chat?:return; if(q.length>4000)return toast("Message is too long. Use 4,000 characters or fewer."); c.input.setText(""); val history=talk.transcript(); val line=talk.add(true,q,now()); c.user(line.text,line.time,line.id); askTalk(c,q,history,line.id) }
    private fun askTalk(c:GaScreens.Chat,q:String,history:String,userId:Long){ val stop=c.progress()
        thread{ try{ val reply=TalkToMeController.reply(api,history,q,languageInstruction()); val text=reply.answer+(if(reply.authoritySummary.isNotBlank())"\n\n"+reply.authoritySummary else ""); runOnUiThread{ stop(); val st=ShareText.answer(q,text); val bot=talk.add(false,text,now(),st); if(chat===c){c.bot(bot.text,bot.time,bot.id);c.actions({shareOut(st)},{copyOut(st)});c.findHelp{showFindHelp()};c.followUps(reply.followUps){f->sendTalk(f)};Glossary.button(ui,text)?.let{c.attach(it)};if(reply.caseStage.isNotBlank()&&MyCaseScreens.STAGES.any{it.first==reply.caseStage})c.attach(ui.secondaryButton("Open My Case: "+MyCaseScreens.STAGES.first{it.first==reply.caseStage}.second+" ›"){showStage(reply.caseStage,JSONObject().put("situation",q))})} } }
        catch(e:Exception){ runOnUiThread{ stop(); val msg=AiErrors.message(e); val bot=talk.add(false,msg,now(),inContext=false); if(chat===c){c.bot(bot.text,bot.time,bot.id); if(AiErrors.isRetryable(e)) c.retry{ talk.delete(bot.id); c.remove(bot.id); askTalk(c,q,history,userId) } } } } } }
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
        catch(e:Exception){ runOnUiThread{ toast(if(e is ApiException&&e.statusCode==404)"That law isn't in GA.LAW.HELP yet." else AiErrors.message(e)) } } } }
    private fun wireChatDelete(c:GaScreens.Chat,t:ChatTranscript){ c.onLawTap={cite->showLaw(cite)}
        c.onMessageLongPress={id->val m=t.messages.firstOrNull{it.id==id}; if(m!=null) AlertDialog.Builder(this).setTitle(if(m.mine)"Your message" else "GA.LAW.HELP answer").setItems(arrayOf("Copy","Share","Delete")){_,i->when(i){0->copyOut(m.shareText);1->shareOut(m.shareText);else->AlertDialog.Builder(this).setTitle("Delete this message?").setMessage("It will be removed from this chat and won't be sent to the AI again. This can't be undone.").setPositiveButton("Delete"){_,_->t.delete(id);c.remove(id);toast("Message deleted.")}.setNegativeButton("Cancel",null).show()}}.show()}
        c.onClearChat={ if(t.messages.isEmpty()) toast("This chat is already empty.") else AlertDialog.Builder(this).setTitle("Clear this chat?").setMessage("All messages in this chat will be deleted from this phone and won't be sent to the AI again. This can't be undone.").setPositiveButton("Clear chat"){_,_->t.clear();c.clearMessages();toast("Chat cleared.")}.setNegativeButton("Cancel",null).show() } }
    private fun languageCode():String { val saved=getSharedPreferences("ga_settings",MODE_PRIVATE).getString("language","English")?:"English"; return when { saved.startsWith("Español")->"es"; saved.startsWith("中文")->"zh"; saved.startsWith("Français")->"fr"; saved.startsWith("العربية")->"ar"; saved.startsWith("Tiếng Việt")->"vi"; else->"en" } }
    private fun languageInstruction():String = when(languageCode()){"es"->"Respond in Spanish.";"zh"->"Respond in Simplified Chinese.";"fr"->"Respond in French.";"ar"->"Respond in Arabic.";"vi"->"Respond in Vietnamese.";else->"Respond in English."}

    // ---------- Charge Check ----------
    private fun showChargeCheck(caseId:Int?,caseTitle:String?,prefill:String?=null){ if(!requireSignedIn())return; lateinit var form:GaScreens.ChargeCheckForm; form=GaScreens.chargeCheck(ui,nav,caseTitle){t->runChargeCheck(form,t,caseId)}; show(form.root); if(!prefill.isNullOrBlank()){form.situation.setText(prefill);runChargeCheck(form,prefill,caseId)} }
    private fun options(arr:JSONArray?,labelKey:String?)=(0 until (arr?.length()?:0)).mapNotNull{i->arr!!.optJSONObject(i)?.let{o->GaScreens.ChargeOption(labelKey?.let{k->clean(o.optString(k))}?.ifBlank{null},o.optString("title"),o.optString("explanation"),cites(o.optJSONArray("citations")))}}
    private fun runChargeCheck(form:GaScreens.ChargeCheckForm,raw:String,caseId:Int?){ val situation=raw.trim(); if(situation.isEmpty()&&caseId==null)return toast("Describe what happened."); if(situation.length>4000)return toast("Description is too long. Use 4,000 characters or fewer."); GaScreens.chargeCheckLoading(ui,form.results)
        thread{ try{ val r=api.chargeCheck(situation,caseId); val ch=r.optJSONArray("charges")
            val charges=(0 until (ch?.length()?:0)).mapNotNull{i->ch!!.optJSONObject(i)?.let{o->val c=o.optJSONObject("citation")?:return@let null;GaScreens.ChargeItem(o.optString("charge"),o.optString("level_label"),clean(o.optString("penalty")).ifBlank{null},clean(o.optString("penalty_note")).ifBlank{null},o.optString("why"),GaScreens.LoopholeCite(c.optString("citation"),clean(c.optString("title")),clean(c.optString("source_url")).ifBlank{null}))}}
            val em=r.optJSONObject("emergency")?.optJSONArray("resources"); val emergency=(0 until (em?.length()?:0)).mapNotNull{i->em!!.optJSONObject(i)?.let{o->o.optString("label") to o.optString("contact")}}
            val result=GaScreens.ChargeCheckResult(charges,options(r.optJSONArray("defenses"),"kind_label"),options(r.optJSONArray("lowest_outcome"),null),lawyerTake(r),clean(r.optString("message")).ifBlank{null},r.optBoolean("refused"),r.optString("estimate_note"),r.optString("rights_reminder"),r.optString("disclaimer",GaScreens.CHARGE_DISCLAIMER),emergency,if(r.isNull("case_id"))null else r.optInt("case_id"))
            val shareText=ShareText.chargeCheck(situation,result)
            runOnUiThread{ GaScreens.renderChargeCheck(ui,form.results,result,{shareOut(shareText)} to {copyOut(shareText)},{n->dial(n)}){c->showLaw(c.citation.replace(Regex("\\s*\\(text as of[^)]*\\)"),""))} }
        }catch(e:Exception){ runOnUiThread{ form.results.removeAllViews(); form.results.addView(ui.emptyCard(R.drawable.ga_ic_error,"Couldn’t check charges",AiErrors.message(e)),ui.lp(4,4)); if(AiErrors.isRetryable(e)) form.results.addView(ui.primaryButton("Retry"){runChargeCheck(form,raw,caseId)},ui.lp(6,6)) } } } }

    // ---------- Civil Case Check ----------
    private fun showCivilCheck(caseId:Int?,caseTitle:String?){ if(!requireSignedIn())return; lateinit var form:GaScreens.ChargeCheckForm; form=GaScreens.civilCheck(ui,nav,caseTitle){t->runCivilCheck(form,t,caseId)}; show(form.root) }
    private fun noAsOf(s:String)=s.replace(Regex("\\s*\\(text as of[^)]*\\)"),"").trim()
    private fun cite1(o:JSONObject?)=o?.let{c->GaScreens.LoopholeCite(noAsOf(c.optString("citation")),clean(c.optString("title")),clean(c.optString("source_url")).ifBlank{null})}
    private fun runCivilCheck(form:GaScreens.ChargeCheckForm,raw:String,caseId:Int?){ val situation=raw.trim(); if(situation.isEmpty()&&caseId==null)return toast("Describe the dispute."); if(situation.length>4000)return toast("Description is too long. Use 4,000 characters or fewer."); GaScreens.chargeCheckLoading(ui,form.results)
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
    private fun showLoopholes(prefill:String?=null){ if(!requireSignedIn())return; lateinit var form:GaScreens.LoopholesForm; form=GaScreens.loopholes(ui,nav,loopholeChips){t->analyzeLoopholes(form,t)}; show(form.root); if(!prefill.isNullOrBlank()){val t=prefill.take(300);form.topic.setText(t);analyzeLoopholes(form,t)} }
    // ---------------- My Case hub ----------------
    private fun savedCases():List<JSONObject> = runCatching{ val a=JSONArray(getSharedPreferences("ga_settings",MODE_PRIVATE).getString("my_cases","[]")); (0 until a.length()).map{a.getJSONObject(it)} }.getOrDefault(emptyList())
    private fun storeCases(list:List<JSONObject>){ getSharedPreferences("ga_settings",MODE_PRIVATE).edit().putString("my_cases",JSONArray(list).toString()).apply() }
    private fun showMyCase(){ show(MyCaseScreens.hub(ui,nav,savedCases(),{k->when(k){"criminal"->showStages();"civil"->showCivilCheck(null,null);else->showTalkToMe()}},{s->showStage(s.optString("stage"),s.optJSONObject("details"))},{s->AlertDialog.Builder(this).setTitle("Delete saved case?").setPositiveButton("Delete"){_,_->storeCases(savedCases().filter{it.optString("id")!=s.optString("id")});showMyCase()}.setNegativeButton("Cancel",null).show()})) }
    private fun showStages(){ show(MyCaseScreens.stages(ui,nav){st->showStage(st,null)}) }
    private fun showStage(stage:String,prefill:JSONObject?){ lateinit var form:MyCaseScreens.StageForm; form=MyCaseScreens.stageForm(ui,nav,stage,prefill){runGuide(form,stage)}; show(form.root); if(prefill!=null&&(prefill.optString("situation").isNotBlank()||prefill.length()>1))runGuide(form,stage) }
    private val guideAnswers=JSONObject()
    private fun runGuide(form:MyCaseScreens.StageForm,stage:String){ val details=JSONObject().put("situation",form.situation.text.toString().trim().take(2000)); form.dates.forEach{(k,v)->val d=v.text.toString().trim(); if(d.isNotBlank())details.put(k,d)}
        GaScreens.loopholesLoading(ui,form.results); ((form.results.getChildAt(0) as? LinearLayout)?.getChildAt(1) as? TextView)?.text="Finding next steps, motions and Georgia laws…"
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
    private fun analyzeLoopholes(form:GaScreens.LoopholesForm,raw:String){ val topic=raw.trim(); if(topic.isEmpty())return toast("Enter a Georgia legal topic."); if(topic.length>300)return toast("Topic is too long. Use 300 characters or fewer."); GaScreens.loopholesLoading(ui,form.results)
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
    private fun showCases(){if(!requireSignedIn())return; renderCases(); runTask("Loading cases…",{showCases()}){val rows=caseRows(api.cases());runOnUiThread{casesCache=rows;renderCases()}}}
    private fun renderCases(){ show(GaScreens.myCases(ui,nav,casesCache,casesFilter,casesQuery,{casesFilter=it;renderCases()},{casesQuery=it;renderCases()},{showCase(it)},{showCreateCase()})) }

    // ---------- Documents ----------
    private var docsTab = 0
    private var docsSortByName = false
    private var docsCache: List<GaScreens.DocRow>? = null
    private fun showDocuments(){if(!requireSignedIn())return; docsCache=null; renderDocuments(); runTask("Loading documents…",{showDocuments()}){val cases=caseRows(api.cases());casesCache=cases;val docs=cases.flatMap{c->val ev=api.evidence(c.id);(0 until ev.length()).mapNotNull{i->ev.optJSONObject(i)?.let{o->GaScreens.DocRow(c.id,c.title,o.optString("filename","Document"),clean(o.optString("media_type")),shortDate(clean(o.optString("uploaded_at"))),humanSize(o.optLong("size_bytes",-1)))}}};runOnUiThread{docsCache=docs;renderDocuments()}}}
    private fun renderDocuments(){ val docs=docsCache?.let{ if(docsSortByName) it.sortedBy{d->d.name.lowercase()} else it }; show(GaScreens.documents(ui,nav,docsTab,docs,{docsTab=it;renderDocuments()},{chooseUploadCase()},{docsSortByName=!docsSortByName;toast(if(docsSortByName)"Sorted by name" else "Sorted by case");renderDocuments()},{showCaseDocuments(it.caseId)})) }
    private fun chooseUploadCase(){ val cases=casesCache.orEmpty(); if(cases.isEmpty()){toast("Create a case first so the file has a secure case workspace.");showCreateCase();return}; val launch={id:Int->pendingUploadCaseId=id;pickDocument.launch(arrayOf("application/pdf","image/*","text/*","application/msword","application/vnd.openxmlformats-officedocument.wordprocessingml.document"))}; if(cases.size==1)launch(cases[0].id) else AlertDialog.Builder(this).setTitle("Add to which case?").setItems(cases.map{it.title}.toTypedArray()){_,i->launch(cases[i].id)}.show() }
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
        GaScreens.Row(R.drawable.ga_ic_location_on,"Find a Local Jail","Search by county"){openUrl("https://www.google.com/maps/search/county+jail+Georgia")},
        GaScreens.Row(R.drawable.ga_ic_person,"Contact a Public Defender","Get legal representation"){openUrl("https://gapubdef.org/")},
        GaScreens.Row(R.drawable.ga_ic_volunteer_activism,"Victim Resources","Support and services"){openUrl("https://cjcc.georgia.gov/victims-compensation")},
        GaScreens.Row(R.drawable.ga_ic_monitor_heart,"Mental Health Support","24/7 crisis help — call or text 988"){dial("988")},
        GaScreens.Row(R.drawable.ga_ic_error,"Report a Rights Violation","File a complaint"){openUrl("https://civilrights.justice.gov/")},
        GaScreens.Row(R.drawable.ga_ic_warning,"Other Emergency Resources","Food, shelter, and more — dial 211"){dial("211")}))) }
    private fun dial(number:String){ runCatching{startActivity(Intent(Intent.ACTION_DIAL,Uri.parse("tel:$number")))}.onFailure{toast("Dial $number from your phone.")} }

    // ---------- Motions & Legal Work ----------
    private fun showMotionsHub(){ if(!requireSignedIn())return; show(GaScreens.motions(ui,nav,listOf(
        GaScreens.Row(R.drawable.ga_ic_description,"Generate a Motion","Create customized legal motions"){chooseCase("Generate a Motion"){showMotionScreen(it)}},
        GaScreens.Row(R.drawable.ga_ic_library_books,"Motion Library","Browse common motions"){startActivity(Intent(this,InternalLegalSearchActivity::class.java).putExtra("mode","motions").putExtra("title","Motion Library"))},
        GaScreens.Row(R.drawable.ga_ic_edit_square,"Legal Writing Help","Improve or review your drafts"){comingSoon("Legal Writing Help","Draft review is not available yet. You can ask Talk to Me about a specific issue in the meantime.",GaScreens.Tab.LEGAL_WORK){showMotionsHub()}},
        GaScreens.Row(R.drawable.ga_ic_sms,"Ask GA.LAW.HELP\nabout my situation","Get personalized guidance"){showTalkToMe()}))) }
    private fun chooseCase(title:String,then:(Int)->Unit){ runTask("Loading cases…",{showMotionsHub()}){val cases=caseRows(api.cases());runOnUiThread{ if(cases.isEmpty()){toast("Create a case first.");showCreateCase()} else if(cases.size==1)then(cases[0].id) else AlertDialog.Builder(this).setTitle(title).setItems(cases.map{it.title}.toTypedArray()){_,i->then(cases[i].id)}.show() }} }
    private fun comingSoon(title:String,body:String,tab:GaScreens.Tab=GaScreens.Tab.MORE,back:()->Unit={showHome()}){ show(GaScreens.comingSoon(ui,nav,tab,title,body,back)) }

    // ---------- Account / Profile ----------
    private fun showAccount(){if(api.isAnonymous)return showAnonymousAccount(); val prefs=getSharedPreferences("ga_settings",MODE_PRIVATE); renderProfile(prefs.getString("profile_email","").orEmpty()); runTask("Loading account…",{showAccount()}){val me=api.me();val email=me.optString("email");prefs.edit().putString("profile_email",email).apply();runOnUiThread{renderProfile(email)}}}
    /** Account tab without an account: what is saved, optional sign-in, and delete-my-data. */
    private fun showAnonymousAccount(){ val root=page("Account","No sign-in needed. GA.LAW.HELP is ready to use.",GaScreens.Tab.ACCOUNT)
        root.addView(label("You're using GA.LAW.HELP without an account. Your cases, Case Chat, Charge Check results and documents are saved to this phone's private anonymous ID. No name, email or phone number is required.",15f))
        addButton(root,"Sign in or create an account (optional)"){startActivity(Intent(this,AuthActivity::class.java))}
        addButton(root,"My Cases"){showCases()}
        addButton(root,"Privacy Policy"){openUrl(privacyUrl())}
        addButton(root,"Delete my data"){confirmDeleteAccount()}
        root.addView(ui.note("Signing in to an account is separate from this device's anonymous data. Uninstalling the app or clearing its storage loses access to the anonymous data; use Delete my data first if you want it removed from our server.")) }
    private fun renderProfile(email:String){ val prefs=getSharedPreferences("ga_settings",MODE_PRIVATE); show(GaScreens.profile(ui,nav,prefs.getString("profile_name","").orEmpty(),email,prefs.getString("profile_phone","").orEmpty(),{toast("Profile photos are coming soon.")}){name,phone->prefs.edit().putString("profile_name",name).putString("profile_phone",phone).apply();toast("Profile saved on this device.")}) }

    // ---------- Payment (free launch) ----------
    private fun showPayment(){ show(GaScreens.payment(ui,nav,"Free Launch","\$0 — free during launch",listOf("Full access to all features","Georgia law search & Talk to Me","Private cases & documents (sign-in)","Case analysis tools"),
        {toast("Paid plans aren’t offered during the free launch. Everything is free.")},{toast("No payment method is needed during the free launch.")},{toast("No billing history — you have not been charged.")})) }

    // ---------- Settings ----------
    private fun showSettings(){ show(GaScreens.settings(ui,nav,true){row->when(row){0->pickLanguage();1->toast("GA.LAW.HELP uses the dark navy theme.");2->comingSoon("Notifications","Court-date and case reminders are not available yet."){showSettings()};3->showPrivacy();4->confirmClearData();else->AlertDialog.Builder(this).setTitle("About GA.LAW.HELP").setMessage("Version ${BuildConfig.VERSION_NAME}\n\nClear answers. A stronger Georgia.\n\nGA.LAW.HELP provides general legal information, not legal advice, and does not create an attorney-client relationship. Questions sent to AI features may be processed by third-party AI providers; some free providers may use them to improve their models, so do not enter sensitive personal information.\n\nContact: davidgoldberg6060@gmail.com").setPositiveButton("OK",null).show()}}) }
    private fun privacyUrl()=BuildConfig.API_BASE_URL.trimEnd('/')+"/privacy"
    private fun showPrivacy(){ val root=page("Privacy & Security","How this app protects your information.",GaScreens.Tab.MORE); root.addView(label("Your sign-in session is stored with Android encrypted storage on this device. My Cases, Documents and case analysis require sign-in, and your uploads are stored in your private case workspace with an integrity hash. Guest questions do not require an account.",15f)); addButton(root,"Read the Privacy Policy"){openUrl(privacyUrl())}; if(api.isAnonymous){ addButton(root,"Delete my data"){confirmDeleteAccount()} } else { addButton(root,"Sign out of this device"){logOutFromDrawer()}; addButton(root,"Delete Account"){confirmDeleteAccount()} } }
    private fun confirmDeleteAccount(){ val anon=api.isAnonymous; val box=LinearLayout(this).apply{orientation=LinearLayout.VERTICAL;setPadding(dp(20),dp(4),dp(20),0)}; val pw=EditText(this).apply{hint="Your password";inputType=android.text.InputType.TYPE_CLASS_TEXT or android.text.InputType.TYPE_TEXT_VARIATION_PASSWORD}; val word=EditText(this).apply{hint="Type DELETE to confirm"}; if(!anon)box.addView(pw); box.addView(word)
        AlertDialog.Builder(this).setTitle(if(anon)"Delete my data?" else "Delete your account?").setMessage(if(anon)"This permanently deletes this device's anonymous record and all of its cases, notes, analyses and uploaded files from GA.LAW.HELP. This cannot be undone." else "This permanently deletes your account, all of your cases, notes, timeline events, analyses and uploaded files from GA.LAW.HELP. This cannot be undone.").setView(box).setPositiveButton("Delete forever"){_,_->
            if(word.text.toString().trim().uppercase()!="DELETE")return@setPositiveButton toast("Type DELETE to confirm."); val password=pw.text.toString(); if(!anon&&password.isEmpty())return@setPositiveButton toast("Enter your password.")
            thread{ try{ api.deleteAccount(password); ChatStore.wipeAll(this); runOnUiThread{ getSharedPreferences("ga_settings",MODE_PRIVATE).edit().clear().apply(); toast(if(anon)"Your data was deleted." else "Your account and data were deleted."); showHome() } } catch(e:Exception){ runOnUiThread{ toast(e.message?:"Account could not be deleted. Please try again.") } } } }.setNegativeButton("Cancel",null).show() }
    private fun pickLanguage(){ val opts=arrayOf("English","Español (Spanish)","中文 (Chinese)","Français (French)","العربية (Arabic)","Tiếng Việt (Vietnamese)"); AlertDialog.Builder(this).setTitle("Language").setItems(opts){_,i->val language=opts[i];getSharedPreferences("ga_settings",MODE_PRIVATE).edit().putString("language",language).apply();val tag=when(i){1->"es";2->"zh-CN";3->"fr";4->"ar";5->"vi";else->"en"};AppCompatDelegate.setApplicationLocales(LocaleListCompat.forLanguageTags(tag));toast("Language preference saved: $language.")}.show() }
    private fun confirmClearData(){ AlertDialog.Builder(this).setTitle("Clear app data?").setMessage("This signs you out and removes saved settings, recent searches and profile details from this device. Your cases on the server are not deleted.").setPositiveButton("Clear"){_,_->thread{runCatching{api.logout()};runOnUiThread{getSharedPreferences("ga_settings",MODE_PRIVATE).edit().clear().apply();getSharedPreferences("ga_law_help",MODE_PRIVATE).edit().clear().apply();showHome()}}}.setNegativeButton("Cancel",null).show() }

    // ---------- More ----------
    private fun showMore(){ show(GaScreens.more(ui,nav,{row->when(row){0->openUrl("https://www.georgialegalaid.org/");1->openUrl("https://georgiacourts.gov/georgia-courts-directory/");2->comingSoon("Frequently Asked Questions","Answers to common questions are coming soon."){showMore()};3->comingSoon("App Tutorial","A guided tour of GA.LAW.HELP is coming soon."){showMore()};4->comingSoon("Terms of Service","The full Terms of Service will be published here."){showMore()};5->openUrl(privacyUrl());else->openUrl("mailto:davidgoldberg6060@gmail.com?subject=GA.LAW.HELP%20support")}}, if(!api.isAnonymous) ({logOutFromDrawer()}) else null)) }

    // ---------- Case workspace and research tools ----------
    private fun showLegalToolsMenu(){val root=page("Legal Tools","Public research tools stay available without an account. Saved cases stay login-only.");addButton(root,"Georgia Laws"){showGeorgiaLaws()};addButton(root,"Court Info"){showCourtInfo()};addButton(root,"Legal Forms"){showLegalForms()};addButton(root,"Know Your Rights"){showKnowYourRights()};addButton(root,"Case Analysis"){if(requireSignedIn())showCaseAnalysis()};addButton(root,"Documents"){if(requireSignedIn())showDocuments()}}
    private fun showDarkMode(){getSharedPreferences("ga_law_help", MODE_PRIVATE).edit().putBoolean("navy_gold_dark", true).apply();toast("Dark mode keeps the navy and gold GA.LAW.HELP theme.");showHome()}
    private fun logOutFromDrawer(){if(api.isAnonymous){toast("You're not signed in to an account.");showHome();return};thread{runCatching{api.logout()};runCatching{api.ensureSession()};runOnUiThread{toast("Signed out. You can keep using GA.LAW.HELP without an account.");showHome()}}}
    private fun showCreateCase(){val root=page("Add Case","Create the case file first; evidence and analysis can be added afterward.");val title=input("Case title");val county=input("Georgia county");val stage=input("Stage (pretrial, appeal, etc.)");val narrative=input("What happened?",true);val typeGroup=RadioGroup(this).apply{orientation=RadioGroup.HORIZONTAL;addView(RadioButton(this@HomeActivity).apply{id=View.generateViewId();text="Criminal";setTextColor(Color.WHITE);isChecked=true;tag="criminal"});addView(RadioButton(this@HomeActivity).apply{id=View.generateViewId();text="Civil";setTextColor(Color.WHITE);tag="civil"});contentDescription="Case type"};root.addView(label("Case type",14f).apply{setTextColor(muted)});root.addView(typeGroup);listOf(title,county,stage,narrative).forEach{root.addView(it,LinearLayout.LayoutParams(-1,-2).apply{setMargins(0,dp(5),0,dp(5))})};addButton(root,"Save Case"){if(title.text.toString().trim().isBlank())return@addButton toast("Enter a case title.");runTask("Creating case…",{showCreateCase()}){val caseType=(typeGroup.findViewById<RadioButton>(typeGroup.checkedRadioButtonId)?.tag as? String)?:"criminal";val created=api.createCase(title.text.toString().trim(),county.text.toString().trim(),stage.text.toString().trim(),narrative.text.toString().trim(),caseType);val id=created.optInt("id");runOnUiThread{if(id>0)showCase(id)else showCases()}}}}
    private fun showCase(caseId:Int){val root=page("Case","Case workspace");root.addView(label("Loading case…",14f).apply{setTextColor(muted)});runTask("Loading case…",{showCase(caseId)}){val detail=api.caseDetail(caseId);runOnUiThread{root.removeViews(2,root.childCount-2);root.addView(label(detail.optString("title","Case #$caseId"),23f,true));val summary=listOf(detail.optString("county"),detail.optString("stage"),detail.optString("narrative")).filter{it.isNotBlank()}.joinToString("\n\n");if(summary.isNotBlank())root.addView(label(summary,14f).apply{setTextColor(muted)});addButton(root,"Case Timeline"){showTimeline(caseId)};addButton(root,"Documents & Evidence"){showCaseDocuments(caseId)};addButton(root,"Innocence & Motion Review"){showInnocenceAnalysis(caseId)};addButton(root,"Case Chat"){showCaseChat(caseId,detail.optString("title"))};addButton(root,"Charge Check: What Could I Be Charged With?"){showChargeCheck(caseId,detail.optString("title"))};addButton(root,"Civil Case Check: Claims, Court & Deadlines"){showCivilCheck(caseId,detail.optString("title"))};addButton(root,"Verified Motion Screen"){showMotionScreen(caseId)};addButton(root,"Run General Case Analysis"){runCaseAnalysis(caseId)};addButton(root,"Why / Explain the Case"){showCaseJson("Why this matters",{api.why(caseId)})};addButton(root,"Red-Team Review"){showCaseJson("Red-Team Review",{api.redTeam(caseId)})};addButton(root,"Second Look"){showCaseJson("Second Look",{api.secondLook(caseId)})}}}}
    // ---------- Case Chat (mockup chat layout, scoped to one case) ----------
    private fun showCaseChat(caseId:Int,caseTitle:String=""){ val t=ChatStore.open(this,ChatStore.caseKey(caseId)); lateinit var c:GaScreens.Chat
        c=GaScreens.caseChat(ui,nav,clean(caseTitle),{q->sendCaseChat(c,caseId,t,q)},listOf(
            "Explain in simple terms" to { if(!t.hasAnswer()) toast("Ask a question first.") else sendCaseChat(c,caseId,t,"Explain your last answer in simple terms.") },
            "What deadlines apply?" to { sendCaseChat(c,caseId,t,"What deadlines could apply to this case? Cite only verified Georgia authority.") },
            "Back to case" to { showCase(caseId) }))
        wireChatDelete(c,t); show(c.root); c.bot("Ask anything about this case. Answers use your case file, recent messages, and verified Georgia authority only. Confirm deadlines and strategy with qualified Georgia counsel.",now()); t.messages.forEach{ if(it.mine) c.user(it.text,it.time,it.id) else c.bot(it.text,it.time,it.id) } }
    private fun sendCaseChat(c:GaScreens.Chat,caseId:Int,t:ChatTranscript,raw:String){ val text=raw.trim(); if(text.isBlank())return toast("Enter a question first."); if(text.length>4000)return toast("Message is too long. Use 4,000 characters or fewer."); c.input.setText("")
        val history=JSONArray(); t.roleHistory(20).forEach{(r,m)->history.put(JSONObject().put("role",r).put("content",m))}
        val mine=t.add(true,text,now()); c.user(text,mine.time,mine.id); askCaseChat(c,caseId,t,text,history) }
    private fun askCaseChat(c:GaScreens.Chat,caseId:Int,t:ChatTranscript,text:String,history:JSONArray){ val stop=c.progress(listOf("Reviewing your case","Looking up Georgia law","Writing your answer","Almost done — thanks for waiting"))
        thread{ try{ val result=api.caseChat(caseId,text,history); val answer=GroundedLegalResult.answer(result).ifBlank{"No grounded case analysis was returned. Add specific facts and try again."}; val authorities=GroundedLegalResult.authoritySummary(result); val lt=lawyerTake(result)
            runOnUiThread{ stop(); val full=answer+(if(authorities.isNotBlank())"\n\n"+authorities else ""); val st=ShareText.answer(text,full,lt); val bot=t.add(false,full,now(),st)
                c.bot(full,bot.time,bot.id); if(lt!=null)c.attach(GaScreens.lawyerCard(ui,lt){x->showLaw(x.citation.replace(Regex("\\s*\\(text as of[^)]*\\)"),""))}); c.actions({shareOut(st)},{copyOut(st)}); c.findHelp{showFindHelp()}; c.followUps(TalkToMeController.followUps(result)){f->sendCaseChat(c,caseId,t,f)} } }
        catch(e:Exception){ runOnUiThread{ stop(); val bot=t.add(false,AiErrors.message(e),now(),inContext=false); c.bot(bot.text,bot.time,bot.id); if(AiErrors.isRetryable(e)) c.retry{ t.delete(bot.id); c.remove(bot.id); askCaseChat(c,caseId,t,text,history) } } } } }
    private fun showTimeline(caseId:Int){val root=page("Case Timeline","Events from first to latest.");runTask("Loading timeline…",{showTimeline(caseId)}){val items=api.timeline(caseId);runOnUiThread{renderJsonArray(root,items,"No timeline events yet.")}}}
    private fun showCaseAnalysis(){if(!requireSignedIn())return; val root=page("Case Analysis","Choose a case, then tell GA.LAW.HELP details that may matter to innocence, reasonable doubt, motions, or post-conviction review.");runTask("Loading cases…",{showCaseAnalysis()}){val cases=api.cases();runOnUiThread{if(cases.length()==0)root.addView(label("Create a case first.",14f).apply{setTextColor(muted)});for(i in 0 until cases.length()){val item=cases.optJSONObject(i)?:continue;val id=item.optInt("id");addButton(root,item.optString("title","Case #$id")){showInnocenceAnalysis(id)}}}}}
    private fun showInnocenceAnalysis(caseId:Int){val root=page("Innocence & Motion Review","Tell the app what happened, what evidence exists, what seems wrong, and anything that may show innocence or reasonable doubt. The app will look for issues and verified Georgia authority without assuming guilt or innocence.");val facts=input("Add case details: alibi, witnesses, identification, video, DNA, statements, searches, withheld evidence, changed testimony, missing proof, or new evidence…",true).apply{minLines=8};root.addView(facts,LinearLayout.LayoutParams(-1,-2).apply{setMargins(0,dp(6),0,dp(8))});root.addView(label("Important: describe facts as accurately as possible. The analysis separates affirmative innocence evidence from reasonable-doubt or insufficiency issues.",13f).apply{setTextColor(muted)});addButton(root,"Analyze Case Details"){val additional=facts.text.toString().trim();runTask("Analyzing case details…",{showInnocenceAnalysis(caseId)}){val result=api.innocenceAnalysis(caseId,additional);runOnUiThread{renderInnocenceResult(root,result,caseId)}}};addButton(root,"Back to Case"){showCase(caseId)}}
    private fun renderInnocenceResult(root:LinearLayout,result:JSONObject,caseId:Int){val review=result.optJSONObject("innocence_review");val motion=result.optJSONObject("motion_and_remedy_review");root.addView(label("Analysis Results",22f,true));if(review!=null){val interpretation=review.optString("interpretation");if(interpretation.isNotBlank())root.addView(label(interpretation,14f).apply{setTextColor(muted)});val signals=review.optJSONArray("issue_signals")?:JSONArray();root.addView(label("Potential Issues",18f,true));renderJsonArray(root,signals,"No specific innocence/doubt signal was identified from the supplied details. Add more facts or records rather than treating this as a negative conclusion.");val questions=review.optJSONArray("follow_up_questions")?:JSONArray();root.addView(label("Questions to Investigate",18f,true));renderJsonArray(root,questions,"No additional questions generated.")};if(motion!=null){root.addView(label("Motions / Remedies to Research",18f,true));val analysis=motion.optString("analysis");if(analysis.isNotBlank())root.addView(label(analysis,14f));val coverage=motion.optJSONObject("authority_coverage");if(coverage!=null)root.addView(label("Verified-authority coverage\n${coverage.toString(2)}",13f).apply{setTextColor(muted)})};root.addView(label(result.optString("notice","Verify facts, current authority, deadlines, and filing requirements before relying on this analysis."),12f).apply{setTextColor(muted)});addButton(root,"Analyze More Details"){showInnocenceAnalysis(caseId)};addButton(root,"Back to Case"){showCase(caseId)}}
    private fun runCaseAnalysis(caseId:Int){val root=page("Case Analysis","Running a fresh general case review.");root.addView(label("Analyzing…",14f).apply{setTextColor(muted)});runTask("Running case analysis…",{runCaseAnalysis(caseId)}){val result=api.runAnalysis(caseId);runOnUiThread{root.removeViews(2,root.childCount-2);root.addView(label(pretty(result),14f));addButton(root,"Innocence & Motion Review"){showInnocenceAnalysis(caseId)};addButton(root,"Back to Case"){showCase(caseId)}}}}
    private fun showMotionScreen(caseId:Int){val root=page("Verified Motion Screen","Login-only screening for this saved case. This is not a filing and does not certify current Georgia law.");val facts=input("Additional facts for motion screening",true);root.addView(facts);addButton(root,"Run motion screen"){runTask("Screening motions…",{showMotionScreen(caseId)}){val result=api.motionScreen(caseId, facts.text.toString().trim());runOnUiThread{while(root.childCount>4)root.removeViewAt(root.childCount-1);val analysis=result.optString("analysis").ifBlank{result.optString("answer")}.ifBlank{pretty(result)};root.addView(label(analysis,14f));root.addView(label("Do not treat unverified citations as current Georgia law. Confirm the official source, deadlines, and procedural posture before relying on this screen.",13f).apply{setTextColor(muted)})}}}}
    private fun showCaseJson(title:String,loader:()->JSONObject){val root=page(title,"Case review output");runTask("Loading…",{showHome()}){val result=loader();runOnUiThread{root.addView(label(pretty(result),14f))}}}
    private fun showCourtInfo(){val root=page("Court Info","Official Georgia court information and self-help resources.");addButton(root,"Georgia Courts"){openUrl("https://georgiacourts.gov/")};addButton(root,"Find a Court"){openUrl("https://georgiacourts.gov/georgia-courts-directory/")};root.addView(label("Court dates, filing rules and deadlines can vary by court. Confirm case-specific requirements with the court or qualified counsel.",14f).apply{setTextColor(muted)})}
    private fun showLegalForms(){val root=page("Legal Forms","Official starting points for criminal, civil, and family matters. Form text is not stored here.");addButton(root,"Criminal — public defender council"){openUrl("https://gapubdef.org/")};addButton(root,"Civil — Georgia Courts self-help"){openUrl("https://georgiacourts.gov/a2j/")};addButton(root,"Family — Georgia Legal Aid"){openUrl("https://www.georgialegalaid.org/")};root.addView(label("Confirm a form is current and accepted by the court before filing. These links are not Lexis annotations and are not a filing.",14f).apply{setTextColor(muted)})}
    private fun showLegalTools(){if(!requireSignedIn())return; val root=page("Legal Tools","Case analysis, legal research, forms and court resources.");addButton(root,"Case Analysis"){showCaseAnalysis()};addButton(root,"Georgia Laws"){showGeorgiaLaws()};addButton(root,"Legal Forms"){showLegalForms()};addButton(root,"Court Info"){showCourtInfo()};addButton(root,"Know Your Rights"){showKnowYourRights()}}
    private fun showKnowYourRights(){val root=page("Know Your Rights","Guest information only. Do not resist, lie, or destroy evidence.");listOf("Arrest" to "If arrested, do not resist or run. You may state that you are remaining silent and want a lawyer.","Police encounter" to "Keep your hands visible. You may ask whether you are free to leave and state that you do not consent to a search. Do not physically interfere.","Court" to "Court dates and filing rules vary. Do not ignore a court date. Ask the court or a lawyer before relying on a deadline.","Jail" to "Calls and common areas may be recorded. Do not discuss case facts there. You may ask for a lawyer.","Constitutional rights" to "You may clearly invoke the right to remain silent and the right to a lawyer. This screen is not a substitute for a licensed Georgia attorney.").forEach{(title,body)->addButton(root,title){val topic=page(title,"General information. Guest rights stay on /public/rights-assistant.");topic.addView(label(body,15f));addButton(topic,"Ask without signing in"){showTalkToMe()}}};root.addView(label("Do not resist, lie, or destroy evidence. Private cases stay login-only.",14f).apply{setTextColor(muted)})}
    private fun showResources(){val root=page("Resources","Georgia courts, legal aid and assistance resources.");addButton(root,"Georgia Legal Aid"){openUrl("https://www.georgialegalaid.org/")};addButton(root,"Georgia Courts"){openUrl("https://georgiacourts.gov/")};addButton(root,"Georgia Public Defender Council"){openUrl("https://gapubdef.org/")};addButton(root,"988 Crisis & Suicide Lifeline"){openUrl("https://988lifeline.org/")}}
    private fun showCaseDocuments(caseId:Int){val root=page("Documents","Evidence and files attached to this case.");addButton(root,"+ Upload Document"){pendingUploadCaseId=caseId;pickDocument.launch(arrayOf("application/pdf","image/*","text/*","application/msword","application/vnd.openxmlformats-officedocument.wordprocessingml.document"))};runTask("Loading documents…",{showCaseDocuments(caseId)}){val items=api.evidence(caseId);runOnUiThread{renderJsonArray(root,items,"No documents uploaded yet.")}}}
    private fun pretty(obj:JSONObject):String{val preferred=listOf("title","citation","summary","analysis","answer","detail","description","status","county","stage","issue","kind","note");val lines=preferred.mapNotNull{key->obj.optString(key).takeIf{it.isNotBlank()}?.let{"$key: $it"}};return if(lines.isNotEmpty())lines.joinToString("\n\n")else obj.toString(2)}
    private fun openUrl(url:String){runCatching{startActivity(Intent(Intent.ACTION_VIEW,Uri.parse(url)))}.onFailure{toast("No browser is available for this link.")}}
    private fun renderJsonArray(root:LinearLayout,items:JSONArray,emptyMessage:String){if(items.length()==0){root.addView(label(emptyMessage,14f).apply{setTextColor(muted)});return};for(i in 0 until items.length()){val item=items.opt(i);val text=when(item){is JSONObject->pretty(item);else->item?.toString().orEmpty()};root.addView(label(text,14f).apply{setPadding(dp(14),dp(12),dp(14),dp(12));background=ui.glowCard(GaUi.CARD,GaUi.STROKE_SOFT,12,glow=false)},LinearLayout.LayoutParams(-1,-2).apply{setMargins(0,dp(5),0,dp(5))})}}
    private fun runTask(message:String,retry:()->Unit,work:()->Unit){thread{try{work()}catch(e:Exception){runOnUiThread{showError(e.message?:"Something went wrong. Please try again.",retry)}}}}
    private fun showError(message:String,retry:()->Unit){val root=page("Couldn’t complete that","Your app is still usable. You can retry or return Home.");root.addView(label(message,15f));addButton(root,"Retry"){retry()};addButton(root,"Home"){showHome()}}
    private fun shareOut(text:String){ runCatching{startActivity(Intent.createChooser(Intent(Intent.ACTION_SEND).setType("text/plain").putExtra(Intent.EXTRA_SUBJECT,"GA.LAW.HELP").putExtra(Intent.EXTRA_TEXT,text),"Share"))}.onFailure{toast("No app is available to share with.")} }
    private fun copyOut(text:String){ (getSystemService(CLIPBOARD_SERVICE) as android.content.ClipboardManager).setPrimaryClip(android.content.ClipData.newPlainText("GA.LAW.HELP",text)); toast("Copied with citations.") }
    private fun toast(message:String)=Toast.makeText(this,message,Toast.LENGTH_SHORT).show()
}
