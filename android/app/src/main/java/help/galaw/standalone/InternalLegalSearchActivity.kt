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

    private val speechLauncher=registerForActivityResult(ActivityResultContracts.StartActivityForResult()){result->
        if(result.resultCode==RESULT_OK){val heard=result.data?.getStringArrayListExtra(RecognizerIntent.EXTRA_RESULTS)?.firstOrNull()?.trim().orEmpty();if(heard.isNotBlank()){speechTarget?.let{target->val existing=target.text.toString().trim();target.setText(listOf(existing,heard).filter{it.isNotBlank()}.joinToString("\n"));target.setSelection(target.text.length)}}}
    }
    private val microphonePermission=registerForActivityResult(ActivityResultContracts.RequestPermission()){granted->if(granted)startSpeechCapture()else Toast.makeText(this,"Microphone permission is needed only when you choose Listen.",Toast.LENGTH_LONG).show()}

    override fun onCreate(savedInstanceState:Bundle?){
        super.onCreate(savedInstanceState);api=ApiClient(this)
        val mode=intent.getStringExtra("mode")?:"case_lookup";activeMode=mode;val title=intent.getStringExtra("title")?:titleFor(mode)
        val shell=LinearLayout(this).apply{orientation=LinearLayout.VERTICAL;setBackgroundColor(navy)};val body=LinearLayout(this).apply{orientation=LinearLayout.VERTICAL;setPadding(dp(16),dp(16),dp(16),dp(28))}
        body.addView(text("←  $title",Color.WHITE,23f,true).apply{setPadding(0,dp(8),0,dp(12));setOnClickListener{finish()}});body.addView(text(descriptionFor(mode),muted,13f))
        val query=EditText(this).apply{hint=hintFor(mode);setHintTextColor(muted);setTextColor(Color.WHITE);minLines=if(grounded(mode))4 else 1;gravity=Gravity.TOP;setPadding(dp(14),dp(12),dp(14),dp(12));background=rounded(panel,blue)};body.addView(query,LinearLayout.LayoutParams(-1,-2))
        if(mode=="talk_to_me"){speechTarget=query;body.addView(Button(this).apply{text="🎙 Listen & transcribe";isAllCaps=false;setTextColor(Color.WHITE);background=rounded(Color.rgb(13,56,78),blue);setOnClickListener{requestSpeechCapture()}},LinearLayout.LayoutParams(-1,-2).apply{setMargins(0,dp(10),0,0)});body.addView(text("Listening starts only when you tap the microphone. Review or edit the transcript before sending it for AI legal analysis.",muted,11f))}
        val search=Button(this).apply{text=buttonFor(mode);isAllCaps=false;setTextColor(Color.WHITE);background=rounded(Color.rgb(10,39,62),Color.rgb(32,100,146))};body.addView(search,LinearLayout.LayoutParams(-1,-2).apply{setMargins(0,dp(10),0,dp(12))})
        val results=LinearLayout(this).apply{orientation=LinearLayout.VERTICAL};body.addView(results);body.addView(Button(this).apply{text="Home";isAllCaps=false;setOnClickListener{startActivity(Intent(this@InternalLegalSearchActivity,HomeActivity::class.java).apply{addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP or Intent.FLAG_ACTIVITY_SINGLE_TOP)});finish()}},LinearLayout.LayoutParams(-1,-2).apply{setMargins(0,dp(12),0,0)})
        shell.addView(ScrollView(this).apply{addView(body)},LinearLayout.LayoutParams(-1,-1));setContentView(shell)
        search.setOnClickListener{val q=query.text.toString().trim();if(q.isBlank()){Toast.makeText(this,"Enter details first.",Toast.LENGTH_SHORT).show();return@setOnClickListener};search.isEnabled=false;results.removeAllViews();results.addView(text(if(grounded(mode))"AI is analyzing the facts and checking verified internal authority…" else "Searching the internal legal corpus…",muted));thread{try{val response=if(grounded(mode))api.groundedLegalAssistant(q,mode)else api.internalLegalSearch(q,mode);runOnUiThread{render(results,response,grounded(mode));search.isEnabled=true}}catch(e:Exception){runOnUiThread{results.removeAllViews();results.addView(text(e.message?:"Request failed. Edit the details and try again.",Color.rgb(245,150,150)));search.isEnabled=true}}}}
    }

    private fun requestSpeechCapture(){if(ContextCompat.checkSelfPermission(this,Manifest.permission.RECORD_AUDIO)==PackageManager.PERMISSION_GRANTED)startSpeechCapture()else microphonePermission.launch(Manifest.permission.RECORD_AUDIO)}
    private fun startSpeechCapture(){val intent=Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply{putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL,RecognizerIntent.LANGUAGE_MODEL_FREE_FORM);putExtra(RecognizerIntent.EXTRA_PROMPT,"Describe what is happening. You can edit the transcript before analysis.");putExtra(RecognizerIntent.EXTRA_MAX_RESULTS,1)};if(intent.resolveActivity(packageManager)==null){Toast.makeText(this,"Speech recognition is not available on this device. You can still type what is happening.",Toast.LENGTH_LONG).show();return};speechLauncher.launch(intent)}

    private fun render(root:LinearLayout,response:JSONObject,isGrounded:Boolean){
        root.removeAllViews();if(isGrounded){val analysis=response.optString("analysis").takeUnless{it.isBlank()||it=="null"};if(activeMode=="talk_to_me"&&analysis!=null)renderTalkToMeCards(root,analysis)else{root.addView(text("AI Analysis",Color.WHITE,20f,true));root.addView(cardText(analysis?:response.optString("coverage_notice","Verified authority was insufficient for a grounded analysis.")))};val count=response.optInt("grounded_authority_count",0);root.addView(text("Verified Supporting Authorities ($count)",Color.WHITE,20f,true));renderAuthorities(root,response.optJSONArray("authorities"),true)}else{root.addView(text("Internal legal results",Color.WHITE,20f,true));renderAuthorities(root,response.optJSONArray("hits"),false)};val notice=response.optString("coverage_notice");if(notice.isNotBlank()&&notice!="null")root.addView(text(notice,muted,11f))
    }
    private fun renderTalkToMeCards(root:LinearLayout,analysis:String){
        root.addView(text("Live Guidance",Color.WHITE,20f,true));val headings=listOf("What appears to be happening","Safest immediate steps","Your rights","What law enforcement may and may not do","What you can lawfully say or do","Verified Georgia authority","Important limitations");val pattern=Regex("(?im)^\\s*(?:#{1,4}\\s*)?(?:\\d+[.)]\\s*)?("+headings.joinToString("|"){Regex.escape(it)}+")\\s*:?\\s*$");val matches=pattern.findAll(analysis).toList();if(matches.isEmpty()){root.addView(cardText(analysis));return};if(matches.first().range.first>0){val intro=analysis.substring(0,matches.first().range.first).trim();if(intro.isNotBlank())root.addView(cardText(intro))};matches.forEachIndexed{i,m->val heading=m.groupValues[1];val start=m.range.last+1;val end=if(i+1<matches.size)matches[i+1].range.first else analysis.length;val body=analysis.substring(start,end).trim().trimStart(':','-',' ');if(body.isNotBlank())addGuidanceCard(root,heading,body)}
    }
    private fun addGuidanceCard(root:LinearLayout,heading:String,body:String){val card=LinearLayout(this).apply{orientation=LinearLayout.VERTICAL;setPadding(dp(14),dp(12),dp(14),dp(12));background=rounded(panel,Color.rgb(28,78,111))};card.addView(text(heading,if(heading.equals("Safest immediate steps",true))Color.rgb(255,211,105)else blue,15f,true));card.addView(text(body,Color.rgb(218,228,235),14f));root.addView(card,LinearLayout.LayoutParams(-1,-2).apply{setMargins(0,dp(6),0,dp(6))})}
    private fun renderAuthorities(root:LinearLayout,hits:org.json.JSONArray?,verifiedOnly:Boolean){var shown=0;if(hits!=null)for(i in 0 until hits.length()){val h=hits.optJSONObject(i)?:continue;val verification=h.optString("verification_status").lowercase();if(verifiedOnly&&verification !in setOf("verified","official","validated","confirmed"))continue;shown++;val card=LinearLayout(this).apply{orientation=LinearLayout.VERTICAL;setPadding(dp(13),dp(11),dp(13),dp(11));background=rounded(panel,Color.rgb(28,78,111))};card.addView(text(h.optString("title","Legal authority"),Color.WHITE,16f,true));val citation=h.optString("citation");if(citation.isNotBlank()&&citation!="null")card.addView(text(citation,Color.rgb(226,181,78),13f,true));val excerpt=h.optString("excerpt");if(excerpt.isNotBlank())card.addView(text(excerpt,Color.rgb(218,228,235),13f));root.addView(card,LinearLayout.LayoutParams(-1,-2).apply{setMargins(0,dp(6),0,dp(6))})};if(shown==0)root.addView(text(if(verifiedOnly)"No verified supporting authority was available. GA.LAW.HELP did not generate an unsupported legal conclusion."else"No indexed authority matched this search. GA.LAW.HELP will not invent a case or citation.",muted))}
    private fun cardText(value:String)=text(value,Color.rgb(218,228,235),14f).apply{setPadding(dp(13),dp(11),dp(13),dp(11));background=rounded(panel,Color.rgb(28,78,111))}
    private fun text(value:String,color:Int,size:Float=14f,bold:Boolean=false)=TextView(this).apply{text=value;textSize=size;setTextColor(color);setPadding(0,dp(5),0,dp(5));if(bold)setTypeface(typeface,Typeface.BOLD)}
    private fun rounded(fill:Int,stroke:Int)=GradientDrawable().apply{setColor(fill);cornerRadius=dp(14).toFloat();setStroke(dp(1),stroke)}
    private fun titleFor(mode:String)=when(mode){"case_analysis"->"Case Analysis";"rights"->"Know Your Rights";"motions"->"Motions & Rules";"talk_to_me"->"Talk to Me";else->"Case & Law Lookup"}
    private fun descriptionFor(mode:String)=when(mode){"case_analysis"->"Describe what happened. The AI analyzes the facts, checks the internal Georgia legal corpus, and shows the verified authority supporting its analysis.";"rights"->"Describe the encounter. The AI checks applicable indexed authority and explains the rights analysis with verified support.";"motions"->"Describe the case stage and issue. The AI evaluates potentially relevant motions and rules against verified indexed authority.";"talk_to_me"->"Tell GA.LAW.HELP what is happening or what was said. Use the microphone or type, review the transcript, then the AI checks verified Georgia authority and explains the safest lawful options and relevant rights.";else->"Search public Georgia cases and statutes already indexed inside GA.LAW.HELP."}
    private fun hintFor(mode:String)=when(mode){"case_analysis"->"What happened in the case? Include charge, stage, evidence, search, statements, witnesses…";"rights"->"Example: Police stopped my car and asked to search…";"motions"->"Example: pretrial identification issue, search warrant, withheld evidence…";"talk_to_me"->"Say or type what is happening, including what was said or done…";else->"Charge, case name, citation, statute, or legal issue…"}
    private fun buttonFor(mode:String)=when(mode){"case_analysis"->"AI Analyze & Verify Authority";"rights"->"AI Check Rights & Authority";"motions"->"AI Analyze Motions & Rules";"talk_to_me"->"AI Analyze What’s Happening";else->"Search Internal Legal Library"}
}
