package help.galaw.standalone

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.graphics.Color
import android.graphics.Typeface
import android.graphics.drawable.GradientDrawable
import android.os.Bundle
import android.speech.RecognizerIntent
import android.view.Gravity
import android.widget.*
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import org.json.JSONObject
import kotlin.concurrent.thread

/** Native GA.LAW.HELP legal retrieval and grounded-analysis screen. No browser redirects. */
class InternalLegalSearchActivity : AppCompatActivity() {
    private lateinit var api: ApiClient
    private var speechTarget: EditText? = null
    private var activeMode: String = "case_lookup"
    private val navy=Color.rgb(3,17,30);private val panel=Color.rgb(8,31,49);private val blue=Color.rgb(37,168,255);private val muted=Color.rgb(170,190,203)
    private fun dp(v:Int)=(v*resources.displayMetrics.density).toInt()
    private fun grounded(mode:String)=mode in setOf("case_analysis","rights","motions","talk_to_me")

    private fun guest(mode:String)=mode in setOf("rights","talk_to_me")
    private fun statusFor(mode:String)=when{
        guest(mode)->"Looking up free guest rights help. This does not require a login and is not a claim of current Georgia law."
        grounded(mode)->"AI is analyzing the facts and checking verified internal authority…"
        else->"Searching the internal legal corpus…"
    }
    private fun lookup(mode:String, q:String): org.json.JSONObject {
        if (mode == "rights" || mode == "talk_to_me") {
            GuestPublicApi.encounter(BuildConfig.API_BASE_URL, q)
            val raw = GuestPublicApi.rightsAssistant(BuildConfig.API_BASE_URL, q, if (mode == "talk_to_me") "talk_to_me" else "rights")
            if (!raw.has("answer") && raw.has("analysis")) raw.put("answer", raw.optString("analysis"))
            raw.put("login_required", false)
            return raw
        }
        return if (grounded(mode)) api.groundedLegalAssistant(q, mode) else api.internalLegalSearch(q, mode)
    }


    private val speechLauncher=registerForActivityResult(ActivityResultContracts.StartActivityForResult()){result->if(result.resultCode==RESULT_OK){val heard=result.data?.getStringArrayListExtra(RecognizerIntent.EXTRA_RESULTS)?.firstOrNull()?.trim().orEmpty();if(heard.isNotBlank()){speechTarget?.let{target->val existing=target.text.toString().trim();target.setText(listOf(existing,heard).filter{it.isNotBlank()}.joinToString("\n"));target.setSelection(target.text.length)}}}}
    private val microphonePermission=registerForActivityResult(ActivityResultContracts.RequestPermission()){granted->if(granted)startSpeechCapture()else Toast.makeText(this,"Microphone permission is needed only when you choose Listen.",Toast.LENGTH_LONG).show()}

