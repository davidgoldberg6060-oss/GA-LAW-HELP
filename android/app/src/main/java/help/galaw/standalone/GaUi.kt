package help.galaw.standalone

import android.content.Context
import android.content.res.ColorStateList
import android.graphics.Color
import android.graphics.Typeface
import android.graphics.drawable.Drawable
import android.graphics.drawable.GradientDrawable
import android.graphics.drawable.LayerDrawable
import android.text.SpannableStringBuilder
import android.text.Spanned
import android.text.style.ForegroundColorSpan
import android.util.TypedValue
import android.view.Gravity
import android.view.View
import android.view.ViewGroup
import android.widget.EditText
import android.widget.FrameLayout
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView
import androidx.core.content.res.ResourcesCompat

/**
 * GA.LAW.HELP design system: dark navy background, glowing blue outlined cards, Cinzel serif
 * wordmark/headlines, gold tagline, original Lady Justice art and the five-tab bottom nav.
 * Everything here builds plain Android Views from a Context so screens can be rendered in
 * activities and in screenshot tests alike.
 */
class GaUi(val context: Context) {
    companion object {
        val NAVY_TOP = Color.rgb(9, 24, 43)
        val NAVY = Color.rgb(5, 15, 28)
        val NAVY_DEEP = Color.rgb(3, 10, 20)
        val CARD = Color.argb(235, 10, 26, 45)
        val CARD_SOLID = Color.rgb(10, 26, 45)
        val BLUE = Color.rgb(47, 155, 255)
        val BLUE_BRIGHT = Color.rgb(77, 171, 255)
        val BLUE_DEEP = Color.rgb(17, 101, 230)
        val STROKE = Color.rgb(36, 117, 214)
        val STROKE_SOFT = Color.rgb(28, 70, 118)
        val GOLD = Color.rgb(230, 190, 92)
        val WHITE = Color.WHITE
        val TEXT = Color.rgb(226, 234, 243)
        val MUTED = Color.rgb(160, 180, 201)
        val RED = Color.rgb(226, 52, 58)
        val RED_DEEP = Color.rgb(120, 14, 22)
        val GREEN = Color.rgb(46, 196, 110)
        fun withAlphaStatic(color: Int, alpha: Int) = Color.argb(alpha, Color.red(color), Color.green(color), Color.blue(color))
    }

    data class NavItem(val key: String, val label: String, val icon: Int, val action: () -> Unit)

    val density = context.resources.displayMetrics.density
    /** The mockups are drawn on a ~360dp-wide phone; scale with the real width (bounded) so proportions hold. */
    val k: Float = ((context.resources.displayMetrics.widthPixels / density) / 360f).coerceIn(0.9f, 1.12f)
    fun dp(v: Int) = (v * density * k).toInt()
    fun dpf(v: Float) = v * density * k

    /** Mockup units: the approved mockups are 1024 px wide, so 1 unit = screenWidth / 1024. */
    val screenW = context.resources.displayMetrics.widthPixels.toFloat().coerceAtLeast(1f)
    fun uf(v: Float) = v * screenW / 1024f
    fun u(v: Number) = Math.round(uf(v.toFloat()))

    /**
     * Single-line text sized and positioned so its ink box lands exactly on the mockup box
     * (x0,y0)-(x1,…) given in mockup units relative to (originX, originY) of the parent frame.
     */
    fun placeText(parent: FrameLayout, value: String, face: Typeface, color: Int, x0: Int, y0: Int, x1: Int, originX: Int = 0, originY: Int = 0): TextView {
        val paint = android.text.TextPaint(android.graphics.Paint.ANTI_ALIAS_FLAG).apply { typeface = face; textSize = 100f }
        val b = android.graphics.Rect(); paint.getTextBounds(value, 0, value.length, b)
        paint.textSize = 100f * uf((x1 - x0).toFloat()) / b.width().coerceAtLeast(1)
        paint.getTextBounds(value, 0, value.length, b)
        val fm = paint.fontMetrics
        val tv = TextView(context).apply {
            text = value; typeface = face; setTextColor(color); setTextSize(TypedValue.COMPLEX_UNIT_PX, paint.textSize)
            includeFontPadding = false; setPadding(0, 0, 0, 0); maxLines = 1; isSingleLine = true
        }
        parent.addView(tv, FrameLayout.LayoutParams(-2, -2).apply {
            leftMargin = Math.round(uf((x0 - originX).toFloat()) - b.left)
            topMargin = Math.round(uf((y0 - originY).toFloat()) - (b.top - fm.ascent))
        })
        return tv
    }

