package help.galaw.standalone

import android.animation.ObjectAnimator
import android.os.Handler
import android.os.Looper
import android.view.View
import android.widget.TextView

/**
 * Short rotating loading lines that cycle every ~2s with a subtle fade.
 * Messages are light flavor for the screen the user is on; they do not claim
 * secret work the app is not doing.
 */
object LoadingLines {
    val AI_HELP = listOf(
        "Checking the Georgia Code…",
        "Pulling up case law…",
        "Lining up your options…",
        "Weighing what comes next…",
        "Putting it in plain words…",
        "Almost ready…"
    )
    val DOCUMENT_READ = listOf(
        "Reading your paper line by line…",
        "Spotting dates and charges…",
        "Finding deadlines…",
        "Lining up next steps…",
        "Almost ready…"
    )
    val DOCUMENTS = listOf(
        "Gathering your files…",
        "Checking what’s on this phone…",
        "Lining up your documents…",
        "Almost ready…"
    )
    val CASES = listOf(
        "Opening your case files…",
        "Pulling up your cases…",
        "Almost ready…"
    )
    val LAWS = listOf(
        "Searching Georgia law…",
        "Opening the stored text…",
        "Almost ready…"
    )
    val CHARGE = listOf(
        "Checking likely Georgia charges…",
        "Looking at defenses and next steps…",
        "Almost ready…"
    )
    val CIVIL = listOf(
        "Checking civil claims and deadlines…",
        "Looking at court paths…",
        "Almost ready…"
    )
    val LOOPHOLES = listOf(
        "Comparing verified Georgia laws…",
        "Looking for gaps and exceptions…",
        "Almost ready…"
    )
    val CASE_WORK = listOf(
        "Working through your case…",
        "Checking verified authorities…",
        "Almost ready…"
    )
    val GENERIC = listOf(
        "One moment…",
        "Working on that…",
        "Almost ready…"
    )
    val ACCOUNT = listOf(
        "Opening your account…",
        "Almost ready…"
    )
    val TIMELINE = listOf(
        "Lining up your timeline…",
        "Almost ready…"
    )

    /** Cycle [lines] on [view] every [intervalMs], fading out/in. Returns a stop function. */
    fun rotate(view: TextView, lines: List<String>, intervalMs: Long = 2000L, contentPrefix: String = "Loading"): () -> Unit {
        if (lines.isEmpty()) return {}
        view.text = lines[0]
        view.contentDescription = "$contentPrefix. ${lines[0]}"
        if (lines.size == 1) return {}
        val handler = Handler(Looper.getMainLooper())
        var i = 0
        var running = true
        val tick = object : Runnable {
            override fun run() {
                if (!running || !view.isAttachedToWindow) return
                i = (i + 1) % lines.size
                ObjectAnimator.ofFloat(view, View.ALPHA, 1f, 0.15f).apply {
                    duration = 180
                    start()
                }
                view.postDelayed({
                    if (!running) return@postDelayed
                    view.text = lines[i]
                    view.contentDescription = "$contentPrefix. ${lines[i]}"
                    ObjectAnimator.ofFloat(view, View.ALPHA, 0.15f, 1f).apply {
                        duration = 220
                        start()
                    }
                    handler.postDelayed(this, intervalMs)
                }, 180)
            }
        }
        handler.postDelayed(tick, intervalMs)
        return {
            running = false
            handler.removeCallbacksAndMessages(null)
            view.alpha = 1f
        }
    }

    /** Attach a rotating line to a TextView that already shows a fixed loading message. */
    fun attach(view: TextView, lines: List<String>, contentPrefix: String = "Loading"): () -> Unit =
        rotate(view, lines, contentPrefix = contentPrefix)
}
