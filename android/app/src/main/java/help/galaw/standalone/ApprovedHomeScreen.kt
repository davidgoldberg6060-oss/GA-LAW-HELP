package help.galaw.standalone

import android.graphics.Color
import android.graphics.Typeface
import android.graphics.drawable.GradientDrawable
import android.view.Gravity
import android.view.View
import android.widget.EditText
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity

/** Home screen matching the owner-approved GA.LAW.HELP reference layout. */
class ApprovedHomeScreen(
    private val activity: AppCompatActivity,
    private val actions: Actions
) {
    interface Actions {
        fun openMenu()
        fun openAccount()
        fun ask(question: String)
        fun openCases()
        fun openTalkToMe()
        fun openLegalTools()
        fun openGeorgiaLaws()
        fun openCourtInfo()
        fun openLegalForms()
        fun openCaseAnalysis()
        fun openKnowYourRights()
        fun openResources()
        fun openEmergency()
        fun openHome()
        fun openDocuments()
    }

    private val blue = Color.rgb(37, 168, 255)
    private val navy = Color.rgb(3, 17, 30)
    private val panel = Color.rgb(8, 31, 49)
    private val border = Color.rgb(31, 75, 105)
    private fun dp(v: Int) = (v * activity.resources.displayMetrics.density).toInt()

    fun build(): View {
        val shell = LinearLayout(activity).apply {
            orientation = LinearLayout.VERTICAL
            setBackgroundColor(navy)
        }
        val body = LinearLayout(activity).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(dp(14), dp(12), dp(14), dp(18))
        }
        body.addView(header())
        body.addView(hero(), LinearLayout.LayoutParams(-1, -2).apply { setMargins(0, dp(8), 0, dp(14)) })

        val ask = EditText(activity).apply {
            hint = "Ask GA.LAW.HELP anything..."
            setHintTextColor(Color.rgb(151, 173, 190))
            setTextColor(Color.WHITE)
            setSingleLine(true)
            setPadding(dp(18), dp(12), dp(18), dp(12))
            background = rounded(panel, blue, 1, 28)
            setOnEditorActionListener { _, _, _ ->
                text.toString().trim().takeIf { it.isNotEmpty() }?.let(actions::ask)
                true
            }
        }
        body.addView(ask)

        body.addView(quickRow(
            tile("▣", "My Cases", actions::openCases),
            tile("◉", "Talk to Me", actions::openTalkToMe),
            tile("⚖", "Legal Tools", actions::openLegalTools)
        ))
        body.addView(gridRow(
            tile("⚖", "Georgia Laws", actions::openGeorgiaLaws),
            tile("▥", "Court Info", actions::openCourtInfo),
            tile("▤", "Legal Forms", actions::openLegalForms)
        ))
        body.addView(gridRow(
            tile("▦", "Case Analysis", actions::openCaseAnalysis),
            tile("🛡", "Know Your Rights", actions::openKnowYourRights),
            tile("☷", "Resources", actions::openResources)
        ))

        body.addView(TextView(activity).apply {
            text = "⚠   EMERGENCY INFORMATION"
            textSize = 15f
            setTextColor(Color.WHITE)
            setTypeface(typeface, Typeface.BOLD)
            gravity = Gravity.CENTER_VERTICAL
            setPadding(dp(16), dp(14), dp(16), dp(14))
            background = rounded(Color.rgb(79, 18, 26), Color.rgb(239, 64, 75), 2, 16)
            setOnClickListener { actions.openEmergency() }
        }, LinearLayout.LayoutParams(-1, -2).apply { setMargins(0, dp(12), 0, dp(14)) })

        body.addView(TextView(activity).apply {
            text = "“Knowledge is power, especially when you need it most.”\n\n—  GA.LAW.HELP  —"
            textSize = 14f
            gravity = Gravity.CENTER
            setTextColor(Color.rgb(170, 190, 203))
            setTypeface(typeface, Typeface.ITALIC)
            setPadding(0, dp(8), 0, dp(14))
        })

        val scroll = android.widget.ScrollView(activity).apply { addView(body) }
        shell.addView(scroll, LinearLayout.LayoutParams(-1, 0, 1f))
        shell.addView(bottomNav())
        return shell
    }

    private fun header(): View = LinearLayout(activity).apply {
        orientation = LinearLayout.HORIZONTAL
        gravity = Gravity.CENTER_VERTICAL
        val menu = TextView(activity).apply {
            text = "☰"
            textSize = 25f
            setTextColor(Color.WHITE)
            gravity = Gravity.CENTER
            contentDescription = "Open menu"
            setOnClickListener { actions.openMenu() }
        }
        addView(menu, LinearLayout.LayoutParams(dp(44), dp(44)))
        val brand = LinearLayout(activity).apply {
            orientation = LinearLayout.VERTICAL
            addView(text("GA.LAW.HELP", 20f, true))
            addView(text("KNOW YOUR RIGHTS. PROTECT YOUR FUTURE.", 9f, false).apply { setTextColor(blue) })
        }
        addView(brand, LinearLayout.LayoutParams(0, -2, 1f))
        addView(TextView(activity).apply {
            text = "●"
            textSize = 24f
            setTextColor(Color.WHITE)
            gravity = Gravity.CENTER
            contentDescription = "Account"
            setOnClickListener { actions.openAccount() }
        }, LinearLayout.LayoutParams(dp(44), dp(44)))
    }

    private fun hero(): View = LinearLayout(activity).apply {
        orientation = LinearLayout.HORIZONTAL
        gravity = Gravity.CENTER_VERTICAL
        setPadding(dp(18), dp(18), dp(12), dp(18))
        background = rounded(Color.rgb(6, 27, 44), Color.rgb(31, 102, 148), 1, 18)
        val copy = LinearLayout(activity).apply {
            orientation = LinearLayout.VERTICAL
            addView(text("GEORGIA LAWS. REAL HELP. REAL PEOPLE.", 10f, false).apply { setTextColor(Color.rgb(152, 173, 187)) })
            addView(text("LEGAL ANSWERS\nANYTIME.", 29f, true))
            addView(text("Understand your rights. Get guidance. Stay informed. Be prepared.", 12f, false).apply { setTextColor(Color.rgb(190, 205, 215)) })
        }
        addView(copy, LinearLayout.LayoutParams(0, -2, 1f))
        addView(ImageView(activity).apply {
            setImageResource(R.drawable.ic_lady_justice)
            scaleType = ImageView.ScaleType.CENTER_INSIDE
            contentDescription = "Blindfolded Lady Justice holding scales"
        }, LinearLayout.LayoutParams(dp(120), dp(145)))
    }

    private fun quickRow(vararg views: View) = gridRow(*views)
    private fun gridRow(vararg views: View) = LinearLayout(activity).apply {
        orientation = LinearLayout.HORIZONTAL
        views.forEach { addView(it, LinearLayout.LayoutParams(0, dp(92), 1f).apply { setMargins(dp(4), dp(5), dp(4), dp(5)) }) }
    }

    private fun tile(icon: String, title: String, action: () -> Unit): View = LinearLayout(activity).apply {
        orientation = LinearLayout.VERTICAL
        gravity = Gravity.CENTER
        setPadding(dp(7), dp(8), dp(7), dp(8))
        background = rounded(panel, border, 1, 15)
        addView(text(icon, 24f, false).apply { gravity = Gravity.CENTER; setTextColor(blue) })
        addView(text(title, 12f, true).apply { gravity = Gravity.CENTER })
        setOnClickListener { action() }
    }

    private fun bottomNav(): View = LinearLayout(activity).apply {
        orientation = LinearLayout.HORIZONTAL
        setPadding(dp(3), dp(4), dp(3), dp(5))
        background = rounded(Color.rgb(6, 27, 44), Color.rgb(24, 66, 94), 1, 0)
        listOf(
            Triple("⌂", "Home", actions::openHome),
            Triple("⚖", "Laws", actions::openGeorgiaLaws),
            Triple("💬", "AI Help", actions::openTalkToMe),
            Triple("📁", "Documents", actions::openDocuments),
            Triple("●", "Account", actions::openAccount)
        ).forEach { (icon, label, action) ->
            addView(TextView(activity).apply {
                text = "$icon\n$label"
                textSize = 10f
                gravity = Gravity.CENTER
                setTextColor(Color.WHITE)
                setPadding(dp(2), dp(6), dp(2), dp(6))
                setOnClickListener { action() }
            }, LinearLayout.LayoutParams(0, -2, 1f))
        }
    }

    private fun text(value: String, size: Float, bold: Boolean) = TextView(activity).apply {
        text = value
        textSize = size
        setTextColor(Color.WHITE)
        if (bold) setTypeface(typeface, Typeface.BOLD)
    }

    private fun rounded(fill: Int, stroke: Int, strokeWidth: Int, radius: Int) = GradientDrawable().apply {
        setColor(fill)
        cornerRadius = dp(radius).toFloat()
        if (strokeWidth > 0) setStroke(dp(strokeWidth), stroke)
    }
}