    /** All-caps tracking text: height from the mockup box (y0..y1), letter spacing fitted to its width. */
    fun placeSpaced(parent: FrameLayout, value: String, face: Typeface, color: Int, x0: Int, y0: Int, x1: Int, y1: Int, originY: Int = 0): TextView {
        val paint = android.text.TextPaint(android.graphics.Paint.ANTI_ALIAS_FLAG).apply { typeface = face; textSize = 100f }
        val b = android.graphics.Rect(); paint.getTextBounds(value, 0, value.length, b)
        paint.textSize = 100f * uf((y1 - y0).toFloat()) / b.height().coerceAtLeast(1)
        val target = uf((x1 - x0).toFloat())
        repeat(3) {
            paint.getTextBounds(value, 0, value.length, b)
            paint.letterSpacing += (target - b.width()) / (paint.textSize * (value.length - 1).coerceAtLeast(1))
        }
        paint.getTextBounds(value, 0, value.length, b)
        val fm = paint.fontMetrics
        val tv = TextView(context).apply {
            text = value; typeface = face; setTextColor(color); setTextSize(TypedValue.COMPLEX_UNIT_PX, paint.textSize); letterSpacing = paint.letterSpacing
            includeFontPadding = false; setPadding(0, 0, 0, 0); maxLines = 1; isSingleLine = true
        }
        parent.addView(tv, FrameLayout.LayoutParams(-2, -2).apply {
            leftMargin = Math.round(uf(x0.toFloat()) - b.left)
            topMargin = Math.round(uf((y0 - originY).toFloat()) - (b.top - fm.ascent))
        })
        return tv
    }

    /** Transparent touch target with a ripple, placed at a mockup-unit box. */
    fun hit(parent: FrameLayout, x0: Int, y0: Int, x1: Int, y1: Int, label: String, radius: Int = 12, originY: Int = 0, action: () -> Unit): View = View(context).apply {
        contentDescription = label; isClickable = true; isFocusable = true; setOnClickListener { action() }
        background = android.graphics.drawable.RippleDrawable(ColorStateList.valueOf(withAlpha(BLUE, 70)), null, rounded(Color.WHITE, radius))
        parent.addView(this, FrameLayout.LayoutParams(u(x1 - x0), u(y1 - y0)).apply { leftMargin = u(x0); topMargin = u(y0 - originY) })
    }

    /** Full-width artwork strip cropped from the mockup, height in mockup units. */
    fun artStrip(res: Int, heightUnits: Int, description: String? = null): FrameLayout = FrameLayout(context).apply {
        addView(ImageView(context).apply {
            setImageResource(res); scaleType = ImageView.ScaleType.FIT_XY
            if (description != null) contentDescription = description else importantForAccessibility = View.IMPORTANT_FOR_ACCESSIBILITY_NO
        }, FrameLayout.LayoutParams(-1, -1))
        layoutParams = LinearLayout.LayoutParams(-1, u(heightUnits))
    }

    val serifBold: Typeface by lazy { runCatching { ResourcesCompat.getFont(context, R.font.cinzel_bold) }.getOrNull() ?: Typeface.create(Typeface.SERIF, Typeface.BOLD) }
    val serifMedium: Typeface by lazy { runCatching { ResourcesCompat.getFont(context, R.font.cinzel_medium) }.getOrNull() ?: Typeface.SERIF }
    val sansBold: Typeface = Typeface.create("sans-serif", Typeface.BOLD)
    val sansMedium: Typeface = Typeface.create("sans-serif-medium", Typeface.NORMAL)

