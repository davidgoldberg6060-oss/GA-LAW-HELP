package help.galaw.standalone

import android.content.Context
import android.database.Cursor
import android.net.Uri
import android.provider.OpenableColumns
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey
import org.json.JSONArray
import org.json.JSONObject
import java.io.ByteArrayOutputStream
import java.io.DataOutputStream
import java.net.HttpURLConnection
import java.net.URL

class ApiException(val statusCode: Int, responseBody: String) : RuntimeException(
    when (statusCode) {
        401 -> "Please sign in to continue."
        403 -> "This feature requires an active GA.LAW.HELP membership."
        422 -> runCatching { JSONObject(responseBody).optString("detail") }.getOrNull().orEmpty().ifBlank { "Check the information and try again." }
        503 -> "This service is temporarily unavailable. Please try again shortly."
        else -> runCatching { JSONObject(responseBody).optString("detail") }.getOrNull().orEmpty().ifBlank { "Request failed ($statusCode)." }
    }
)

class ApiClient(private val context: Context) {
    private val masterKey = MasterKey.Builder(context).setKeyScheme(MasterKey.KeyScheme.AES256_GCM).build()
    private val prefs = EncryptedSharedPreferences.create(
        context, "secure_auth", masterKey,
        EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
        EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM,
    )

    var token: String?
        get() = prefs.getString("access_token", null)
        private set(value) { prefs.edit().putString("access_token", value).apply() }
    private var refreshToken: String?
        get() = prefs.getString("refresh_token", null)
        set(value) { prefs.edit().putString("refresh_token", value).apply() }

    private fun connection(path: String, method: String): HttpURLConnection {
        require(BuildConfig.API_BASE_URL.startsWith("https://") || BuildConfig.DEBUG) { "Production API URL must use HTTPS" }
        return (URL(BuildConfig.API_BASE_URL.trimEnd('/') + path).openConnection() as HttpURLConnection).apply {
            requestMethod = method
            connectTimeout = 15_000
            readTimeout = 60_000
            setRequestProperty("Accept", "application/json")
            token?.let { setRequestProperty("Authorization", "Bearer $it") }
        }
    }

    private fun read(c: HttpURLConnection): Pair<Int, String> {
        val code = c.responseCode
        val stream = if (code in 200..299) c.inputStream else c.errorStream
        return code to stream?.bufferedReader()?.use { it.readText() }.orEmpty()
    }

    private fun execute(path: String, method: String = "GET", body: JSONObject? = null, retry: Boolean = true): String {
        val c = connection(path, method)
        if (body != null) {
            c.doOutput = true
            c.setRequestProperty("Content-Type", "application/json")
            c.outputStream.use { it.write(body.toString().toByteArray()) }
        }
        val (code, response) = read(c)
        if (code == 401 && retry && refreshAccess()) return execute(path, method, body, false)
        if (code !in 200..299) throw ApiException(code, response)
        return response
    }

    private fun refreshAccess(): Boolean {
        val current = refreshToken ?: return false
        return try {
            val c = connection("/auth/refresh", "POST")
            c.doOutput = true
            c.setRequestProperty("Content-Type", "application/json")
            c.outputStream.use { it.write(JSONObject().put("refresh_token", current).toString().toByteArray()) }
            val (code, response) = read(c)
            if (code !in 200..299) return false
            saveTokens(JSONObject(response)); true
        } catch (_: Exception) { false }
    }

    private fun saveTokens(obj: JSONObject) {
        token = obj.getString("access_token")
        refreshToken = obj.getString("refresh_token")
    }

    fun auth(path: String, email: String, password: String): JSONObject {
        val obj = JSONObject(execute(path, "POST", JSONObject().put("email", email).put("password", password), false))
        if (obj.has("access_token") && obj.has("refresh_token")) saveTokens(obj)
        return obj
    }

    fun resendVerification(email: String): JSONObject = JSONObject(execute("/auth/resend-verification", "POST", JSONObject().put("email", email), false))
    fun verifyEmail(verificationToken: String): JSONObject = JSONObject(execute("/auth/verify-email", "POST", JSONObject().put("token", verificationToken), false))
    fun forgotPassword(email: String): JSONObject = JSONObject(execute("/auth/forgot-password", "POST", JSONObject().put("email", email), false))
    fun resetPassword(resetToken: String, newPassword: String): JSONObject = JSONObject(execute("/auth/reset-password", "POST", JSONObject().put("token", resetToken).put("new_password", newPassword), false))

    fun billingStatus(): JSONObject = JSONObject(execute("/billing/status"))
    fun createCheckout(): JSONObject = JSONObject(execute("/billing/checkout", "POST", JSONObject()))

    fun cases(): JSONArray = JSONArray(execute("/cases"))
    fun createCase(title: String, county: String, stage: String, narrative: String): JSONObject = JSONObject(execute(
        "/cases", "POST", JSONObject().put("title", title).put("county", county.ifBlank { JSONObject.NULL })
            .put("stage", stage.ifBlank { JSONObject.NULL }).put("narrative", narrative.ifBlank { JSONObject.NULL })
            .put("case_type", "criminal")
    ))
    fun timeline(caseId: Int): JSONArray = JSONArray(execute("/cases/$caseId/timeline"))
    fun evidence(caseId: Int): JSONArray = JSONArray(execute("/cases/$caseId/evidence"))
    fun caseDetail(caseId: Int): JSONObject = JSONObject(execute("/cases/$caseId"))
    fun runAnalysis(caseId: Int): JSONObject = JSONObject(execute("/cases/$caseId/analysis/run", "POST", JSONObject().put("focus", "full_case")))
    fun analysis(caseId: Int): JSONObject = JSONObject(execute("/cases/$caseId/analysis"))
    fun why(caseId: Int): JSONObject = JSONObject(execute("/cases/$caseId/why"))
    fun redTeam(caseId: Int): JSONObject = JSONObject(execute("/cases/$caseId/red-team"))
    fun secondLook(caseId: Int): JSONObject = JSONObject(execute("/cases/$caseId/second-look"))

