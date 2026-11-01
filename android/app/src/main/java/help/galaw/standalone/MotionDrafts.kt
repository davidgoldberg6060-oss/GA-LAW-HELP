package help.galaw.standalone

import android.app.AlarmManager
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.graphics.pdf.PdfDocument
import android.os.Build
import android.text.Layout
import android.text.StaticLayout
import android.text.TextPaint
import androidx.core.content.FileProvider
import java.io.File
import java.time.LocalDate
import java.time.ZoneId

/** Share a motion template as text or PDF. */
object MotionDrafts {
    fun shareText(ctx: Context, title: String, text: String) {
        ctx.startActivity(Intent.createChooser(Intent(Intent.ACTION_SEND).apply { type = "text/plain"; putExtra(Intent.EXTRA_SUBJECT, title); putExtra(Intent.EXTRA_TEXT, text) }, "Share draft"))
    }

    fun pdf(ctx: Context, title: String, text: String): File {
        val doc = PdfDocument()
        val paint = TextPaint().apply { textSize = 10.5f; isAntiAlias = true; typeface = android.graphics.Typeface.MONOSPACE }
        val w = 612; val h = 792; val margin = 54; val width = w - 2 * margin
        val layout = StaticLayout.Builder.obtain(text, 0, text.length, paint, width).setAlignment(Layout.Alignment.ALIGN_NORMAL).setLineSpacing(0f, 1.2f).build()
        var line = 0; var pageNo = 1
        while (line < layout.lineCount) {
            val page = doc.startPage(PdfDocument.PageInfo.Builder(w, h, pageNo).create())
            val top = layout.getLineTop(line); var end = line
            while (end < layout.lineCount && layout.getLineBottom(end) - top <= h - 2 * margin) end++
            page.canvas.save(); page.canvas.translate(margin.toFloat(), (margin - top).toFloat())
            page.canvas.clipRect(0, top, width, layout.getLineBottom(end - 1)); layout.draw(page.canvas); page.canvas.restore()
            doc.finishPage(page); line = end; pageNo++
        }
        val dir = File(ctx.cacheDir, "drafts").apply { mkdirs() }
        val f = File(dir, title.replace(Regex("[^A-Za-z0-9]+"), "_").take(60) + ".pdf")
        f.outputStream().use { doc.writeTo(it) }; doc.close()
        return f
    }

    fun sharePdf(ctx: Context, title: String, text: String) {
        val uri = FileProvider.getUriForFile(ctx, ctx.packageName + ".drafts", pdf(ctx, title, text))
        ctx.startActivity(Intent.createChooser(Intent(Intent.ACTION_SEND).apply { type = "application/pdf"; putExtra(Intent.EXTRA_STREAM, uri); addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION) }, "Share PDF"))
    }
}

/** Local deadline reminders: 7 days before, 1 day before and on the day, at 9:00 AM. */
object DeadlineReminders {
    const val CHANNEL = "deadlines"
    fun schedule(ctx: Context, title: String, dueIso: String): Int {
        val due = runCatching { LocalDate.parse(dueIso.take(10)) }.getOrNull() ?: return 0
        val am = ctx.getSystemService(AlarmManager::class.java) ?: return 0
        var n = 0
        for (before in listOf(7L, 1L, 0L)) {
            val at = due.minusDays(before).atTime(9, 0).atZone(ZoneId.systemDefault()).toInstant().toEpochMilli()
            if (at <= System.currentTimeMillis()) continue
            val msg = when (before) { 0L -> "Deadline today: $title"; 1L -> "Deadline tomorrow: $title"; else -> "Deadline in 7 days ($dueIso): $title" }
            val pi = PendingIntent.getBroadcast(ctx, (title + dueIso + before).hashCode(), Intent(ctx, DeadlineReminderReceiver::class.java).putExtra("msg", msg),
                PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE)
            am.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, at, pi); n++
        }
        return n
    }
}

class DeadlineReminderReceiver : BroadcastReceiver() {
    override fun onReceive(ctx: Context, intent: Intent) {
        val nm = ctx.getSystemService(NotificationManager::class.java) ?: return
        if (Build.VERSION.SDK_INT >= 26) nm.createNotificationChannel(NotificationChannel(DeadlineReminders.CHANNEL, "Case deadlines", NotificationManager.IMPORTANCE_HIGH))
        val open = PendingIntent.getActivity(ctx, 0, Intent(ctx, HomeActivity::class.java), PendingIntent.FLAG_IMMUTABLE)
        val n = android.app.Notification.Builder(ctx, DeadlineReminders.CHANNEL).setSmallIcon(android.R.drawable.ic_dialog_info)
            .setContentTitle("GA.LAW.HELP deadline reminder").setContentText(intent.getStringExtra("msg") ?: "A case deadline is coming up.")
            .setStyle(android.app.Notification.BigTextStyle().bigText((intent.getStringExtra("msg") ?: "") + "\nConfirm the exact deadline with a lawyer."))
            .setContentIntent(open).setAutoCancel(true).build()
        runCatching { nm.notify((intent.getStringExtra("msg") ?: "").hashCode(), n) }
    }
}