    // ---------- drawables ----------
    fun screenBackground(): Drawable = GradientDrawable(GradientDrawable.Orientation.TOP_BOTTOM, intArrayOf(NAVY_TOP, NAVY, NAVY_DEEP))

    fun rounded(fill: Int, radius: Int, stroke: Int = 0, strokeWidth: Float = 0f): GradientDrawable = GradientDrawable().apply {
        setColor(fill); cornerRadius = dpf(radius.toFloat()); if (strokeWidth > 0f) setStroke(dpf(strokeWidth).toInt().coerceAtLeast(1), stroke)
    }

    /** Glowing outlined card: soft outer halo layers plus a crisp blue border. */
    fun glowCard(fill: Int = CARD, stroke: Int = STROKE, radius: Int = 12, glow: Boolean = true): Drawable {
        if (!glow) return rounded(fill, radius, stroke, 1.2f)
        val halo1 = rounded(Color.TRANSPARENT, radius + 3, withAlpha(stroke, 26), 3f)
        val halo2 = rounded(Color.TRANSPARENT, radius + 2, withAlpha(stroke, 60), 2f)
        val body = rounded(fill, radius, stroke, 1.3f)
        return LayerDrawable(arrayOf(halo1, halo2, body)).apply {
            setLayerInset(1, dp(1), dp(1), dp(1), dp(1))
            setLayerInset(2, dp(3), dp(3), dp(3), dp(3))
        }
    }

    fun primaryButtonBg(radius: Int = 12): Drawable {
        val halo = rounded(Color.TRANSPARENT, radius + 3, withAlpha(BLUE, 70), 3f)
        val body = GradientDrawable(GradientDrawable.Orientation.TOP_BOTTOM, intArrayOf(Color.rgb(38, 132, 255), Color.rgb(13, 86, 214))).apply {
            cornerRadius = dpf(radius.toFloat()); setStroke(dp(1), Color.rgb(110, 185, 255))
        }
        return LayerDrawable(arrayOf(halo, body)).apply { setLayerInset(1, dp(3), dp(3), dp(3), dp(3)) }
    }

    fun withAlpha(color: Int, alpha: Int) = Color.argb(alpha, Color.red(color), Color.green(color), Color.blue(color))

    // ---------- text ----------
    fun text(value: CharSequence, size: Float, color: Int = TEXT, face: Typeface? = null, gravity: Int = Gravity.START): TextView = TextView(context).apply {
        text = value; textSize = size * k; setTextColor(color); this.gravity = gravity; if (face != null) typeface = face
        includeFontPadding = true
    }

    fun title(value: String) = text(value, 0f, WHITE, sansBold).apply { setTextSize(TypedValue.COMPLEX_UNIT_PX, uf(84f)); setPadding(0, u(32), 0, u(6)) }
    fun subtitle(value: String) = text(value, 14.5f, TEXT).apply { setPadding(0, 0, 0, dp(14)); setLineSpacing(0f, 1.1f) }
    fun sectionHeader(value: String) = text(value, 17f, WHITE, sansBold).apply { setPadding(0, dp(14), 0, dp(8)) }

    /** Single-line text that shrinks to fit its width (API 26+ uniform autosize). */
    fun fit(tv: TextView, minSp: Int, maxSp: Int): TextView = tv.apply {
        maxLines = 1; setAutoSizeTextTypeUniformWithConfiguration(minSp, maxSp, 1, TypedValue.COMPLEX_UNIT_SP)
    }

    fun glowText(tv: TextView, color: Int = BLUE, radius: Float = 14f): TextView = tv.apply { setShadowLayer(dpf(radius / 2), 0f, 0f, color) }

    fun icon(res: Int, tint: Int = BLUE, sizeDp: Int = 24): ImageView = ImageView(context).apply {
        setImageResource(res); imageTintList = ColorStateList.valueOf(tint); scaleType = ImageView.ScaleType.FIT_CENTER
        layoutParams = LinearLayout.LayoutParams(dp(sizeDp), dp(sizeDp))
    }

