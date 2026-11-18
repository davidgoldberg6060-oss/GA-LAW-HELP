package help.galaw.standalone

import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.os.Build

/** Simple on-device notifications (deadlines already handled by DeadlineReminderReceiver). */
object AppNotifications {
    const val CHANNEL = "galaw_general"
    private const val CHANNEL_NAME = "GA Law Help"

    fun ensureChannel(ctx: Context) {
        if (Build.VERSION.SDK_INT < 26) return
        val nm = ctx.getSystemService(NotificationManager::class.java) ?: return
        if (nm.getNotificationChannel(CHANNEL) != null) return
        nm.createNotificationChannel(
            NotificationChannel(CHANNEL, CHANNEL_NAME, NotificationManager.IMPORTANCE_DEFAULT).apply {
                description = "Answers ready, case updates, and reminders"
            }
        )
    }

    fun post(ctx: Context, title: String, body: String, id: Int = title.hashCode()) {
        ensureChannel(ctx)
        val nm = ctx.getSystemService(NotificationManager::class.java) ?: return
        val open = PendingIntent.getActivity(
            ctx, 0, Intent(ctx, HomeActivity::class.java),
            PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT
        )
        val n = if (Build.VERSION.SDK_INT >= 26) {
            android.app.Notification.Builder(ctx, CHANNEL)
        } else {
            @Suppress("DEPRECATION")
            android.app.Notification.Builder(ctx)
        }
            .setSmallIcon(android.R.drawable.ic_dialog_info)
            .setContentTitle(title)
            .setContentText(body)
            .setStyle(android.app.Notification.BigTextStyle().bigText(body))
            .setContentIntent(open)
            .setAutoCancel(true)
            .build()
        runCatching { nm.notify(id, n) }
    }
}