    private fun displayName(uri: Uri): String {
        var name = uri.lastPathSegment?.substringAfterLast('/') ?: "evidence"
        val cursor: Cursor? = context.contentResolver.query(uri, arrayOf(OpenableColumns.DISPLAY_NAME), null, null, null)
        cursor?.use { if (it.moveToFirst()) name = it.getString(0) }
        return name.replace(Regex("[\\r\\n\\\"]"), "_")
    }

    private fun size(uri: Uri): Long = context.contentResolver.openAssetFileDescriptor(uri, "r")?.use { it.length } ?: -1L

    fun upload(caseId: Int, uri: Uri): JSONObject {
        val bytes = size(uri)
        return if (bytes > 8L * 1024 * 1024) resumableUpload(caseId, uri, bytes) else directUpload(caseId, uri)
    }

    private fun directUpload(caseId: Int, uri: Uri): JSONObject {
        val boundary = "GALaw${System.currentTimeMillis()}"
        val c = connection("/cases/$caseId/evidence", "POST")
        c.doOutput = true; c.setRequestProperty("Content-Type", "multipart/form-data; boundary=$boundary")
        val name = displayName(uri)
        val mediaType = context.contentResolver.getType(uri) ?: "application/octet-stream"
        DataOutputStream(c.outputStream).use { out ->
            out.writeBytes("--$boundary\r\nContent-Disposition: form-data; name=\"file\"; filename=\"$name\"\r\nContent-Type: $mediaType\r\n\r\n")
            context.contentResolver.openInputStream(uri)!!.use { it.copyTo(out, 1024 * 1024) }
            out.writeBytes("\r\n--$boundary--\r\n")
        }
        val (code, response) = read(c)
        if (code !in 200..299) throw ApiException(code, response)
        return JSONObject(response)
    }

    private fun resumableUpload(caseId: Int, uri: Uri, totalBytes: Long): JSONObject {
        val chunkSize = 8 * 1024 * 1024
        val totalChunks = ((totalBytes + chunkSize - 1) / chunkSize).toInt()
        val mediaType = context.contentResolver.getType(uri) ?: "application/octet-stream"
        val init = JSONObject(execute("/cases/$caseId/uploads/init", "POST", JSONObject()
            .put("filename", displayName(uri)).put("media_type", mediaType)
            .put("total_chunks", totalChunks).put("total_bytes", totalBytes)))
        val uploadId = init.getString("upload_id")
        context.contentResolver.openInputStream(uri)!!.use { input ->
            repeat(totalChunks) { index ->
                val buffer = ByteArrayOutputStream(chunkSize)
                val block = ByteArray(1024 * 1024)
                while (buffer.size() < chunkSize) {
                    val n = input.read(block, 0, minOf(block.size, chunkSize - buffer.size()))
                    if (n < 0) break
                    buffer.write(block, 0, n)
                }
                uploadChunk(caseId, uploadId, index, buffer.toByteArray())
            }
        }
        return JSONObject(execute("/cases/$caseId/uploads/$uploadId/complete", "POST", JSONObject()))
    }

    private fun uploadChunk(caseId: Int, uploadId: String, index: Int, bytes: ByteArray) {
        val boundary = "GAChunk${System.nanoTime()}"
        val c = connection("/cases/$caseId/uploads/$uploadId/chunks/$index", "PUT")
        c.doOutput = true; c.setRequestProperty("Content-Type", "multipart/form-data; boundary=$boundary")
        DataOutputStream(c.outputStream).use { out ->
            out.writeBytes("--$boundary\r\nContent-Disposition: form-data; name=\"file\"; filename=\"chunk-$index\"\r\nContent-Type: application/octet-stream\r\n\r\n")
            out.write(bytes); out.writeBytes("\r\n--$boundary--\r\n")
        }
        val (code, response) = read(c)
        if (code !in 200..299) throw ApiException(code, response)
    }

    fun logout() {
        val current = refreshToken
        if (current != null) runCatching { execute("/auth/logout", "POST", JSONObject().put("refresh_token", current), false) }
        prefs.edit().clear().apply()
    }

    fun caseNotes(caseId:Int): JSONArray = JSONArray(execute("/cases/$caseId/notes"))
    fun saveCaseNote(caseId:Int,title:String,content:String,language:String): JSONObject = JSONObject(execute("/cases/$caseId/notes","POST",JSONObject().put("title",title).put("content",content).put("note_type","LEGAL_RESEARCH").put("language",language)))
    fun deleteCaseNote(caseId:Int,noteId:Long): JSONObject = JSONObject(execute("/cases/$caseId/notes/$noteId","DELETE"))

    fun publicAsk(question:String): JSONObject = JSONObject(execute("/public/ask","POST",JSONObject().put("question",question)))
    fun searchAuthorities(query:String): JSONArray = JSONObject(execute("/legal/authorities/search?query="+java.net.URLEncoder.encode(query,"UTF-8"))).optJSONArray("items") ?: JSONArray()
}