    // ---------- brand ----------
    fun wordmark(size: Float): TextView = glowText(text("GA.LAW.HELP", size, Color.rgb(236, 244, 255), serifBold, Gravity.CENTER), BLUE, 18f)
    fun tagline(size: Float): TextView = text("CLEAR ANSWERS. A STRONGER GEORGIA.", size, GOLD, serifMedium, Gravity.CENTER).apply { letterSpacing = 0.04f }

    /** Painterly Lady Justice from the approved mockup (blue statue variant for inner screens). */
    fun ladyJustice(painted: Boolean = false): View = ImageView(context).apply {
        setImageResource(if (painted) R.drawable.ga_lady_justice_art else R.drawable.ga_lady_justice_blue)
        scaleType = ImageView.ScaleType.FIT_CENTER; contentDescription = "Lady Justice holding the scales"
    }

    fun brandLockup(): View = ImageView(context).apply {
        setImageResource(R.drawable.ga_brand_lockup); scaleType = ImageView.ScaleType.FIT_XY; contentDescription = "GA.LAW.HELP — Clear answers. A stronger Georgia."
    }

    /** Compact header used on every inner screen (Talk to Me, My Cases, Settings …). */
    fun pageHeader(onMenu: () -> Unit): View {
        val bar = FrameLayout(context).apply { clipChildren = false }
        bar.addView(ladyJustice(), FrameLayout.LayoutParams(u(262), u(196)).apply { leftMargin = u(96); topMargin = u(4) })
        bar.addView(icon(R.drawable.ga_ic_menu, Color.rgb(74, 190, 253), 30).apply { contentDescription = "Open menu"; setOnClickListener { onMenu() } },
            FrameLayout.LayoutParams(u(78), u(78)).apply { leftMargin = u(42); topMargin = u(51) })
        bar.addView(brandLockup().apply { tag = "brand" }, FrameLayout.LayoutParams(u(530), u(119)).apply { leftMargin = u(326); topMargin = u(23) })
        val wrap = LinearLayout(context).apply { orientation = LinearLayout.VERTICAL; clipChildren = false }
        wrap.addView(bar, LinearLayout.LayoutParams(-1, u(196)))
        wrap.addView(View(context).apply { background = GradientDrawable(GradientDrawable.Orientation.LEFT_RIGHT, intArrayOf(withAlpha(BLUE, 40), Color.rgb(40, 150, 245), withAlpha(BLUE, 40))) }, LinearLayout.LayoutParams(-1, u(4)))
        return wrap
    }

    // ---------- controls ----------
    fun primaryButton(label: String, action: () -> Unit): TextView = text(label, 16f, WHITE, sansMedium, Gravity.CENTER).apply {
        background = primaryButtonBg(); setPadding(dp(16), dp(15), dp(16), dp(15)); isClickable = true; setOnClickListener { action() }
    }

    fun secondaryButton(label: String, action: () -> Unit): TextView = text(label, 15f, TEXT, null, Gravity.CENTER).apply {
        background = glowCard(CARD, STROKE_SOFT, 10, glow = false); setPadding(dp(16), dp(13), dp(16), dp(13)); isClickable = true; setOnClickListener { action() }
    }

    fun input(hint: String, multiLine: Boolean = false): EditText = EditText(context).apply {
        this.hint = hint; setHintTextColor(MUTED); setTextColor(WHITE); textSize = 15f
        background = glowCard(Color.argb(200, 8, 22, 40), STROKE_SOFT, 10, glow = false); setPadding(dp(14), dp(12), dp(14), dp(12))
        if (multiLine) { minLines = 3; gravity = Gravity.TOP } else setSingleLine(true)
    }

    fun labeledInput(label: String, hint: String, value: String = ""): Pair<LinearLayout, EditText> {
        val box = LinearLayout(context).apply { orientation = LinearLayout.VERTICAL; background = glowCard(Color.argb(200, 8, 22, 40), STROKE_SOFT, 10, glow = false); setPadding(dp(12), dp(8), dp(12), dp(6)) }
        box.addView(text(label, 12f, MUTED))
        val edit = EditText(context).apply { this.hint = hint; setText(value); setHintTextColor(MUTED); setTextColor(WHITE); textSize = 16f; background = null; setPadding(0, dp(2), 0, dp(4)); setSingleLine(true) }
        box.addView(edit)
        return box to edit
    }

