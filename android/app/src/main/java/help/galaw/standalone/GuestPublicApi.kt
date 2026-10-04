package help.galaw.standalone

import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL
import java.net.URLEncoder

/**
 * Guest-accessible Georgia rights and encounter helpers.
 * These calls do not require a session and must not send the user to login.
 */
object GuestPublicApi {
    /** Server limit for POST /public/rights-assistant `query` (backend/app/main.py). */
    const val MAX_QUERY_CHARS = 4_000

    /** Server limit for GET /public/encounter `situation` (backend/app/public_rights.py max_length). */
    const val MAX_SITUATION_CHARS = 400

    const val QUERY_TOO_LONG_MESSAGE =
        "Your question is too long for free guest help. Please shorten it to 4,000 characters or fewer and focus on the key facts."

    /** The encounter pack only needs a short situation label; trim instead of failing with HTTP 422. */
    fun encounterSituation(situation: String): String = situation.trim().take(MAX_SITUATION_CHARS)

    fun encounter(baseUrl: String, situation: String = ""): JSONObject {
        val path = "/public/encounter?situation=" + URLEncoder.encode(encounterSituation(situation), "UTF-8")
        return JSONObject(get(baseUrl, path))
    }

    fun rightsAssistant(baseUrl: String, query: String, mode: String = "rights"): JSONObject {
        require(query.trim().length <= MAX_QUERY_CHARS) { QUERY_TOO_LONG_MESSAGE }
        val body = JSONObject().put("query", query).put("mode", mode)
        return JSONObject(post(baseUrl, "/public/rights-assistant", body))
    }

    private fun open(baseUrl: String, path: String, method: String): HttpURLConnection {
        val root = baseUrl.trimEnd('/')
        return (URL(root + path).openConnection() as HttpURLConnection).apply {
            requestMethod = method
            connectTimeout = 8_000
            readTimeout = 30_000
            setRequestProperty("Accept", "application/json")
        }
    }

    private fun read(c: HttpURLConnection): Pair<Int, String> {
        val code = c.responseCode
        val stream = if (code in 200..299) c.inputStream else c.errorStream
        return code to (stream?.bufferedReader()?.use { it.readText() }.orEmpty())
    }

    private fun get(baseUrl: String, path: String): String {
        val c = open(baseUrl, path, "GET")
        val (code, response) = read(c)
        if (code !in 200..299) throw ApiException(code, response)
        return response
    }

    private fun post(baseUrl: String, path: String, body: JSONObject): String {
        val c = open(baseUrl, path, "POST")
        c.doOutput = true
        c.setRequestProperty("Content-Type", "application/json")
        c.outputStream.use { it.write(body.toString().toByteArray()) }
        val (code, response) = read(c)
        if (code !in 200..299) throw ApiException(code, response)
        return response
    }
}
