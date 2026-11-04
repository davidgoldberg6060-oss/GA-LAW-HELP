package help.galaw.standalone

import android.content.Context
import android.content.Intent
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.graphics.ImageDecoder
import android.graphics.Matrix
import android.media.ExifInterface
import android.net.Uri
import android.os.Build
import android.provider.OpenableColumns
import androidx.core.content.FileProvider
import org.json.JSONArray
import org.json.JSONObject
import java.io.ByteArrayOutputStream
import java.io.File

/**
 * One on-device document store shared by every screen (Documents, AI Help, cases).
 * Each document is one or more pages saved in the app's private files dir. Photos are
 * downscaled to [MAX_EDGE] px JPEG so they upload fast and the AI can read them.
 */
class DocumentLibrary(private val context: Context) {
    companion object {
        const val MAX_EDGE = 2200
        const val JPEG_QUALITY = 85
        const val MAX_PDF_BYTES = 15L * 1024 * 1024
        const val MAX_PAGES = 10
    }

    data class Page(val file: File, val mime: String)
    data class Doc(val id: String, val name: String, val mime: String, val pages: List<Page>, val addedAt: Long,
                   val caseIds: List<Int>, val summary: String) {
        val bytes: Long get() = pages.sumOf { it.file.length() }
        val isImage: Boolean get() = mime.startsWith("image/")
    }

    class DocumentException(message: String) : RuntimeException(message)

    private val dir = File(context.filesDir, "documents").apply { mkdirs() }
    private val index = File(dir, "index.json")

    @Synchronized private fun readIndex(): JSONArray = runCatching { JSONArray(index.readText()) }.getOrDefault(JSONArray())
    @Synchronized private fun writeIndex(a: JSONArray) { val tmp = File(dir, "index.tmp"); tmp.writeText(a.toString()); tmp.renameTo(index) }

    @Synchronized fun list(): List<Doc> {
        val a = readIndex(); val out = mutableListOf<Doc>()
        for (i in 0 until a.length()) {
            val o = a.optJSONObject(i) ?: continue
            val pages = o.optJSONArray("pages") ?: JSONArray()
            val pageList = (0 until pages.length()).mapNotNull { j -> pages.optJSONObject(j)?.let { Page(File(dir, it.optString("file")), it.optString("mime")) } }.filter { it.file.exists() }
            if (pageList.isEmpty()) continue
            val cases = o.optJSONArray("cases") ?: JSONArray()
            out += Doc(o.optString("id"), o.optString("name", "Document"), o.optString("mime"), pageList, o.optLong("added"),
                (0 until cases.length()).map { cases.optInt(it) }, o.optString("summary"))
        }
        return out.sortedByDescending { it.addedAt }
    }

    fun get(id: String): Doc? = list().firstOrNull { it.id == id }

    /** Copy picked/captured files into the library as ONE document (several photos = several pages). */
    fun add(uris: List<Uri>, nameHint: String? = null): Doc {
        if (uris.isEmpty()) throw DocumentException("No file was selected.")
        if (uris.size > MAX_PAGES) throw DocumentException("Please add $MAX_PAGES pages or fewer at a time.")
        val id = "d" + System.currentTimeMillis()
        val pages = JSONArray(); var mime = ""
        uris.forEachIndexed { i, uri ->
            val type = mimeOf(uri)
            val (bytes, outMime, ext) = when {
                type.startsWith("image/") -> Triple(prepareImage(uri), "image/jpeg", "jpg")
                type == "application/pdf" -> Triple(readLimited(uri, MAX_PDF_BYTES), type, "pdf")
                else -> Triple(readLimited(uri, MAX_PDF_BYTES), type.ifBlank { "application/octet-stream" }, displayName(uri).substringAfterLast('.', "bin").take(5))
            }
            if (mime.isEmpty()) mime = outMime
            val f = File(dir, "$id-$i.$ext"); f.writeBytes(bytes)
            pages.put(JSONObject().put("file", f.name).put("mime", outMime))
        }
        val first = displayName(uris[0])
        val name = nameHint ?: if (uris.size > 1) "${first.substringBeforeLast('.')} (${uris.size} pages)" else first
        val o = JSONObject().put("id", id).put("name", name).put("mime", mime).put("pages", pages).put("added", System.currentTimeMillis()).put("cases", JSONArray())
        synchronized(this) { val a = readIndex(); a.put(o); writeIndex(a) }
        return get(id)!!
    }

    @Synchronized private fun update(id: String, change: (JSONObject) -> Unit) {
        val a = readIndex(); for (i in 0 until a.length()) { val o = a.optJSONObject(i) ?: continue; if (o.optString("id") == id) change(o) }; writeIndex(a)
    }
    fun markAttached(id: String, caseId: Int) = update(id) { o -> val c = o.optJSONArray("cases") ?: JSONArray(); if ((0 until c.length()).none { c.optInt(it) == caseId }) c.put(caseId); o.put("cases", c) }
    fun saveSummary(id: String, summary: String) = update(id) { it.put("summary", summary.take(20000)) }
    fun rename(id: String, name: String) = update(id) { it.put("name", name.take(120)) }
    @Synchronized fun delete(id: String) {
        val a = readIndex(); val keep = JSONArray()
        for (i in 0 until a.length()) { val o = a.optJSONObject(i) ?: continue
            if (o.optString("id") == id) { val p = o.optJSONArray("pages") ?: JSONArray(); for (j in 0 until p.length()) File(dir, p.optJSONObject(j)?.optString("file") ?: "").delete() } else keep.put(o) }
        writeIndex(keep)
    }

    fun uriFor(page: Page): Uri = FileProvider.getUriForFile(context, context.packageName + ".drafts", page.file)