    /** Search field with leading magnifier; optional trailing round arrow button. */
    fun searchField(hint: String, glowing: Boolean, height: Int = 52, showButton: Boolean = true, onSubmit: ((String) -> Unit)? = null): Pair<View, EditText> {
        val row = LinearLayout(context).apply {
            orientation = LinearLayout.HORIZONTAL; gravity = Gravity.CENTER_VERTICAL; setPadding(dp(16), 0, dp(8), 0)
            background = if (glowing) glowCard(Color.argb(220, 8, 24, 44), BLUE_BRIGHT, 14) else glowCard(Color.argb(200, 8, 22, 40), STROKE_SOFT, 12, glow = false)
        }
        row.addView(icon(R.drawable.ga_ic_search, MUTED, 24))
        val edit = EditText(context).apply {
            this.hint = hint; setHintTextColor(MUTED); setTextColor(WHITE); textSize = 15.5f; background = null; setSingleLine(true); setPadding(dp(12), 0, dp(8), 0)
            imeOptions = android.view.inputmethod.EditorInfo.IME_ACTION_SEARCH
            if (onSubmit != null) setOnEditorActionListener { v, _, _ -> onSubmit(v.text.toString()); true }
        }
        row.addView(edit, LinearLayout.LayoutParams(0, -1, 1f))
        if (onSubmit != null && showButton) {
            val go = FrameLayout(context).apply {
                background = GradientDrawable().apply { shape = GradientDrawable.OVAL; colors = intArrayOf(Color.rgb(40, 140, 255), Color.rgb(16, 98, 228)); setStroke(dp(1), Color.rgb(140, 200, 255)) }
                contentDescription = "Ask"; setOnClickListener { onSubmit(edit.text.toString()) }
                addView(icon(R.drawable.ga_ic_arrow_forward, WHITE, 22), FrameLayout.LayoutParams(dp(22), dp(22), Gravity.CENTER))
            }
            row.addView(go, LinearLayout.LayoutParams(dp(38), dp(38)))
        }
        row.layoutParams = LinearLayout.LayoutParams(-1, dp(height))
        return row to edit
    }

    /** Segmented tab chips (Statutes | Case Law | Court Rules, All | Active …). */
    fun tabs(labels: List<String>, selected: Int, onSelect: (Int) -> Unit, underline: Boolean = false): LinearLayout = LinearLayout(context).apply {
        orientation = LinearLayout.HORIZONTAL
        labels.forEachIndexed { i, label ->
            val active = i == selected
            val chip = text(label, 14.5f, if (active) (if (underline) BLUE_BRIGHT else WHITE) else TEXT, if (active) sansMedium else null, Gravity.CENTER).apply {
                background = when {
                    active && !underline -> primaryButtonBg(10)
                    active && underline -> LayerDrawable(arrayOf(glowCard(CARD, STROKE_SOFT, 10, glow = false), GradientDrawable().apply { setColor(BLUE_BRIGHT); cornerRadius = dpf(2f) })).apply { setLayerInset(1, dp(14), dp(38), dp(14), dp(2)); }
                    else -> glowCard(CARD, STROKE_SOFT, 10, glow = false)
                }
                setPadding(dp(6), dp(11), dp(6), dp(11)); setOnClickListener { onSelect(i) }
            }
            chip.isSingleLine = true
            addView(chip, LinearLayout.LayoutParams(0, dp(44), maxOf(label.length, 7).toFloat()).apply { setMargins(if (i == 0) 0 else dp(4), 0, if (i == labels.lastIndex) 0 else dp(4), 0) })
        }
    }

