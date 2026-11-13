package help.galaw.standalone

import org.json.JSONObject

/** Georgia courtroom checklists, tailored by case type. Loaded from courtroom_prep.json. */
object CourtroomPrep {
    data class Section(val id: String, val title: String, val items: List<String>)
    data class Pack(
        val title: String, val caseType: String?, val label: String, val family: String,
        val language: String, val quick: String, val sections: List<Section>,
        val disclaimer: String, val notice: String
    )

    fun catalog(json: String): JSONObject = JSONObject(json)

    fun typeIds(json: String): List<Pair<String, String>> {
        val types = catalog(json).getJSONObject("types")
        val out = mutableListOf("" to "Any Georgia court date")
        val keys = types.keys()
        while (keys.hasNext()) {
            val id = keys.next()
            val info = types.getJSONObject(id)
            out.add(id to info.optString("label_en", id))
        }
        return out
    }

    private fun items(block: JSONObject?, section: String, language: String): List<String> {
        if (block == null || !block.has(section)) return emptyList()
        val arr = block.optJSONArray(section) ?: return emptyList()
        val key = if (language == "es") "es" else "en"
        val out = ArrayList<String>()
        val seen = HashSet<String>()
        for (i in 0 until arr.length()) {
            val obj = arr.optJSONObject(i) ?: continue
            val text = obj.optString(key).ifBlank { obj.optString("en") }.trim()
            if (text.isNotEmpty() && seen.add(text)) out.add(text)
        }
        return out
    }

    fun prepFor(json: String, caseType: String?, language: String = "en"): Pack {
        val data = catalog(json)
        val types = data.getJSONObject("types")
        val kind = caseType?.trim().orEmpty().takeIf { types.has(it) }
        val info = kind?.let { types.getJSONObject(it) }
        val spanish = language.startsWith("es")
        val label = when {
            info != null && spanish -> info.optString("label_es", info.optString("label_en"))
            info != null -> info.optString("label_en")
            spanish -> "Cualquier fecha de corte en Georgia"
            else -> "Any Georgia court date"
        }
        val quick = when {
            info != null && spanish -> info.optString("quick_es")
            info != null -> info.optString("quick_en")
            spanish -> data.optString("quick_es")
            else -> data.optString("quick_en")
        }
        val title = if (info != null) {
            if (spanish) "Preparación para la corte: $label" else "Courtroom prep: $label"
        } else if (spanish) "Preparación para la corte" else "Courtroom prep"
        val general = data.getJSONObject("general")
        val sectionArr = data.getJSONArray("sections")
        val sections = (0 until sectionArr.length()).map { i ->
            val spec = sectionArr.getJSONObject(i)
            val id = spec.getString("id")
            val seen = LinkedHashSet<String>()
            seen.addAll(items(info, id, if (spanish) "es" else "en"))
            seen.addAll(items(general, id, if (spanish) "es" else "en"))
            Section(id, if (spanish) spec.getString("title_es") else spec.getString("title_en"), seen.toList())
        }
        val notice = if (spanish) "Esto es información legal, no asesoramiento jurídico." else "This is legal information, not legal advice."
        val disclaimer = if (spanish) data.getString("disclaimer_es") else data.getString("disclaimer_en")
        return Pack(title, kind, label, info?.optString("family") ?: "general", if (spanish) "es" else "en", quick, sections, disclaimer, notice)
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
        append("\n\n").append(pack.disclaimer).append("\n").append(pack.notice).append("\n")
    }
}