    override fun onCreate(savedInstanceState:Bundle?){
        super.onCreate(savedInstanceState);api=ApiClient(this);val mode=intent.getStringExtra("mode")?:"case_lookup";activeMode=mode;val title=intent.getStringExtra("title")?:titleFor(mode)
        val shell=LinearLayout(this).apply{orientation=LinearLayout.VERTICAL;setBackgroundColor(navy)};val body=LinearLayout(this).apply{orientation=LinearLayout.VERTICAL;setPadding(dp(16),dp(16),dp(16),dp(28))}
        body.addView(text("←  $title",Color.WHITE,23f,true).apply{setPadding(0,dp(8),0,dp(12));setOnClickListener{finish()}});body.addView(text(descriptionFor(mode),muted,13f))
        val query=EditText(this).apply{hint=hintFor(mode);setHintTextColor(muted);setTextColor(Color.WHITE);minLines=if(grounded(mode))4 else 1;gravity=Gravity.TOP;setPadding(dp(14),dp(12),dp(14),dp(12));background=rounded(panel,blue)};body.addView(query,LinearLayout.LayoutParams(-1,-2))
        if(mode=="talk_to_me"){speechTarget=query;body.addView(Button(this).apply{text="🎙 Listen & transcribe";isAllCaps=false;setTextColor(Color.WHITE);background=rounded(Color.rgb(13,56,78),blue);setOnClickListener{requestSpeechCapture()}},LinearLayout.LayoutParams(-1,-2).apply{setMargins(0,dp(10),0,0)});body.addView(text("Listening starts only when you tap the microphone. Review or edit the transcript before sending it for AI legal analysis.",muted,11f))}
        val search=Button(this).apply{text=buttonFor(mode);isAllCaps=false;setTextColor(Color.WHITE);background=rounded(Color.rgb(10,39,62),Color.rgb(32,100,146))};body.addView(search,LinearLayout.LayoutParams(-1,-2).apply{setMargins(0,dp(10),0,dp(12))})
        val results=LinearLayout(this).apply{orientation=LinearLayout.VERTICAL};body.addView(results);body.addView(Button(this).apply{text="Home";isAllCaps=false;setOnClickListener{startActivity(Intent(this@InternalLegalSearchActivity,HomeActivity::class.java).apply{addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP or Intent.FLAG_ACTIVITY_SINGLE_TOP)});finish()}},LinearLayout.LayoutParams(-1,-2).apply{setMargins(0,dp(12),0,0)})
        shell.addView(ScrollView(this).apply{addView(body)},LinearLayout.LayoutParams(-1,-1));setContentView(shell)
        search.setOnClickListener{val q=query.text.toString().trim();if(q.isBlank()){Toast.makeText(this,"Enter details first.",Toast.LENGTH_SHORT).show();return@setOnClickListener};search.isEnabled=false;results.removeAllViews();results.addView(text(statusFor(mode),muted));thread{try{val response=lookup(mode,q);runOnUiThread{render(results,response,grounded(mode)||guest(mode));search.isEnabled=true}}catch(e:Exception){runOnUiThread{results.removeAllViews();results.addView(text(e.message?:"Request failed. Edit the details and try again.",Color.rgb(245,150,150)));search.isEnabled=true}}}}
    }

    private fun requestSpeechCapture(){if(ContextCompat.checkSelfPermission(this,Manifest.permission.RECORD_AUDIO)==PackageManager.PERMISSION_GRANTED)startSpeechCapture()else microphonePermission.launch(Manifest.permission.RECORD_AUDIO)}
    private fun startSpeechCapture(){val intent=Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply{putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL,RecognizerIntent.LANGUAGE_MODEL_FREE_FORM);putExtra(RecognizerIntent.EXTRA_PROMPT,"Describe what is happening. You can edit the transcript before analysis.");putExtra(RecognizerIntent.EXTRA_MAX_RESULTS,1)};if(intent.resolveActivity(packageManager)==null){Toast.makeText(this,"Speech recognition is not available on this device. You can still type what is happening.",Toast.LENGTH_LONG).show();return};speechLauncher.launch(intent)}

    private fun render(root:LinearLayout,response:JSONObject,isGrounded:Boolean){
        root.removeAllViews();if(isGrounded){val analysis=response.optString("analysis").takeUnless{it.isBlank()||it=="null"};val sections=response.optJSONObject("sections");when(activeMode){"talk_to_me"->renderTypedTalkToMe(root,sections,analysis);"case_analysis"->renderTypedCaseAnalysis(root,sections,analysis);"rights"->renderTypedRights(root,sections,analysis);"motions"->renderTypedMotions(root,sections,analysis);else->{root.addView(text("AI Analysis",Color.WHITE,20f,true));root.addView(cardText(analysis?:response.optString("coverage_notice","Verified authority was insufficient for a grounded analysis.")))}};val count=response.optInt("grounded_authority_count",0);root.addView(text("Verified Supporting Authorities ($count)",Color.WHITE,20f,true));renderAuthorities(root,response.optJSONArray("authorities"),true)}else{root.addView(text("Internal legal results",Color.WHITE,20f,true));renderAuthorities(root,response.optJSONArray("hits"),false)};val notice=response.optString("coverage_notice");if(notice.isNotBlank()&&notice!="null")root.addView(text(notice,muted,11f))
    }
    private fun renderTypedTalkToMe(root:LinearLayout,sections:JSONObject?,fallback:String?){root.addView(text("Live Guidance",Color.WHITE,20f,true));renderSectionCards(root,sections,listOf("what_appears_to_be_happening" to "What appears to be happening","safest_immediate_steps" to "Safest immediate steps","your_rights" to "Your rights","law_enforcement_limits" to "What law enforcement may and may not do","lawful_things_to_say_or_do" to "What you can lawfully say or do","verified_georgia_authority" to "Verified Georgia authority","important_limitations" to "Important limitations"),fallback,"Verified authority was insufficient for grounded live guidance.")}
    private fun renderTypedCaseAnalysis(root:LinearLayout,sections:JSONObject?,fallback:String?){root.addView(text("Case Analysis",Color.WHITE,20f,true));renderSectionCards(root,sections,listOf("facts_to_verify" to "Facts to verify","legal_issues" to "Legal issues","prosecution_arguments" to "Prosecution arguments","defense_arguments" to "Defense arguments","possible_motions" to "Possible motions","practical_next_steps" to "Practical next steps","verified_georgia_authority" to "Verified Georgia authority","important_limitations" to "Important limitations"),fallback,"No structured case analysis was available.")}
    private fun renderTypedRights(root:LinearLayout,sections:JSONObject?,fallback:String?){root.addView(text("Rights Analysis",Color.WHITE,20f,true));renderSectionCards(root,sections,listOf("situation" to "Situation","rights_that_may_apply" to "Rights that may apply","law_enforcement_authority" to "Law enforcement authority","law_enforcement_limits" to "Law enforcement limits","lawful_options" to "Lawful options","verified_georgia_authority" to "Verified Georgia authority","important_limitations" to "Important limitations"),fallback,"No structured rights analysis was available.")}
    private fun renderTypedMotions(root:LinearLayout,sections:JSONObject?,fallback:String?){root.addView(text("Motions & Rules Analysis",Color.WHITE,20f,true));renderSectionCards(root,sections,listOf("case_issue" to "Case issue","potential_motions" to "Potential motions","required_facts_or_evidence" to "Required facts or evidence","opposing_arguments" to "Opposing arguments","procedural_questions_to_verify" to "Procedural questions to verify","verified_georgia_authority" to "Verified Georgia authority","important_limitations" to "Important limitations"),fallback,"No structured motions analysis was available.")}
    private fun renderSectionCards(root:LinearLayout,sections:JSONObject?,fields:List<Pair<String,String>>,fallback:String?,emptyMessage:String){var shown=0;if(sections!=null)for((key,label)in fields){val value=sections.optString(key).trim();if(value.isNotBlank()&&value!="null"){addGuidanceCard(root,label,value);shown++}};if(shown==0)root.addView(cardText(if(!fallback.isNullOrBlank())fallback else emptyMessage))}
    private fun addGuidanceCard(root:LinearLayout,heading:String,body:String){val card=LinearLayout(this).apply{orientation=LinearLayout.VERTICAL;setPadding(dp(14),dp(12),dp(14),dp(12));background=rounded(panel,Color.rgb(28,78,111))};card.addView(text(heading,if(heading in setOf("Safest immediate steps","Defense arguments","Possible motions","Rights that may apply","Potential motions","Lawful options"))Color.rgb(255,211,105)else blue,15f,true));card.addView(text(body,Color.rgb(218,228,235),14f));root.addView(card,LinearLayout.LayoutParams(-1,-2).apply{setMargins(0,dp(6),0,dp(6))})}
    private fun renderAuthorities(root:LinearLayout,hits:org.json.JSONArray?,verifiedOnly:Boolean){var shown=0;if(hits!=null)for(i in 0 until hits.length()){val h=hits.optJSONObject(i)?:continue;val verification=h.optString("verification_status").lowercase();if(verifiedOnly&&verification !in setOf("verified","official","validated","confirmed"))continue;shown++;val card=LinearLayout(this).apply{orientation=LinearLayout.VERTICAL;setPadding(dp(13),dp(11),dp(13),dp(11));background=rounded(panel,Color.rgb(28,78,111))};val recordType=h.optString("record_type").trim().lowercase();val badge=when(recordType){"case","opinion","decision"->"GEORGIA CASE";"statute","code","law"->"GEORGIA STATUTE";else->recordType.uppercase().takeIf{it.isNotBlank()}?:"LEGAL AUTHORITY"};card.addView(text(badge,blue,11f,true));card.addView(text(h.optString("title","Legal authority"),Color.WHITE,16f,true));val citation=h.optString("citation");if(citation.isNotBlank()&&citation!="null")card.addView(text(citation,Color.rgb(226,181,78),13f,true));addMetadata(card,h);val excerpt=h.optString("excerpt");if(excerpt.isNotBlank()&&excerpt!="null")card.addView(text(excerpt,Color.rgb(218,228,235),13f));root.addView(card,LinearLayout.LayoutParams(-1,-2).apply{setMargins(0,dp(6),0,dp(6))})};if(shown==0)root.addView(text(if(verifiedOnly)"No verified supporting authority was available. Any general legal information above still requires Georgia-authority verification."else"No indexed authority matched this search. GA.LAW.HELP will not invent a case or citation.",muted))}
    private fun addMetadata(card:LinearLayout,h:JSONObject){val rows=listOf("court" to "Court","docket_number" to "Case / docket","decision_date" to "Decision date","statute_section" to "Code section","effective_date" to "Effective date","jurisdiction" to "Jurisdiction","verification_status" to "Verification","currency_status" to "Currency","precedential_status" to "Precedential status","status_checked_at" to "Status checked");for((key,label)in rows){val value=h.optString(key).trim();if(value.isNotBlank()&&value!="null"&&value!="unknown")card.addView(text("$label: $value",muted,11f))};val treatment=h.optJSONArray("negative_treatment");if(treatment!=null&&treatment.length()>0){val values=(0 until treatment.length()).mapNotNull{treatment.optString(it).takeIf{v->v.isNotBlank()}};if(values.isNotEmpty())card.addView(text("Negative treatment: ${values.joinToString(", ")}",Color.rgb(245,150,150),11f,true))}}
    private fun cardText(value:String)=text(value,Color.rgb(218,228,235),14f).apply{setPadding(dp(13),dp(11),dp(13),dp(11));background=rounded(panel,Color.rgb(28,78,111))}
    private fun text(value:String,color:Int,size:Float=14f,bold:Boolean=false)=TextView(this).apply{text=value;textSize=size;setTextColor(color);setPadding(0,dp(5),0,dp(5));if(bold)setTypeface(typeface,Typeface.BOLD)}
    private fun rounded(fill:Int,stroke:Int)=GradientDrawable().apply{setColor(fill);cornerRadius=dp(14).toFloat();setStroke(dp(1),stroke)}
    private fun titleFor(mode:String)=when(mode){"case_analysis"->"Case Analysis";"rights"->"Know Your Rights";"motions"->"Motions & Rules";"talk_to_me"->"Talk to Me";else->"Case & Law Lookup"}
    private fun descriptionFor(mode:String)=when(mode){"case_analysis"->"Describe what happened. The AI analyzes the facts, checks the internal Georgia legal corpus, and separates general issue-spotting from verified authority.";"rights"->"Describe the encounter. The AI separates the situation, possible rights, officer authority and limits, lawful options, and verified Georgia authority.";"motions"->"Describe the case stage and issue. The AI separates potential motions, required facts or evidence, opposing arguments, procedural questions, and verified Georgia authority.";"talk_to_me"->"Tell GA.LAW.HELP what is happening or what was said. Use the microphone or type, review the transcript, then the AI checks verified Georgia authority and explains the safest lawful options and relevant rights.";else->"Search public Georgia cases and statutes already indexed inside GA.LAW.HELP. Results stay in the app and show stored court, date, docket, statute, and authority-status metadata when available."}
    private fun hintFor(mode:String)=when(mode){"case_analysis"->"What happened in the case? Include charge, stage, evidence, search, statements, witnesses…";"rights"->"Example: Police stopped my car and asked to search…";"motions"->"Example: pretrial identification issue, search warrant, withheld evidence…";"talk_to_me"->"Say or type what is happening, including what was said or done…";else->"Charge, case name, citation, statute, or legal issue…"}
    private fun buttonFor(mode:String)=when(mode){"case_analysis"->"AI Analyze & Verify Authority";"rights"->"AI Check Rights & Authority";"motions"->"AI Analyze Motions & Rules";"talk_to_me"->"AI Analyze What’s Happening";else->"Search Internal Legal Library"}
}