    /** Dropdown-styled selector box (All Titles ▾). */
    fun dropdown(value: String, onClick: () -> Unit): View = LinearLayout(context).apply {
        orientation = LinearLayout.HORIZONTAL; gravity = Gravity.CENTER_VERTICAL; setPadding(dp(12), 0, dp(8), 0)
        background = glowCard(Color.argb(200, 8, 22, 40), STROKE_SOFT, 10, glow = false); isClickable = true; setOnClickListener { onClick() }
        addView(text(value, 14.5f, TEXT).apply { maxLines = 1; ellipsize = android.text.TextUtils.TruncateAt.END }, LinearLayout.LayoutParams(0, -2, 1f))
        addView(icon(R.drawable.ga_ic_expand_more, TEXT, 22))
    }

    /** Row card: icon, title, subtitle, chevron — Motions, Emergency, list items. */
    fun rowCard(iconRes: Int?, title: String, subtitle: String?, iconTint: Int = BLUE, glow: Boolean = true, trailing: View? = null, iconSize: Int = 30, action: (() -> Unit)?): View = LinearLayout(context).apply {
        orientation = LinearLayout.HORIZONTAL; gravity = Gravity.CENTER_VERTICAL; setPadding(dp(16), dp(14), dp(12), dp(14))
        background = glowCard(CARD, if (glow) STROKE else STROKE_SOFT, 12, glow)
        if (iconRes != null) addView(icon(iconRes, iconTint, iconSize), LinearLayout.LayoutParams(dp(iconSize), dp(iconSize)).apply { rightMargin = dp(16) })
        val col = LinearLayout(context).apply { orientation = LinearLayout.VERTICAL }
        col.addView(text(title, 16f, WHITE, sansMedium))
        if (!subtitle.isNullOrBlank()) col.addView(text(subtitle, 13.5f, Color.rgb(140, 185, 230)).apply { setPadding(0, dp(2), 0, 0) })
        addView(col, LinearLayout.LayoutParams(0, -2, 1f))
        addView(trailing ?: icon(R.drawable.ga_ic_chevron_right, TEXT, 24))
        if (action != null) { isClickable = true; setOnClickListener { action() } }
    }

    /** Grouped settings list: one rounded container with thin dividers. */
    fun settingsList(rows: List<Triple<Int, String, View?>>, onClick: (Int) -> Unit): View = LinearLayout(context).apply {
        orientation = LinearLayout.VERTICAL; background = glowCard(CARD, STROKE_SOFT, 12, glow = false)
        rows.forEachIndexed { i, (iconRes, label, trailing) ->
            if (i > 0) addView(View(context).apply { setBackgroundColor(withAlpha(STROKE_SOFT, 160)) }, LinearLayout.LayoutParams(-1, dp(1)))
            addView(LinearLayout(context).apply {
                orientation = LinearLayout.HORIZONTAL; gravity = Gravity.CENTER_VERTICAL; setPadding(dp(14), dp(13), dp(12), dp(13)); isClickable = true; setOnClickListener { onClick(i) }
                addView(icon(iconRes, TEXT, 24), LinearLayout.LayoutParams(dp(24), dp(24)).apply { rightMargin = dp(18) })
                addView(text(label, 16f, TEXT), LinearLayout.LayoutParams(0, -2, 1f))
                addView(trailing ?: icon(R.drawable.ga_ic_chevron_right, TEXT, 22))
            }, LinearLayout.LayoutParams(-1, dp(56)))
        }
    }

    fun toggle(on: Boolean): View = FrameLayout(context).apply {
        background = rounded(if (on) Color.rgb(28, 120, 240) else Color.rgb(40, 55, 75), 14)
        addView(View(context).apply { background = GradientDrawable().apply { shape = GradientDrawable.OVAL; setColor(Color.rgb(230, 240, 250)) } },
            FrameLayout.LayoutParams(dp(22), dp(22), Gravity.CENTER_VERTICAL or (if (on) Gravity.END else Gravity.START)).apply { setMargins(dp(3), 0, dp(3), 0) })
        layoutParams = LinearLayout.LayoutParams(dp(50), dp(28))
    }

