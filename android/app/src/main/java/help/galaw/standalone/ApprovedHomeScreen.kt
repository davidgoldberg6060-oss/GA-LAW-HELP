package help.galaw.standalone

import android.graphics.Color
import android.graphics.Typeface
import android.graphics.drawable.GradientDrawable
import android.text.SpannableString
import android.text.Spanned
import android.text.style.ForegroundColorSpan
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
    private val panel = Color.rgb(7, 28, 46)
    private val border = Color.rgb(22, 79, 120)
    private val muted = Color.rgb(175, 194, 208)
    private fun dp(v: Int) = (v * activity.resources.displayMetrics.density).toInt()

    fun build(): View {
        val shell = LinearLayout(activity).apply {
            orientation = LinearLayout.VERTICAL
            setBackgroundColor(navy)
        }
        val body = LinearLayout(activity).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(dp(12), dp(8), dp(12), dp(16))
        }

        body.addView(header())
        body.addView(heroCopy(), LinearLayout.LayoutParams(-1, -2).apply { setMargins(dp(4), dp(5), dp(4), dp(12)) })
        body.addView(searchBar(), LinearLayout.LayoutParams(-1, dp(58)).apply { setMargins(dp(3), 0, dp(3), dp(10)) })

        body.addView(gridRow(
            tile("▣", "My Cases", "Manage your cases", actions::openCases),
            tile("◉", "Talk to Me", "Get legal answers", actions::openTalkToMe),
            tile("▤", "Legal Tools", "Forms, templates & more", actions::openLegalTools)
        ))
        body.addView(gridRow(
            tile("▥", "Georgia Laws", "Statutes & rules", actions::openGeorgiaLaws),
            tile("⚖", "Court Info", "Find courts & dockets", actions::openCourtInfo),
            tile("▤", "Legal Forms", "Fill & download", actions::openLegalForms)
        ))
        body.addView(gridRow(
            tile("▦", "Case Analysis", "Get insights", actions::openCaseAnalysis),
            tile("♙", "Know Your Rights", "Learn in plain language", actions::openKnowYourRights),
            tile("◉", "Resources", "Aid, programs & more", actions::openResources)
        ))

        body.addView(emergencyBanner(), LinearLayout.LayoutParams(-1, -2).apply { setMargins(dp(3), dp(8), dp(3), dp(12)) })

        body.addView(TextView(activity).apply {
            text = "“Justice is not a privilege. It’s a right.”"
            textSize = 17f
            gravity = Gravity.CENTER
            setTextColor(Color.WHITE)
            setTypeface(Typeface.create(Typeface.SERIF, Typeface.ITALIC))
            setPadding(0, dp(8), 0, dp(3))
        })
        body.addView(TextView(activity).apply {
            text = "GA.LAW.HELP"
            textSize = 11f
            gravity = Gravity.CENTER
            setTextColor(muted)
            letterSpacing = .12f
            setPadding(0, 0, 0, dp(12))
        })

        val scroll = android.widget.ScrollView(activity).apply {
            isFillViewport = true
            setBackgroundColor(navy)
            addView(body)
        }
        shell.addView(scroll, LinearLayout.LayoutParams(-1, 0, 1f))
        shell.addView(bottomNav())
        return shell
    }

    private fun header(): View = LinearLayout(activity).apply {
        orientation = LinearLayout.HORIZONTAL
        gravity = Gravity.CENTER_VERTICAL
        setPadding(0, dp(2), 0, dp(2))

        addView(TextView(activity).apply {
            text = "☰"
            textSize = 25f
            setTextColor(blue)
            gravity = Gravity.CENTER
            contentDescription = "Open menu"
            setOnClickListener { actions.openMenu() }
        }, LinearLayout.LayoutParams(dp(42), dp(52)))

        addView(ImageView(activity).apply {
            setImageResource(R.drawable.ic_lady_justice)
            scaleType = ImageView.ScaleType.CENTER_INSIDE
            contentDescription = "Blindfolded Lady Justice holding scales"
        }, LinearLayout.LayoutParams(dp(76), dp(82)))

        val brand = LinearLayout(activity).apply {
            orientation = LinearLayout.VERTICAL
            gravity = Gravity.CENTER_VERTICAL
            addView(text("GA.LAW.HELP", 24f, true).apply {
                setTypeface(Typeface.create(Typeface.SERIF, Typeface.BOLD))
                setPadding(dp(3), 0, 0, 0)
            })
            addView(text("CLEAR ANSWERS. A STRONGER GEORGIA.", 8.5f, false).apply {
                setTextColor(Color.rgb(225, 203, 153))
                setPadding(dp(3), 0, 0, 0)
            })
        }
        addView(brand, LinearLayout.LayoutParams(0, -2, 1f))

        addView(TextView(activity).apply {
            text = "⌕"
            textSize = 28f
            setTextColor(blue)
            gravity = Gravity.CENTER
            contentDescription = "Search laws"
            setOnClickListener { actions.openGeorgiaLaws() }
        }, LinearLayout.LayoutParams(dp(42), dp(50)))

        addView(TextView(activity).apply {
            text = "◎"
            textSize = 25f
            setTextColor(blue)
            gravity = Gravity.CENTER
            contentDescription = "Account"
            setOnClickListener { actions.openAccount() }
        }, LinearLayout.LayoutParams(dp(42), dp(50)))
    }

    private fun heroCopy(): View = LinearLayout(activity).apply {
        orientation = LinearLayout.VERTICAL
        gravity = Gravity.CENTER_HORIZONTAL
        val headline = SpannableString("LEGAL ANSWERS  ANYTIME")
        val start = headline.toString().indexOf("ANYTIME")
        headline.setSpan(ForegroundColorSpan(blue), start, headline.length, Spanned.SPAN_EXCLUSIVE_EXCLUSIVE)
        addView(TextView(activity).apply {
            text = headline
            textSize = 27f
            gravity = Gravity.CENTER
            setTextColor(Color.WHITE)
            setTypeface(Typeface.create(Typeface.SERIF, Typeface.BOLD))
            setPadding(0, dp(6), 0, dp(4))
        })
        addView(text("Search Georgia law, get guidance, and take the next step with confidence.", 13f, false).apply {
            gravity = Gravity.CENTER
            setTextColor(Color.rgb(205, 216, 224))
        })
    }

    private fun searchBar(): View {
        val row = LinearLayout(activity).apply {
            orientation = LinearLayout.HORIZONTAL
            gravity = Gravity.CENTER_VERTICAL
            setPadding(dp(14), 0, dp(7), 0)
            background = rounded(Color.rgb(5, 24, 41), blue, 1, 18)
        }
        val ask = EditText(activity).apply {
            hint = "Ask a legal question..."
            setHintTextColor(Color.rgb(148, 169, 187))
            setTextColor(Color.WHITE)
            setSingleLine(true)
            textSize = 15f
            setPadding(dp(8), 0, dp(8), 0)
            background = null
            setOnEditorActionListener { _, _, _ ->
                submitQuestion(this)
                true
            }
        }
        row.addView(TextView(activity).apply {
            text = "⌕"
            textSize = 28f
            setTextColor(Color.rgb(114, 179, 236))
            gravity = Gravity.CENTER
        }, LinearLayout.LayoutParams(dp(38), -1))
        row.addView(ask, LinearLayout.LayoutParams(0, -1, 1f))
        row.addView(TextView(activity).apply {
            text = "→"
            textSize = 25f
            setTextColor(Color.WHITE)
            gravity = Gravity.CENTER
            background = rounded(Color.rgb(13, 132, 238), Color.rgb(91, 193, 255), 1, 22)
            contentDescription = "Ask GA.LAW.HELP"
            setOnClickListener { submitQuestion(ask) }
        }, LinearLayout.LayoutParams(dp(44), dp(44)))
        return row
    }

    private fun submitQuestion(input: EditText) {
        input.text.toString().trim().takeIf { it.isNotEmpty() }?.let(actions::ask)
    }

    private fun gridRow(vararg views: View) = LinearLayout(activity).apply {
        orientation = LinearLayout.HORIZONTAL
        views.forEach {
            addView(it, LinearLayout.LayoutParams(0, dp(116), 1f).apply {
                setMargins(dp(3), dp(4), dp(3), dp(4))
            })
        }
    }

    private fun tile(icon: String, title: String, subtitle: String, action: () -> Unit): View = LinearLayout(activity).apply {
        orientation = LinearLayout.VERTICAL
        gravity = Gravity.CENTER
        setPadding(dp(5), dp(8), dp(5), dp(7))
        background = rounded(panel, border, 1, 12)
        addView(text(icon, 27f, false).apply { gravity = Gravity.CENTER; setTextColor(blue) })
        addView(text(title, 12.5f, true).apply { gravity = Gravity.CENTER; setPadding(0, dp(2), 0, 0) })
        addView(text(subtitle, 9.5f, false).apply { gravity = Gravity.CENTER; setTextColor(muted); setPadding(0, dp(2), 0, 0) })
        setOnClickListener { action() }
    }

    private fun emergencyBanner(): View = LinearLayout(activity).apply {
        orientation = LinearLayout.HORIZONTAL
        gravity = Gravity.CENTER_VERTICAL
        setPadding(dp(14), dp(10), dp(10), dp(10))
        background = rounded(Color.rgb(94, 12, 20), Color.rgb(255, 65, 65), 1, 12)
        addView(TextView(activity).apply {
            text = "⚠"
            textSize = 30f
            setTextColor(Color.rgb(255, 215, 215))
            gravity = Gravity.CENTER
        }, LinearLayout.LayoutParams(dp(48), -1))
        addView(LinearLayout(activity).apply {
            orientation = LinearLayout.VERTICAL
            addView(text("EMERGENCY INFORMATION", 14f, true))
            addView(text("Get immediate help and important resources.", 10f, false).apply { setTextColor(Color.rgb(240, 204, 207)) })
        }, LinearLayout.LayoutParams(0, -2, 1f))
        addView(text("Find help now  ›", 11f, true).apply {
            gravity = Gravity.CENTER
            setPadding(dp(5), 0, 0, 0)
        })
        setOnClickListener { actions.openEmergency() }
    }

    private fun bottomNav(): View = LinearLayout(activity).apply {
        orientation = LinearLayout.HORIZONTAL
        setPadding(dp(3), dp(4), dp(3), dp(5))
        background = rounded(Color.rgb(4, 20, 35), Color.rgb(20, 64, 92), 1, 0)
        listOf(
            Triple("⌂", "Home", actions::openHome),
            Triple("⚖", "Laws", actions::openGeorgiaLaws),
            Triple("◉", "AI Help", actions::openTalkToMe),
            Triple("▤", "Documents", actions::openDocuments),
            Triple("◎", "Account", actions::openAccount)
        ).forEachIndexed { index, (icon, label, action) ->
            addView(TextView(activity).apply {
                text = "$icon\n$label"
                textSize = 10f
                gravity = Gravity.CENTER
                setTextColor(if (index == 0) blue else Color.rgb(203, 216, 228))
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
