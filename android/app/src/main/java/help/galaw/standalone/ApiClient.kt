package help.galaw.standalone

import android.app.Activity
import android.content.Context
import android.content.Intent
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
import java.net.SocketTimeoutException
import java.net.UnknownHostException
import java.net.URL

private fun apiErrorMessage(statusCode: Int, responseBody: String): String {
    if (statusCode == 401) return "Your session refreshed. Please try again."
    if (statusCode == 429) { val d = runCatching { JSONObject(responseBody).optString("detail") }.getOrNull(); return if (!d.isNullOrBlank()) d else "You've reached today's limit. Please try again tomorrow." }
    if (statusCode == 403) return "This feature is not available for this account."
    if (statusCode == 503) return "This service is temporarily unavailable. Please try again shortly."
    val detail = runCatching { JSONObject(responseBody).opt("detail") }.getOrNull()
    if (statusCode == 422 && detail is JSONArray && detail.length() > 0) {
        val first = detail.optJSONObject(0)
        val field = first?.optJSONArray("loc")?.let { loc -> if (loc.length() > 0) loc.optString(loc.length() - 1) else "" }.orEmpty()
        val msg = first?.optString("msg").orEmpty()
        return when {
            field.equals("email", true) -> "Enter a valid email address."
            field.contains("password", true) && msg.contains("15", true) -> "Password must be at least 15 characters."
            msg.isNotBlank() -> msg.replaceFirstChar { if (it.isLowerCase()) it.titlecase() else it.toString() }
            else -> "Check the information and try again."
        }
    }
    if (detail is String && detail.isNotBlank()) return detail
    return if (statusCode == 422) "Check the information and try again." else "Request failed ($statusCode)."
}
class ApiException(val statusCode: Int, responseBody: String) : RuntimeException(apiErrorMessage(statusCode, responseBody))
class ApiNetworkException(message: String, cause: Throwable? = null) : RuntimeException(message, cause)
class ApiClient(private val context: Context) {
    private val masterKey = MasterKey.Builder(context).setKeyScheme(MasterKey.KeyScheme.AES256_GCM).build()
    private val prefs = EncryptedSharedPreferences.create(context, "secure_auth", masterKey, EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV, EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM)
    var token: String? get() = prefs.getString("access_token", null); private set(value) { prefs.edit().putString("access_token", value).apply() }
    private var refreshToken: String? get() = prefs.getString("refresh_token", null); set(value) { prefs.edit().putString("refresh_token", value).apply() }
    fun clearSession() { prefs.edit().clear().apply() }
    /** True when this device is using its anonymous identity (no login screen, no email). */
    val isAnonymous: Boolean get() = token == null || prefs.getBoolean("anonymous", false)
    /** Random per-install secret kept in its own encrypted file so signing out never loses it. */
    private val devicePrefs by lazy { EncryptedSharedPreferences.create(context, "device_identity", masterKey, EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV, EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM) }
    val deviceKey: String @Synchronized get() = devicePrefs.getString("device_key", null) ?: newDeviceKey().also { devicePrefs.edit().putString("device_key", it).commit() }
    private fun newDeviceKey(): String { val b = ByteArray(32); java.security.SecureRandom().nextBytes(b); return android.util.Base64.encodeToString(b, android.util.Base64.URL_SAFE or android.util.Base64.NO_PADDING or android.util.Base64.NO_WRAP) }
    private fun rotateDeviceKey() { devicePrefs.edit().putString("device_key", newDeviceKey()).commit() }
    /** Silently get a session for this device. Safe to call from any background thread. */
    @Synchronized fun ensureSession() { if (token != null) return; anonymousSignIn() }
    private fun anonymousSignIn() { val c=connection("/auth/anonymous","POST");c.doOutput=true;c.setRequestProperty("Content-Type","application/json");c.outputStream.use{it.write(JSONObject().put("device_key",deviceKey).toString().toByteArray())};val(code,response)=read(c);if(code !in 200..299)throw ApiException(code,response);saveTokens(JSONObject(response));prefs.edit().putBoolean("anonymous",true).apply() }
    /** A session that can no longer be refreshed falls back to this device's anonymous identity; no login screen. */
    private fun expireSession() { clearSession(); runCatching { anonymousSignIn() } }
    private fun connection(path:String,method:String):HttpURLConnection { return connection(path,method,30_000) }
    private fun connection(path:String,method:String,readMs:Int):HttpURLConnection { require(BuildConfig.API_BASE_URL.startsWith("https://")||BuildConfig.DEBUG); return (URL(BuildConfig.API_BASE_URL.trimEnd('/')+path).openConnection() as HttpURLConnection).apply { requestMethod=method;connectTimeout=8_000;readTimeout=readMs;setRequestProperty("Accept","application/json");token?.let{setRequestProperty("Authorization","Bearer $it")} } }
    private fun read(c:HttpURLConnection):Pair<Int,String>{val code=c.responseCode;val stream=if(code in 200..299)c.inputStream else c.errorStream;return code to stream?.bufferedReader()?.use{it.readText()}.orEmpty()}
    private fun networkMessage(e:Exception)=when(e){is UnknownHostException->ApiNetworkException("Can’t reach GA.LAW.HELP right now. Check your internet connection, then tap Retry.",e);is SocketTimeoutException->ApiNetworkException("GA.LAW.HELP took too long to respond. Check your connection, then tap Retry.",e);else->ApiNetworkException("Couldn’t connect to GA.LAW.HELP. Check your internet connection, then tap Retry.",e)}
    private fun execute(path:String,method:String="GET",body:JSONObject?=null,retry:Boolean=true,readMs:Int=30_000):String{try{if(token==null&&!path.startsWith("/auth/"))ensureSession();val c=connection(path,method,readMs);if(body!=null){c.doOutput=true;c.setRequestProperty("Content-Type","application/json");c.outputStream.use{it.write(body.toString().toByteArray())}};val(code,response)=read(c);if(code==401&&retry&&refreshAccess())return execute(path,method,body,false);if(code==401&&!path.startsWith("/auth/")){expireSession();if(retry&&token!=null)return execute(path,method,body,false)};if(code !in 200..299)throw ApiException(code,response);return response}catch(e:ApiException){throw e}catch(e:Exception){throw networkMessage(e)}}
    private fun refreshAccess():Boolean{val current=refreshToken?:return false;return try{val c=connection("/auth/refresh","POST");c.doOutput=true;c.setRequestProperty("Content-Type","application/json");c.outputStream.use{it.write(JSONObject().put("refresh_token",current).toString().toByteArray())};val(code,response)=read(c);if(code !in 200..299)false else{saveTokens(JSONObject(response));true}}catch(_:Exception){false}}
    private fun saveTokens(obj:JSONObject){token=obj.getString("access_token");refreshToken=obj.getString("refresh_token")}
    fun auth(path:String,email:String,password:String):JSONObject{val obj=JSONObject(execute(path,"POST",JSONObject().put("email",email).put("password",password),false));if(obj.has("access_token")&&obj.has("refresh_token")){saveTokens(obj);prefs.edit().putBoolean("anonymous",false).apply()};return obj}
    fun resendVerification(email:String)=JSONObject(execute("/auth/resend-verification","POST",JSONObject().put("email",email),false));fun verifyEmail(t:String)=JSONObject(execute("/auth/verify-email","POST",JSONObject().put("token",t),false));fun forgotPassword(e:String)=JSONObject(execute("/auth/forgot-password","POST",JSONObject().put("email",e),false));fun resetPassword(t:String,p:String)=JSONObject(execute("/auth/reset-password","POST",JSONObject().put("token",t).put("new_password",p),false))
    fun me()=JSONObject(execute("/me"));fun billingStatus()=JSONObject(execute("/billing/status"));fun createCheckout(plan:String="monthly")=JSONObject(execute("/billing/checkout?plan="+java.net.URLEncoder.encode(plan,"UTF-8"),"POST",JSONObject()))
    fun cases()=JSONArray(execute("/cases"));fun createCase(title:String,county:String,stage:String,narrative:String)=JSONObject(execute("/cases","POST",JSONObject().put("title",title).put("county",county.ifBlank{JSONObject.NULL}).put("stage",stage.ifBlank{JSONObject.NULL}).put("narrative",narrative.ifBlank{JSONObject.NULL}).put("case_type","criminal")))
    fun timeline(id:Int)=JSONArray(execute("/cases/$id/timeline"));fun evidence(id:Int)=JSONArray(execute("/cases/$id/evidence"));fun caseDetail(id:Int)=JSONObject(execute("/cases/$id"));fun runAnalysis(id:Int)=JSONObject(execute("/cases/$id/analysis/run","POST",JSONObject().put("focus","full_case")));fun analysis(id:Int)=JSONObject(execute("/cases/$id/analysis"));fun why(id:Int)=JSONObject(execute("/cases/$id/why"));fun redTeam(id:Int)=JSONObject(execute("/cases/$id/red-team"));fun secondLook(id:Int)=JSONObject(execute("/cases/$id/second-look"));fun innocenceAnalysis(id:Int,f:String)=JSONObject(execute("/cases/$id/innocence-analysis","POST",JSONObject().put("additional_facts",f)))
    /** Charge Check makes two grounded model calls, so it gets a longer read timeout. */
    fun chargeCheck(situation:String, caseId:Int?)=JSONObject(execute("/charge-check","POST",JSONObject().put("situation",situation).put("case_id",caseId?:JSONObject.NULL),readMs=90_000))
    fun loopholes(topic:String)=JSONObject(execute("/loopholes/analyze","POST",JSONObject().put("topic",topic)))
    fun caseChat(id:Int, message:String, history:JSONArray)=JSONObject(execute("/cases/$id/chat","POST",JSONObject().put("message",message).put("history",history)))
    fun motionScreen(id:Int, additionalFacts:String="")=JSONObject(execute("/cases/$id/motion-screen","POST",JSONObject().put("additional_facts", additionalFacts)))
    fun internalLegalSearch(query:String,mode:String="case_analysis",limit:Int=12):JSONObject=JSONObject(execute("/internal/legal-search","POST",JSONObject().put("query",query).put("mode",mode).put("limit",limit)))
    fun groundedLegalAssistant(query:String,mode:String="case_analysis"):JSONObject=JSONObject(execute("/internal/legal-assistant","POST",JSONObject().put("query",query).put("mode",mode)))
    fun caseLookup(query:String)=internalLegalSearch(query,"case_lookup")
    fun rightsLookup(query:String)=internalLegalSearch(query,"rights")
    fun motionsLookup(query:String)=internalLegalSearch(query,"motions")
    fun caseAnalysisWithVerifiedAuthorities(facts:String)=groundedLegalAssistant(facts,"case_analysis")
    fun talkToMeAnalysis(transcript:String)=groundedLegalAssistant(transcript,"talk_to_me")
    fun rightsAnalysis(description:String)=groundedLegalAssistant(description,"rights")
    fun motionsAnalysis(facts:String)=groundedLegalAssistant(facts,"motions")
    private fun displayName(uri:Uri):String{var name=uri.lastPathSegment?.substringAfterLast('/')?:"evidence";val cursor:Cursor?=context.contentResolver.query(uri,arrayOf(OpenableColumns.DISPLAY_NAME),null,null,null);cursor?.use{if(it.moveToFirst())name=it.getString(0)};return name.replace(Regex("[\\r\\n\\\"]"),"_")}
    private fun size(uri:Uri):Long=context.contentResolver.openAssetFileDescriptor(uri,"r")?.use{it.length}?:-1L
    fun upload(caseId:Int,uri:Uri):JSONObject{val bytes=size(uri);return if(bytes>8L*1024*1024)resumableUpload(caseId,uri,bytes)else directUpload(caseId,uri)}
    private fun directUpload(caseId:Int,uri:Uri):JSONObject{val boundary="GALaw${System.currentTimeMillis()}";val c=connection("/cases/$caseId/evidence","POST");c.doOutput=true;c.setRequestProperty("Content-Type","multipart/form-data; boundary=$boundary");val name=displayName(uri);val mediaType=context.contentResolver.getType(uri)?:"application/octet-stream";DataOutputStream(c.outputStream).use{out->out.writeBytes("--$boundary\r\nContent-Disposition: form-data; name=\"file\"; filename=\"$name\"\r\nContent-Type: $mediaType\r\n\r\n");context.contentResolver.openInputStream(uri)!!.use{it.copyTo(out,1024*1024)};out.writeBytes("\r\n--$boundary--\r\n")};val(code,response)=read(c);if(code==401)expireSession();if(code !in 200..299)throw ApiException(code,response);return JSONObject(response)}
    private fun resumableUpload(caseId:Int,uri:Uri,totalBytes:Long):JSONObject{val chunkSize=8*1024*1024;val totalChunks=((totalBytes+chunkSize-1)/chunkSize).toInt();val mediaType=context.contentResolver.getType(uri)?:"application/octet-stream";val init=JSONObject(execute("/cases/$caseId/uploads/init","POST",JSONObject().put("filename",displayName(uri)).put("media_type",mediaType).put("total_chunks",totalChunks).put("total_bytes",totalBytes)));val uploadId=init.getString("upload_id");context.contentResolver.openInputStream(uri)!!.use{input->repeat(totalChunks){index->val buffer=ByteArrayOutputStream(chunkSize);val block=ByteArray(1024*1024);while(buffer.size()<chunkSize){val n=input.read(block,0,minOf(block.size,chunkSize-buffer.size()));if(n<0)break;buffer.write(block,0,n)};uploadChunk(caseId,uploadId,index,buffer.toByteArray())}};return JSONObject(execute("/cases/$caseId/uploads/$uploadId/complete","POST",JSONObject()))}
    private fun uploadChunk(caseId:Int,uploadId:String,index:Int,bytes:ByteArray){val boundary="GAChunk${System.nanoTime()}";val c=connection("/cases/$caseId/uploads/$uploadId/chunks/$index","PUT");c.doOutput=true;c.setRequestProperty("Content-Type","multipart/form-data; boundary=$boundary");DataOutputStream(c.outputStream).use{out->out.writeBytes("--$boundary\r\nContent-Disposition: form-data; name=\"file\"; filename=\"chunk-$index\"\r\nContent-Type: application/octet-stream\r\n\r\n");out.write(bytes);out.writeBytes("\r\n--$boundary--\r\n")};val(code,response)=read(c);if(code==401)expireSession();if(code !in 200..299)throw ApiException(code,response)}
    fun deleteAccount(password:String):JSONObject{val anon=isAnonymous;val r=JSONObject(execute("/me/delete","POST",JSONObject().put("password",if(anon)deviceKey else password).put("confirm","DELETE"),false));clearSession();if(anon)rotateDeviceKey();return r}
    /** Anonymous users delete their device's data with the device key; no password needed. */
    fun deleteDeviceData():JSONObject=deleteAccount("")
    fun logout(){val current=refreshToken;if(current!=null)runCatching{execute("/auth/logout","POST",JSONObject().put("refresh_token",current),false)};clearSession()}
    fun caseNotes(id:Int)=JSONArray(execute("/cases/$id/notes"));fun saveCaseNote(id:Int,title:String,content:String,language:String)=JSONObject(execute("/cases/$id/notes","POST",JSONObject().put("title",title).put("content",content).put("note_type","LEGAL_RESEARCH").put("language",language)));fun deleteCaseNote(id:Int,noteId:Long)=JSONObject(execute("/cases/$id/notes/$noteId","DELETE"))
    fun publicAsk(question:String):JSONObject {
        GuestPublicApi.encounter(BuildConfig.API_BASE_URL, question)
        val result = GuestPublicApi.rightsAssistant(BuildConfig.API_BASE_URL, question, "rights")
        val answer = GroundedLegalResult.answer(result).ifBlank { result.optString("answer") }
        result.put("answer", answer.ifBlank { "No grounded guest rights answer was returned. This is general information, not a citation of current Georgia law." })
        return result
    }
    fun searchAuthorities(query:String)=JSONObject(execute("/legal/authorities/search?query="+java.net.URLEncoder.encode(query,"UTF-8"))).optJSONArray("items")?:JSONArray()
}