    /** Empty-state card styled like the mockup list rows. */
    fun emptyCard(iconRes: Int, title: String, body: String): View = LinearLayout(context).apply {
        orientation = LinearLayout.VERTICAL; gravity = Gravity.CENTER_HORIZONTAL; setPadding(dp(18), dp(22), dp(18), dp(22))
        background = glowCard(CARD, STROKE_SOFT, 12, glow = false)
        addView(icon(iconRes, GOLD, 36))
        addView(text(title, 16f, WHITE, sansMedium, Gravity.CENTER).apply { setPadding(0, dp(8), 0, dp(4)) })
        addView(text(body, 13.5f, MUTED, null, Gravity.CENTER))
    }

    fun note(value: String) = text(value, 12.5f, MUTED).apply { setPadding(0, dp(10), 0, dp(4)) }

    fun headline(white: String, blue: String, size: Float): TextView {
        val s = SpannableStringBuilder(white).apply { val start = length; append(blue); setSpan(ForegroundColorSpan(BLUE_BRIGHT), start, length, Spanned.SPAN_EXCLUSIVE_EXCLUSIVE) }
        return glowText(text(s, size, Color.rgb(240, 246, 255), serifBold, Gravity.CENTER), BLUE, 16f)
    }

    // ---------- navigation ----------
    fun bottomNav(items: List<NavItem>, selectedKey: String, large: Boolean = false): View {
        if (large) return bottomNavLarge(items, selectedKey)
        val wrap = LinearLayout(context).apply { orientation = LinearLayout.VERTICAL; setBackgroundColor(Color.rgb(0, 12, 29)) }
        wrap.addView(View(context).apply { background = GradientDrawable(GradientDrawable.Orientation.TOP_BOTTOM, intArrayOf(Color.rgb(10, 62, 125), Color.rgb(3, 30, 66))) }, LinearLayout.LayoutParams(-1, u(4)))
        val row = LinearLayout(context).apply { orientation = LinearLayout.HORIZONTAL }
        items.forEach { item ->
            val active = item.key == selectedKey
            val cell = FrameLayout(context).apply {
                isClickable = true; contentDescription = item.label; setOnClickListener { item.action() }
                background = android.graphics.drawable.RippleDrawable(ColorStateList.valueOf(withAlpha(BLUE, 60)), null, null)
            }
            val iconRes = if (active && item.icon == R.drawable.ga_ic_home) R.drawable.ga_ic_home_filled else item.icon
            val ic = icon(iconRes, if (active) Color.rgb(64, 170, 255) else Color.rgb(176, 205, 240), 24)
            if (active) ic.background = GradientDrawable().apply { gradientType = GradientDrawable.RADIAL_GRADIENT; gradientRadius = uf(34f); colors = intArrayOf(withAlpha(BLUE, 90), Color.TRANSPARENT) }
            cell.addView(ic, FrameLayout.LayoutParams(u(46), u(46), Gravity.CENTER_HORIZONTAL).apply { topMargin = u(14) })
            cell.addView(text(item.label, 0f, if (active) Color.rgb(240, 244, 250) else Color.rgb(186, 208, 238), if (active) sansMedium else null, Gravity.CENTER).apply {
                setTextSize(TypedValue.COMPLEX_UNIT_PX, uf(23.5f)); includeFontPadding = false; maxLines = 1
            }, FrameLayout.LayoutParams(-1, -2, Gravity.CENTER_HORIZONTAL).apply { topMargin = u(57) })
            if (active) cell.addView(View(context).apply {
                background = GradientDrawable().apply { setColor(Color.rgb(150, 210, 255)); cornerRadius = uf(4f); setStroke(u(2).coerceAtLeast(1), withAlpha(BLUE, 160)) }
            }, FrameLayout.LayoutParams(u(57), u(8), Gravity.CENTER_HORIZONTAL).apply { topMargin = u(87) })
            row.addView(cell, LinearLayout.LayoutParams(0, -1, 1f))
        }
        wrap.addView(row, LinearLayout.LayoutParams(-1, u(139)))
        return wrap
    }

