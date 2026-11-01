package help.galaw.standalone

import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.text.Editable
import android.text.TextWatcher
import android.view.View
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import org.json.JSONObject

/** Data loaded from assets/funny_georgia.json. Every entry carries a citation and an https source. */
data class FunnyLaw(val title:String,val summary:String,val citation:String,val jurisdiction:String,val category:String,val sourceUrl:String,val status:String)
data class FunnyCase(val name:String,val court:String,val year:Int,val citation:String,val summary:String,val sourceUrl:String)

object FunnyGeorgiaData {
    fun parse(json:String):Pair<List<FunnyLaw>,List<FunnyCase>> {
        val o=JSONObject(json)
        val laws=o.getJSONArray("laws").let{a->(0 until a.length()).map{i->a.getJSONObject(i).let{FunnyLaw(it.getString("title"),it.getString("summary"),it.getString("citation"),it.getString("jurisdiction"),it.getString("category"),it.getString("source_url"),it.optString("status"))}}}
        val cases=o.getJSONArray("cases").let{a->(0 until a.length()).map{i->a.getJSONObject(i).let{FunnyCase(it.getString("name"),it.getString("court"),it.getInt("year"),it.getString("citation"),it.getString("summary"),it.getString("source_url"))}}}
        return laws to cases
    }
}

/** Builds the Funny & Weird Georgia Laws screen in the approved GA.LAW.HELP style (testable without an Activity). */
class FunnyGeorgiaScreen(private val ui:GaUi, private val laws:List<FunnyLaw>, private val cases:List<FunnyCase>, private val onBack:()->Unit, private val openSource:(String)->Unit, startOnCases:Boolean=false, private val bottomNav:View?=null) {
    private var showCases=startOnCases; private var query=""
    private lateinit var tabsHost:FrameLayout; private lateinit var list:LinearLayout; private lateinit var count:TextView
    fun build():View {
        val (root, body) = ui.screen(onBack, bottomNav)
        if(bottomNav==null) body.addView(ui.secondaryButton("← Back"){onBack()}.apply{contentDescription="Back"}, ui.lp(4,0))
        body.addView(ui.title("Funny & Weird Georgia Laws"))
        body.addView(ui.subtitle("Real Georgia laws and court cases that sound made up. Every card shows its citation — tap it to open the source."))
        tabsHost=FrameLayout(ui.context); body.addView(tabsHost, ui.lp(0,12,ui.dp(46)))
        val (searchBox, search) = ui.searchField("Search funny laws and cases...", glowing=false, height=50, showButton=false) { q -> query=q.trim().lowercase(); render() }
        search.contentDescription="Search funny laws and cases"
        search.addTextChangedListener(object:TextWatcher{override fun beforeTextChanged(s:CharSequence?,a:Int,b:Int,c:Int){};override fun onTextChanged(s:CharSequence?,a:Int,b:Int,c:Int){};override fun afterTextChanged(s:Editable?){query=s?.toString()?.trim()?.lowercase()?:"";render()}})
        body.addView(searchBox, ui.lp(0,6,ui.dp(50)))
        count=ui.note(""); body.addView(count)
        list=LinearLayout(ui.context).apply{orientation=LinearLayout.VERTICAL}; body.addView(list)
        body.addView(ui.note("Legal-information note: laws can be amended, repealed, limited by courts, or apply only in one city. The official text controls. This is not legal advice."))
        render(); return root
    }
    private fun matches(vararg f:String)=query.isEmpty()||f.any{it.lowercase().contains(query)}
    private fun render(){
        tabsHost.removeAllViews(); tabsHost.addView(ui.tabs(listOf("Funny Laws (${laws.size})","Funny Cases (${cases.size})"), if(showCases)1 else 0, { showCases = it==1; render() }), FrameLayout.LayoutParams(-1,-1))
        list.removeAllViews()
        if(showCases){
            val shown=cases.filter{matches(it.name,it.summary,it.court,it.citation)}
            count.text="${shown.size} of ${cases.size} real Georgia court cases"
            shown.forEach{c->list.addView(entry("${c.name} (${c.year})",c.summary,"${c.court} • ${c.citation}",null,c.sourceUrl))}
        } else {
            val shown=laws.filter{matches(it.title,it.summary,it.citation,it.category,it.jurisdiction)}
            count.text="${shown.size} of ${laws.size} real laws"
            var lastCat=""
            shown.forEach{l->if(l.category!=lastCat){lastCat=l.category;list.addView(ui.sectionHeader(l.category))}
                list.addView(entry(l.title,l.summary,"${l.citation} • ${l.jurisdiction}",l.status.takeIf{!it.startsWith("In the current Georgia Code")},l.sourceUrl))}
        }
        if(list.childCount==0) list.addView(ui.note("No matches. Try another word."))
    }
    private fun entry(title:String,summary:String,cite:String,status:String?,url:String)=LinearLayout(ui.context).apply{
        orientation=LinearLayout.VERTICAL;setPadding(ui.dp(14),ui.dp(12),ui.dp(14),ui.dp(12));background=ui.glowCard(glow=false)
        layoutParams=ui.lp(5,5)
        addView(ui.text(title,16f,GaUi.WHITE,ui.sansBold)); addView(ui.text(summary,14f,GaUi.TEXT).apply{setPadding(0,ui.dp(4),0,ui.dp(4))}); addView(ui.text("⚖ $cite",12.5f,GaUi.BLUE,ui.sansBold))
        if(status!=null) addView(ui.text("⚠ Status: $status",12.5f,GaUi.GOLD).apply{setPadding(0,ui.dp(4),0,0)})
        addView(ui.text("Open source ↗",12.5f,GaUi.MUTED).apply{setPadding(0,ui.dp(4),0,0)}); contentDescription="$title. $cite. Open source"
        setOnClickListener{ openSource(url) }
    }
}

class FunnyLawsActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState:Bundle?){
        super.onCreate(savedInstanceState); SystemBars.apply(this);val (laws,cases)=FunnyGeorgiaData.parse(assets.open("funny_georgia.json").bufferedReader().use{it.readText()})
        setContentView(FunnyGeorgiaScreen(GaUi(this),laws,cases,{finish()},{url->
            if(url.startsWith("https://")) runCatching{startActivity(Intent(Intent.ACTION_VIEW,Uri.parse(url)))}.onFailure{Toast.makeText(this,"No browser is available.",Toast.LENGTH_SHORT).show()}
        },intent.getBooleanExtra("cases",false)).build())
    }
}
