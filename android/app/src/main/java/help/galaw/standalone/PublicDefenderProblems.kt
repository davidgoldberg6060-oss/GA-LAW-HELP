package help.galaw.standalone

import org.json.JSONObject

/** Georgia guide when a user has a problem with a public defender or appointed lawyer. */
object PublicDefenderProblems {
    const val HEADING = "Problem with my public defender?"
    data class Section(val id: String, val title: String, val items: List<String>)
    data class Template(val id: String, val kind: String, val motionKey: String, val title: String, val body: String)
    data class Link(val id: String, val label: String, val url: String)
    data class Pack(
        val title: String, val hint: String, val language: String, val quick: String,
        val sections: List<Section>, val templates: List<Template>, val links: List<Link>,
        val motionKey: String, val disclaimer: String, val notice: String
    )

    private val COUNSEL = Regex("public defender|court[- ]appointed|appointed (counsel|lawyer|attorney)|defensor p[uú]blico|abogado asignado|(my|mi) (lawyer|attorney|counsel|abogado)", RegexOption.IGNORE_CASE)
    private val DISTRUST = Regex("work(?:ing|s)? (with|for|against)|working against|with the (state|da|prosecutor)|against me|not (helping|working for) me|won'?t (call|meet|visit|review)|never (call|called|meet|met|visit|review)|pressur(?:e|ing|ed).{0,40}plea|conflict of interest|co-?defendant|fire (my|the) (lawyer|attorney|public defender)|get (a |me )?(new|different|another) (lawyer|attorney|public defender)|ineffective|working with the state|defensor p[uú]blico", RegexOption.IGNORE_CASE)
    private val REQUEST_ONLY = Regex("how do i (get|ask for|request)|qualify for|apply for", RegexOption.IGNORE_CASE)

    fun detects(text: String): Boolean {
        val q = text.trim()
        if (q.isEmpty() || (REQUEST_ONLY.containsMatchIn(q) && !DISTRUST.containsMatchIn(q))) return false
        return COUNSEL.containsMatchIn(q) && (DISTRUST.containsMatchIn(q) || Regex("state|prosecutor|prosecution|\\bda\\b|against", RegexOption.IGNORE_CASE).containsMatchIn(q))
    }

    fun packFor(json: String, language: String = "en"): Pack {
        val data = JSONObject(json)
        val spanish = language.startsWith("es")
        fun pick(obj: org.json.JSONObject, en: String, es: String) = if (spanish) obj.optString(es).ifBlank { obj.optString(en) } else obj.optString(en)
        val sectionsArr = data.getJSONArray("sections")
        val sections = (0 until sectionsArr.length()).map { i ->
            val spec = sectionsArr.getJSONObject(i)
            val itemsArr = spec.getJSONArray("items")
            val items = (0 until itemsArr.length()).mapNotNull { j ->
                val item = itemsArr.getJSONObject(j)
                pick(item, "en", "es").trim().ifBlank { null }
            }
            Section(spec.getString("id"), pick(spec, "title_en", "title_es"), items)
        }
        val tmplArr = data.getJSONArray("templates")
        val templates = (0 until tmplArr.length()).map { i ->
            val row = tmplArr.getJSONObject(i)
            Template(row.getString("id"), row.optString("kind"), row.optString("motion_key"), pick(row, "title_en", "title_es"), pick(row, "body_en", "body_es"))
        }
        val linkArr = data.getJSONArray("links")
        val links = (0 until linkArr.length()).map { i ->
            val row = linkArr.getJSONObject(i)
            Link(row.getString("id"), pick(row, "label_en", "label_es"), row.getString("url"))
        }
        val notice = if (spanish) "Esto es información legal, no asesoramiento jurídico." else "This is legal information, not legal advice."
        return Pack(pick(data, "title_en", "title_es"), pick(data, "hint_en", "hint_es"), if (spanish) "es" else "en",
            pick(data, "quick_en", "quick_es"), sections, templates, links, "discharge_appointed_counsel",
            pick(data, "disclaimer_en", "disclaimer_es"), notice)
    }

    fun asText(pack: Pack): String = buildString {
        append(pack.title).append("\n\n")
        append(if (pack.language == "es") "Respuesta rápida" else "Quick answer").append("\n")
        append(pack.quick)
        pack.sections.forEach { s ->
            if (s.items.isNotEmpty()) {
                append("\n\n").append(s.title)
                s.items.forEach { append("\n• ").append(it) }
            }
        }
        pack.templates.forEach { tmpl ->
            append("\n\n").append(tmpl.title).append("\n").append(tmpl.body)
        }
        append("\n\n").append(pack.disclaimer).append("\n").append(pack.notice).append("\n")
    }
}