    /** Inner-screen nav from the 16-screen mockup: taller, bigger icons/labels, blue active tab with an underline. */
    private fun bottomNavLarge(items: List<NavItem>, selectedKey: String): View {
        val wrap = LinearLayout(context).apply { orientation = LinearLayout.VERTICAL; background = GradientDrawable(GradientDrawable.Orientation.TOP_BOTTOM, intArrayOf(Color.rgb(4, 16, 32), Color.rgb(1, 9, 20))) }
        wrap.addView(View(context).apply { background = GradientDrawable(GradientDrawable.Orientation.LEFT_RIGHT, intArrayOf(Color.rgb(16, 60, 112), Color.rgb(30, 92, 160), Color.rgb(16, 60, 112))) }, LinearLayout.LayoutParams(-1, u(4)))
        val row = LinearLayout(context).apply { orientation = LinearLayout.HORIZONTAL }
        items.forEach { item ->
            val active = item.key == selectedKey
            val cell = FrameLayout(context).apply {
                isClickable = true; contentDescription = item.label; setOnClickListener { item.action() }
                background = android.graphics.drawable.RippleDrawable(ColorStateList.valueOf(withAlpha(BLUE, 60)), null, null)
            }
            val ic = icon(item.icon, if (active) Color.rgb(52, 168, 255) else Color.rgb(226, 234, 244), 24)
            if (active) ic.background = GradientDrawable().apply { gradientType = GradientDrawable.RADIAL_GRADIENT; gradientRadius = uf(46f); colors = intArrayOf(withAlpha(BLUE, 110), Color.TRANSPARENT) }
            cell.addView(ic, FrameLayout.LayoutParams(u(72), u(72), Gravity.CENTER_HORIZONTAL).apply { topMargin = u(26) })
            cell.addView(text(item.label, 0f, if (active) Color.rgb(64, 176, 255) else Color.rgb(222, 230, 240), if (active) sansMedium else sansMedium, Gravity.CENTER).apply {
                setTextSize(TypedValue.COMPLEX_UNIT_PX, uf(36f)); includeFontPadding = false; maxLines = 1
                if (active) setShadowLayer(uf(10f), 0f, 0f, BLUE)
            }, FrameLayout.LayoutParams(-1, -2, Gravity.CENTER_HORIZONTAL).apply { topMargin = u(110) })
            if (active) cell.addView(View(context).apply { background = GradientDrawable().apply { setColor(Color.rgb(40, 160, 255)); cornerRadius = uf(5f) } },
                FrameLayout.LayoutParams(u(150), u(9), Gravity.CENTER_HORIZONTAL).apply { topMargin = u(168) })
            row.addView(cell, LinearLayout.LayoutParams(0, -1, 1f))
        }
        wrap.addView(row, LinearLayout.LayoutParams(-1, u(180)))
        return wrap
    }

    /** Standard inner screen: header, scrolling content, bottom nav. Returns (root, content). */
    fun screen(onMenu: () -> Unit, nav: View?): Pair<View, LinearLayout> {
        val shell = LinearLayout(context).apply { orientation = LinearLayout.VERTICAL; background = screenBackground() }
        shell.addView(pageHeader(onMenu))
        val content = LinearLayout(context).apply { orientation = LinearLayout.VERTICAL; setPadding(dp(18), dp(4), dp(18), dp(20)) }
        shell.addView(ScrollView(context).apply { isFillViewport = true; addView(content) }, LinearLayout.LayoutParams(-1, 0, 1f))
        if (nav != null) shell.addView(nav)
        return shell to content
    }

    fun gap(v: Int) = View(context).apply { layoutParams = LinearLayout.LayoutParams(1, dp(v)) }
    fun lp(top: Int = 0, bottom: Int = 0, height: Int = ViewGroup.LayoutParams.WRAP_CONTENT) = LinearLayout.LayoutParams(-1, height).apply { setMargins(0, dp(top), 0, dp(bottom)) }
    fun sp(v: Float) = TypedValue.applyDimension(TypedValue.COMPLEX_UNIT_SP, v, context.resources.displayMetrics)
}
