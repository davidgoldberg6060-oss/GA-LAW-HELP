package help.galaw.standalone

import android.graphics.Color
import android.graphics.Typeface
import android.graphics.drawable.GradientDrawable
import android.os.Bundle
import android.view.Gravity
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import org.json.JSONObject
import kotlin.concurrent.thread

/** Native GA.LAW.HELP legal retrieval screen. No browser redirects. */
class InternalLegalSearchActivity : AppCompatActivity() {
    private lateinit var api: ApiClient
    private val navy = Color.rgb(3, 17, 30)
    private val panel = Color.rgb(8, 31, 49)
    private val blue = Color.rgb(37, 168, 255)
    private val muted = Color.rgb(170, 190, 203)
    private fun dp(v:Int)=(v*resources.displayMetrics.density).toInt()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState); api=ApiClient(this)
        val mode=intent.getStringExtra("mode") ?: "case_lookup"
        val title=intent.getStringExtra("title") ?: titleFor(mode)
        val shell=LinearLayout(this).apply{orientation=LinearLayout.VERTICAL;setBackgroundColor(navy)}
        val body=LinearLayout(this).apply{orientation=LinearLayout.VERTICAL;setPadding(dp(16),dp(16),dp(16),dp(28))}
        body.addView(TextView(this).apply{text="←  $title";textSize=23f;setTextColor(Color.WHITE);setTypeface(typeface,Typeface.BOLD);setPadding(0,dp(8),0,dp(12));setOnClickListener{finish()}})
        body.addView(TextView(this).apply{text=descriptionFor(mode);textSize=13f;setTextColor(muted);setPadding(0,0,0,dp(12))})
        val query=EditText(this).apply{hint=hintFor(mode);setHintTextColor(muted);setTextColor(Color.WHITE);minLines=if(mode=="case_analysis"||mode=="talk_to_me")4 else 1;gravity=Gravity.TOP;setPadding(dp(14),dp(12),dp(14),dp(12));background=rounded(panel,blue)}
        body.addView(query,LinearLayout.LayoutParams(-1,-2))
        val search=Button(this).apply{text=buttonFor(mode);isAllCaps=false;setTextColor(Color.WHITE);background=rounded(Color.rgb(10,39,62),Color.rgb(32,100,146))}
        body.addView(search,LinearLayout.LayoutParams(-1,-2).apply{setMargins(0,dp(10),0,dp(12))})
        val results=LinearLayout(this).apply{orientation=LinearLayout.VERTICAL}
        body.addView(results)
        shell.addView(ScrollView(this).apply{addView(body)},LinearLayout.LayoutParams(-1,-1));setContentView(shell)
        search.setOnClickListener{
            val q=query.text.toString().trim();if(q.isBlank()){Toast.makeText(this,"Enter details first.",Toast.LENGTH_SHORT).show();return@setOnClickListener}
            search.isEnabled=false;results.removeAllViews();results.addView(text("Searching the internal legal corpus…",muted))
            thread{
                try{val response=api.internalLegalSearch(q,mode);runOnUiThread{render(results,response);search.isEnabled=true}}
                catch(e:Exception){runOnUiThread{results.removeAllViews();results.addView(text(e.message?:"Search failed.",Color.rgb(245,150,150)));search.isEnabled=true}}
            }
        }
    }

    private fun render(root:LinearLayout,response:JSONObject){
        root.removeAllViews();val hits=response.optJSONArray("hits")
        if(hits==null||hits.length()==0){root.addView(text("No verified indexed authority matched this search. GA.LAW.HELP will not invent a case or citation.",muted));return}
        root.addView(text("Internal legal results",Color.WHITE,20f,true))
        for(i in 0 until hits.length()){
            val h=hits.optJSONObject(i)?:continue
            val card=LinearLayout(this).apply{orientation=LinearLayout.VERTICAL;setPadding(dp(13),dp(11),dp(13),dp(11));background=rounded(panel,Color.rgb(28,78,111))}
            card.addView(text(h.optString("title","Legal authority"),Color.WHITE,16f,true))
            val citation=h.optString("citation");if(citation.isNotBlank()&&citation!="null")card.addView(text(citation,Color.rgb(226,181,78),13f,true))
            val corpus=h.optString("corpus").replace('_',' ');if(corpus.isNotBlank())card.addView(text(corpus.replaceFirstChar{it.uppercase()},blue,12f,true))
            val excerpt=h.optString("excerpt");if(excerpt.isNotBlank())card.addView(text(excerpt,Color.rgb(218,228,235),13f,false))
            val verification=h.optString("verification_status");if(verification.isNotBlank()&&verification!="null")card.addView(text("Status: $verification",muted,11f,false))
            root.addView(card,LinearLayout.LayoutParams(-1,-2).apply{setMargins(0,dp(6),0,dp(6))})
        }
        root.addView(text(response.optString("coverage_notice","Results are limited to verified material indexed inside GA.LAW.HELP."),muted,11f,false))
    }
    private fun text(value:String,color:Int,size:Float=14f,bold:Boolean=false)=TextView(this).apply{text=value;textSize=size;setTextColor(color);setPadding(0,dp(5),0,dp(5));if(bold)setTypeface(typeface,Typeface.BOLD)}
    private fun rounded(fill:Int,stroke:Int)=GradientDrawable().apply{setColor(fill);cornerRadius=dp(14).toFloat();setStroke(dp(1),stroke)}
    private fun titleFor(mode:String)=when(mode){"case_analysis"->"Case Analysis";"rights"->"Know Your Rights";"motions"->"Motions & Rules";"talk_to_me"->"Talk to Me";else->"Case & Law Lookup"}
    private fun descriptionFor(mode:String)=when(mode){"case_analysis"->"Describe what happened. Search verified internal cases, statutes, rules, motions and law-enforcement authority relevant to those facts.";"rights"->"Describe the police encounter or rights question. Results stay inside the app and identify indexed authority.";"motions"->"Describe the case stage and issue to find potentially relevant motion and procedural authority.";"talk_to_me"->"Enter what is happening or what was said. This retrieves legal context from the app's internal corpus; it does not replace emergency services or a lawyer.";else->"Search public Georgia cases and statutes already indexed inside GA.LAW.HELP."}
    private fun hintFor(mode:String)=when(mode){"case_analysis"->"What happened in the case? Include charge, stage, evidence, search, statements, witnesses…";"rights"->"Example: Police stopped my car and asked to search…";"motions"->"Example: pretrial identification issue, search warrant, withheld evidence…";"talk_to_me"->"Tell GA.LAW.HELP what is happening…";else->"Charge, case name, citation, statute, or legal issue…"}
    private fun buttonFor(mode:String)=when(mode){"case_analysis"->"Analyze Against Internal Law";"rights"->"Check Rights & Authority";"motions"->"Find Motions & Rules";"talk_to_me"->"Get Legal Context";else->"Search Internal Legal Library"}
}
