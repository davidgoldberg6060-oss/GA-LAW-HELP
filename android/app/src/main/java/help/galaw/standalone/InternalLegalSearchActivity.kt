package help.galaw.standalone

import android.content.Intent
import android.graphics.Color
import android.graphics.Typeface
import android.graphics.drawable.GradientDrawable
import android.os.Bundle
import android.view.Gravity
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import org.json.JSONObject
import kotlin.concurrent.thread

/** Native GA.LAW.HELP legal retrieval and grounded-analysis screen. No browser redirects. */
class InternalLegalSearchActivity : AppCompatActivity() {
    private lateinit var api: ApiClient
    private val navy=Color.rgb(3,17,30);private val panel=Color.rgb(8,31,49);private val blue=Color.rgb(37,168,255);private val muted=Color.rgb(170,190,203)
    private fun dp(v:Int)=(v*resources.displayMetrics.density).toInt()
    private fun grounded(mode:String)=mode in setOf("case_analysis","rights","motions","talk_to_me")

    override fun onCreate(savedInstanceState:Bundle?){
        super.onCreate(savedInstanceState);api=ApiClient(this)
        val mode=intent.getStringExtra("mode")?:"case_lookup";val title=intent.getStringExtra("title")?:titleFor(mode)
        val shell=LinearLayout(this).apply{orientation=LinearLayout.VERTICAL;setBackgroundColor(navy)}
        val body=LinearLayout(this).apply{orientation=LinearLayout.VERTICAL;setPadding(dp(16),dp(16),dp(16),dp(28))}
        body.addView(text("←  $title",Color.WHITE,23f,true).apply{setPadding(0,dp(8),0,dp(12));setOnClickListener{finish()}})
        body.addView(text(descriptionFor(mode),muted,13f))
        val query=EditText(this).apply{hint=hintFor(mode);setHintTextColor(muted);setTextColor(Color.WHITE);minLines=if(grounded(mode))4 else 1;gravity=Gravity.TOP;setPadding(dp(14),dp(12),dp(14),dp(12));background=rounded(panel,blue)}
        body.addView(query,LinearLayout.LayoutParams(-1,-2))
        val search=Button(this).apply{text=buttonFor(mode);isAllCaps=false;setTextColor(Color.WHITE);background=rounded(Color.rgb(10,39,62),Color.rgb(32,100,146))}
        body.addView(search,LinearLayout.LayoutParams(-1,-2).apply{setMargins(0,dp(10),0,dp(12))})
        val results=LinearLayout(this).apply{orientation=LinearLayout.VERTICAL};body.addView(results)
        body.addView(Button(this).apply{text="Home";isAllCaps=false;setOnClickListener{startActivity(Intent(this@InternalLegalSearchActivity,HomeActivity::class.java).apply{addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP or Intent.FLAG_ACTIVITY_SINGLE_TOP)});finish()}},LinearLayout.LayoutParams(-1,-2).apply{setMargins(0,dp(12),0,0)})
        shell.addView(ScrollView(this).apply{addView(body)},LinearLayout.LayoutParams(-1,-1));setContentView(shell)
        search.setOnClickListener{
            val q=query.text.toString().trim();if(q.isBlank()){Toast.makeText(this,"Enter details first.",Toast.LENGTH_SHORT).show();return@setOnClickListener}
            search.isEnabled=false;results.removeAllViews();results.addView(text(if(grounded(mode))"AI is analyzing the facts and checking verified internal authority…" else "Searching the internal legal corpus…",muted))
            thread{try{val response=if(grounded(mode))api.groundedLegalAssistant(q,mode) else api.internalLegalSearch(q,mode);runOnUiThread{render(results,response,grounded(mode));search.isEnabled=true}}catch(e:Exception){runOnUiThread{results.removeAllViews();results.addView(text(e.message?:"Request failed. Edit the details and try again.",Color.rgb(245,150,150)));search.isEnabled=true}}}
        }
    }

    private fun render(root:LinearLayout,response:JSONObject,isGrounded:Boolean){
        root.removeAllViews()
        if(isGrounded){
            val analysis=response.optString("analysis").takeUnless{it.isBlank()||it=="null"}
            root.addView(text("AI Analysis",Color.WHITE,20f,true))
            if(analysis!=null){root.addView(cardText(analysis))}else{root.addView(cardText(response.optString("coverage_notice","Verified authority was insufficient for a grounded analysis.")))}
            val count=response.optInt("grounded_authority_count",0);root.addView(text("Verified Supporting Authorities ($count)",Color.WHITE,20f,true))
            renderAuthorities(root,response.optJSONArray("authorities"),verifiedOnly=true)
        }else{
            root.addView(text("Internal legal results",Color.WHITE,20f,true));renderAuthorities(root,response.optJSONArray("hits"),verifiedOnly=false)
        }
        val notice=response.optString("coverage_notice");if(notice.isNotBlank()&&notice!="null")root.addView(text(notice,muted,11f))
    }

    private fun renderAuthorities(root:LinearLayout,hits:org.json.JSONArray?,verifiedOnly:Boolean){
        var shown=0
        if(hits!=null)for(i in 0 until hits.length()){
            val h=hits.optJSONObject(i)?:continue;val verification=h.optString("verification_status").lowercase()
            if(verifiedOnly&&verification !in setOf("verified","official","validated","confirmed"))continue
            shown++;val card=LinearLayout(this).apply{orientation=LinearLayout.VERTICAL;setPadding(dp(13),dp(11),dp(13),dp(11));background=rounded(panel,Color.rgb(28,78,111))}
            card.addView(text(h.optString("title","Legal authority"),Color.WHITE,16f,true));val citation=h.optString("citation");if(citation.isNotBlank()&&citation!="null")card.addView(text(citation,Color.rgb(226,181,78),13f,true));val corpus=h.optString("corpus").replace('_',' ');if(corpus.isNotBlank())card.addView(text(corpus.replaceFirstChar{it.uppercase()},blue,12f,true));val excerpt=h.optString("excerpt");if(excerpt.isNotBlank())card.addView(text(excerpt,Color.rgb(218,228,235),13f));if(verification.isNotBlank()&&verification!="null")card.addView(text("Verified status: $verification",muted,11f));root.addView(card,LinearLayout.LayoutParams(-1,-2).apply{setMargins(0,dp(6),0,dp(6))})
        }
        if(shown==0)root.addView(text(if(verifiedOnly)"No verified supporting authority was available. GA.LAW.HELP did not generate an unsupported legal conclusion." else "No indexed authority matched this search. GA.LAW.HELP will not invent a case or citation.",muted))
    }
    private fun cardText(value:String)=text(value,Color.rgb(218,228,235),14f).apply{setPadding(dp(13),dp(11),dp(13),dp(11));background=rounded(panel,Color.rgb(28,78,111))}
    private fun text(value:String,color:Int,size:Float=14f,bold:Boolean=false)=TextView(this).apply{text=value;textSize=size;setTextColor(color);setPadding(0,dp(5),0,dp(5));if(bold)setTypeface(typeface,Typeface.BOLD)}
    private fun rounded(fill:Int,stroke:Int)=GradientDrawable().apply{setColor(fill);cornerRadius=dp(14).toFloat();setStroke(dp(1),stroke)}
    private fun titleFor(mode:String)=when(mode){"case_analysis"->"Case Analysis";"rights"->"Know Your Rights";"motions"->"Motions & Rules";"talk_to_me"->"Talk to Me";"court_info"->"Georgia Court Info";"legal_forms"->"Georgia Legal Forms";"resources"->"Georgia Legal Resources";else->"Case & Law Lookup"}
    private fun descriptionFor(mode:String)=when(mode){"case_analysis"->"Describe what happened. The AI analyzes the facts, checks the internal Georgia legal corpus, and shows the verified authority supporting its analysis.";"rights"->"Describe the encounter. The AI checks applicable indexed authority and explains the rights analysis with verified support.";"motions"->"Describe the case stage and issue. The AI evaluates potentially relevant motions and rules against verified indexed authority.";"talk_to_me"->"Tell GA.LAW.HELP what is happening or what was said. The AI analyzes the situation and checks verified legal authority while keeping the experience inside the app.";"court_info"->"Search court procedure, jurisdiction, filing and court-related information already indexed inside GA.LAW.HELP.";"legal_forms"->"Describe the filing or case stage to find indexed form guidance, rules and related authority without leaving the app.";"resources"->"Describe the legal help or service you need. GA.LAW.HELP searches its internal resource and authority index.";else->"Search public Georgia cases and statutes already indexed inside GA.LAW.HELP."}
    private fun hintFor(mode:String)=when(mode){"case_analysis"->"What happened in the case? Include charge, stage, evidence, search, statements, witnesses…";"rights"->"Example: Police stopped my car and asked to search…";"motions"->"Example: pretrial identification issue, search warrant, withheld evidence…";"talk_to_me"->"Tell GA.LAW.HELP what is happening…";"court_info"->"Court, county, filing rule, deadline, jurisdiction…";"legal_forms"->"Form or filing needed, case type, court and stage…";"resources"->"Public defender, legal aid, court help, appeal assistance…";else->"Charge, case name, citation, statute, or legal issue…"}
    private fun buttonFor(mode:String)=when(mode){"case_analysis"->"AI Analyze & Verify Authority";"rights"->"AI Check Rights & Authority";"motions"->"AI Analyze Motions & Rules";"talk_to_me"->"AI Analyze What’s Happening";"court_info"->"Search Court Information";"legal_forms"->"Search Forms & Filing Guidance";"resources"->"Search Legal Resources";else->"Search Internal Legal Library"}
}
