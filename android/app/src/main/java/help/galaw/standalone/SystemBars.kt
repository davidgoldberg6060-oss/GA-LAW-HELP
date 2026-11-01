package help.galaw.standalone

import android.app.Activity
import android.graphics.drawable.GradientDrawable
import android.os.Build
import android.view.View
import android.view.WindowManager
import androidx.core.graphics.Insets
import androidx.core.view.ViewCompat
import androidx.core.view.WindowCompat
import androidx.core.view.WindowInsetsCompat

/**
 * targetSdk 35 forces edge-to-edge on Android 15+, so the app must keep its own UI out of the
 * status bar, navigation bar (gesture pill or 3-button bar), display cutout and keyboard.
 * Every screen is placed inside android.R.id.content, so padding that frame once per activity
 * protects all screens, drawers and in-content overlays. The padded strips show the dark navy
 * app background with light system-bar icons.
 */
object SystemBars {
    fun apply(activity: Activity) {
        val window = activity.window
        WindowCompat.setDecorFitsSystemWindows(window, false)
        @Suppress("DEPRECATION") run {
            window.statusBarColor = android.graphics.Color.TRANSPARENT
            window.navigationBarColor = android.graphics.Color.TRANSPARENT
        }
        if (Build.VERSION.SDK_INT >= 29) { window.isNavigationBarContrastEnforced = false; window.isStatusBarContrastEnforced = false }
        if (Build.VERSION.SDK_INT >= 28) window.attributes = window.attributes.apply {
            layoutInDisplayCutoutMode = if (Build.VERSION.SDK_INT >= 30) WindowManager.LayoutParams.LAYOUT_IN_DISPLAY_CUTOUT_MODE_ALWAYS else WindowManager.LayoutParams.LAYOUT_IN_DISPLAY_CUTOUT_MODE_SHORT_EDGES
        }
        WindowCompat.getInsetsController(window, window.decorView).apply { isAppearanceLightStatusBars = false; isAppearanceLightNavigationBars = false }
        val content = activity.findViewById<View>(android.R.id.content)
        content.background = GradientDrawable(GradientDrawable.Orientation.TOP_BOTTOM, intArrayOf(GaUi.NAVY_TOP, GaUi.NAVY_DEEP))
        ViewCompat.setOnApplyWindowInsetsListener(content) { v, insets ->
            val p = padding(insets)
            v.setPadding(p.left, p.top, p.right, p.bottom)
            WindowInsetsCompat.CONSUMED
        }
        ViewCompat.requestApplyInsets(content)
    }

    /** Bars + cutout on every side; the bottom also grows to clear the keyboard when it is open. */
    fun padding(insets: WindowInsetsCompat): Insets {
        val bars = insets.getInsets(WindowInsetsCompat.Type.systemBars() or WindowInsetsCompat.Type.displayCutout())
        val ime = insets.getInsets(WindowInsetsCompat.Type.ime())
        return Insets.of(bars.left, bars.top, bars.right, maxOf(bars.bottom, ime.bottom))
    }
}