    /** Open or share a saved document with other apps (viewer, email, messages, Drive...). */
    fun shareIntent(doc: Doc): Intent {
        val uris = ArrayList(doc.pages.map { uriFor(it) })
        val i = if (uris.size == 1) Intent(Intent.ACTION_SEND).putExtra(Intent.EXTRA_STREAM, uris[0]) else Intent(Intent.ACTION_SEND_MULTIPLE).putParcelableArrayListExtra(Intent.EXTRA_STREAM, uris)
        return Intent.createChooser(i.setType(doc.mime.ifBlank { "*/*" }).addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION), "Share document")
    }
    fun viewIntent(doc: Doc): Intent = Intent(Intent.ACTION_VIEW).setDataAndType(uriFor(doc.pages[0]), doc.pages[0].mime).addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)

    /** Pages the AI can read (photos and PDFs). */
    fun readablePages(doc: Doc): List<Page> = doc.pages.filter { it.mime.startsWith("image/") || it.mime == "application/pdf" }

    fun newCameraUri(): Uri {
        val f = File(File(context.cacheDir, "camera").apply { mkdirs() }, "page-${System.currentTimeMillis()}.jpg")
        return FileProvider.getUriForFile(context, context.packageName + ".drafts", f)
    }

    fun mimeOf(uri: Uri): String {
        val t = context.contentResolver.getType(uri) ?: ""
        if (t.isNotBlank() && t != "application/octet-stream") return t
        val n = displayName(uri).lowercase()
        return when { n.endsWith(".pdf") -> "application/pdf"; n.endsWith(".jpg") || n.endsWith(".jpeg") -> "image/jpeg"; n.endsWith(".png") -> "image/png"
            n.endsWith(".heic") || n.endsWith(".heif") -> "image/heic"; n.endsWith(".webp") -> "image/webp"; else -> t }
    }

    fun displayName(uri: Uri): String {
        var name = uri.lastPathSegment?.substringAfterLast('/') ?: "document"
        runCatching { context.contentResolver.query(uri, arrayOf(OpenableColumns.DISPLAY_NAME), null, null, null)?.use { if (it.moveToFirst()) it.getString(0)?.let { n -> name = n } } }
        return name.replace(Regex("[\\r\\n\"/]"), "_")
    }

    private fun readLimited(uri: Uri, max: Long): ByteArray {
        val input = context.contentResolver.openInputStream(uri) ?: throw DocumentException("That file couldn't be opened. Try choosing it again.")
        input.use { val out = ByteArrayOutputStream(); val buf = ByteArray(64 * 1024); var total = 0L
            while (true) { val n = it.read(buf); if (n < 0) break; total += n; if (total > max) throw DocumentException("That file is larger than 15 MB. Please choose a smaller file."); out.write(buf, 0, n) }
            return out.toByteArray() }
    }

    /** Decode any phone photo (JPEG, PNG, HEIC, WEBP), fix rotation, shrink to MAX_EDGE, save as JPEG. */
    fun prepareImage(uri: Uri): ByteArray {
        val bmp: Bitmap = try {
            if (Build.VERSION.SDK_INT >= 28) {
                ImageDecoder.decodeBitmap(ImageDecoder.createSource(context.contentResolver, uri)) { d, info, _ ->
                    val w = info.size.width; val h = info.size.height; val edge = maxOf(w, h)
                    if (edge > MAX_EDGE) { val s = MAX_EDGE.toFloat() / edge; d.setTargetSize((w * s).toInt().coerceAtLeast(1), (h * s).toInt().coerceAtLeast(1)) }
                    d.allocator = ImageDecoder.ALLOCATOR_SOFTWARE
                }
            } else legacyDecode(uri)
        } catch (e: OutOfMemoryError) { throw DocumentException("That photo is too large to open. Try a lower camera resolution.")
        } catch (e: DocumentException) { throw e
        } catch (e: Exception) { throw DocumentException("That photo couldn't be read. Try taking it again or choose a JPG or PNG.") }
        val out = ByteArrayOutputStream()
        bmp.compress(Bitmap.CompressFormat.JPEG, JPEG_QUALITY, out); bmp.recycle()
        return out.toByteArray()
    }

    private fun legacyDecode(uri: Uri): Bitmap {
        val r = context.contentResolver
        val bounds = BitmapFactory.Options().apply { inJustDecodeBounds = true }
        r.openInputStream(uri)?.use { BitmapFactory.decodeStream(it, null, bounds) }
        var sample = 1; while (maxOf(bounds.outWidth, bounds.outHeight) / (sample * 2) >= MAX_EDGE) sample *= 2
        var bmp = r.openInputStream(uri)?.use { BitmapFactory.decodeStream(it, null, BitmapFactory.Options().apply { inSampleSize = sample }) }
            ?: throw DocumentException("That photo couldn't be read. Try taking it again or choose a JPG or PNG.")
        val rotation = runCatching { r.openInputStream(uri)?.use { ExifInterface(it).getAttributeInt(ExifInterface.TAG_ORIENTATION, ExifInterface.ORIENTATION_NORMAL) } }.getOrNull()
        val deg = when (rotation) { ExifInterface.ORIENTATION_ROTATE_90 -> 90f; ExifInterface.ORIENTATION_ROTATE_180 -> 180f; ExifInterface.ORIENTATION_ROTATE_270 -> 270f; else -> 0f }
        val edge = maxOf(bmp.width, bmp.height); val scale = if (edge > MAX_EDGE) MAX_EDGE.toFloat() / edge else 1f
        if (deg != 0f || scale != 1f) { val m = Matrix().apply { postScale(scale, scale); postRotate(deg) }; bmp = Bitmap.createBitmap(bmp, 0, 0, bmp.width, bmp.height, m, true) }
        return bmp
    }
}
