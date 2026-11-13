package help.galaw.standalone

import org.json.JSONObject

/** Official GPDC circuit office directory. Contact information only; no ratings or win/loss records. */
object PublicDefenderOffices {
    data class ExtraOffice(val location: String, val address: String, val phone: String)
    data class Office(
        val id: String, val circuit: String, val optOut: Boolean, val optOutNote: String,
        val counties: List<String>, val defender: String?, val address: String, val phone: String,
        val fax: String, val email: String, val website: String, val hours: String,
        val additionalOffices: List<ExtraOffice>, val pageUrl: String, val juvenile: String
    )
    data class Directory(
        val checkedOn: String, val sourceUrl: String, val findToolUrl: String, val outcomeNote: String,
        val barLabel: String, val barUrl: String, val barExplainer: String, val disciplineUrl: String,
        val offices: List<Office>
    )

    fun load(json: String, language: String = "en"): Directory {
        val data = JSONObject(json)
        val spanish = language.startsWith("es")
        val bar = data.getJSONObject("bar_directory")
        val arr = data.getJSONArray("offices")
        val offices = (0 until arr.length()).map { i ->
            val o = arr.getJSONObject(i)
            val counties = o.optJSONArray("counties")
            val extras = o.optJSONArray("additional_offices")
            val juv = o.optJSONObject("juvenile")
            Office(
                o.getString("id"), o.getString("circuit"), o.optBoolean("opt_out"),
                o.optString("opt_out_note"),
                if (counties == null) emptyList() else (0 until counties.length()).map { counties.getString(it) },
                o.optString("defender").ifBlank { null },
                o.optString("address"), o.optString("phone"), o.optString("fax"),
                o.optString("email"), o.optString("website"), o.optString("hours"),
                if (extras == null) emptyList() else (0 until extras.length()).map { j ->
                    val e = extras.getJSONObject(j)
                    ExtraOffice(e.optString("location"), e.optString("address"), e.optString("phone"))
                },
                o.getString("page_url"),
                if (juv == null) "" else listOf(juv.optString("name"), juv.optString("phone")).filter { it.isNotBlank() }.joinToString(" · ")
            )
        }
        return Directory(
            data.getString("checked_on"), data.getString("source_url"), data.getString("find_tool_url"),
            if (spanish) data.getString("outcome_note_es") else data.getString("outcome_note_en"),
            if (spanish) bar.getString("label_es") else bar.getString("label_en"),
            bar.getString("url"),
            if (spanish) bar.getString("explainer_es") else bar.getString("explainer_en"),
            bar.getString("discipline_url"),
            offices
        )
    }

    fun search(dir: Directory, query: String): List<Office> {
        val q = query.trim().lowercase()
        if (q.isEmpty()) return dir.offices
        val tokens = q.split(Regex("[^a-z0-9]+")).filter { it.isNotEmpty() }
        return dir.offices.filter { office ->
            val blob = listOf(
                office.circuit, office.defender.orEmpty(), office.address, office.phone, office.email,
                office.counties.joinToString(" "), office.optOutNote, office.juvenile
            ).joinToString(" ").lowercase()
            blob.contains(q) || (tokens.isNotEmpty() && tokens.all { blob.contains(it) })
        }
    }
}
