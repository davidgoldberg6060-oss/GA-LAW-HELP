package help.galaw.standalone

import android.content.Intent
import android.graphics.Color
import android.graphics.Typeface
import android.graphics.drawable.GradientDrawable
import android.os.Bundle
import android.util.Patterns
import android.view.Gravity
import android.view.View
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import kotlin.concurrent.thread

class AuthActivity : AppCompatActivity() {
    private lateinit var api: ApiClient
    private lateinit var root: LinearLayout
    private val navy = Color.rgb(4,18,31)
    private val blue = Color.rgb(40,169,255)
    private val card = Color.rgb(11,35,54)

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        api = ApiClient(this)
        if (api.token != null) openApp() else showAuth()
    }

    private fun dp(v:Int)=(v*resources.displayMetrics.density).toInt()
    private fun text(value:String,size:Float=16f)=TextView(this).apply { text=value; textSize=size; setTextColor(Color.WHITE) }
    private fun field(hintText:String,password:Boolean=false)=EditText(this).apply {
        hint=hintText; setHintTextColor(Color.rgb(150,172,190)); setTextColor(Color.WHITE); setPadding(dp(18),dp(14),dp(18),dp(14))
        background=GradientDrawable().apply { cornerRadius=dp(16).toFloat(); setColor(Color.rgb(8,31,49)); setStroke(dp(1),Color.rgb(39,124,184)) }
        if(password) inputType=129
    }
    private fun button(title:String,primary:Boolean=false,onClick:()->Unit)=Button(this).apply {
        text=title; isAllCaps=false; textSize=15f; setTextColor(Color.WHITE)
        background=GradientDrawable().apply { cornerRadius=dp(16).toFloat(); setColor(if(primary) Color.rgb(18,112,176) else card); setStroke(dp(1),if(primary) blue else Color.rgb(29,67,94)) }
        setOnClickListener { onClick() }
    }
    private fun add(view:View,top:Int=10){ root.addView(view,LinearLayout.LayoutParams(-1,-2).apply{setMargins(0,dp(top),0,0)}) }
    private fun toast(message:String)=Toast.makeText(this,message,Toast.LENGTH_LONG).show()

    private fun validEmail(value:String):Boolean = value.isNotBlank() && Patterns.EMAIL_ADDRESS.matcher(value).matches()
    private fun validateCredentials(email:String,password:String):Boolean {
        if(!validEmail(email)) { toast("Enter a valid email address."); return false }
        if(password.length < 15) { toast("Password must be at least 15 characters."); return false }
        return true
    }

    private fun base(){
        root=LinearLayout(this).apply { orientation=LinearLayout.VERTICAL; setPadding(dp(22),dp(30),dp(22),dp(30)); setBackgroundColor(navy) }
        setContentView(ScrollView(this).apply { setBackgroundColor(navy); addView(root) })
    }

    private fun showAuth(){
        base()
        add(ImageView(this).apply { setImageResource(R.drawable.ic_lady_justice); scaleType=ImageView.ScaleType.CENTER_INSIDE; contentDescription="Lady Justice" },0)
        root.getChildAt(0).layoutParams=LinearLayout.LayoutParams(-1,dp(170))
        add(text("GA.LAW.HELP",32f).apply { gravity=Gravity.CENTER; setTypeface(typeface,Typeface.BOLD) },2)
        add(text("KNOW YOUR RIGHTS. PROTECT YOUR FUTURE.",12f).apply { gravity=Gravity.CENTER; setTextColor(blue) },2)
        add(text("Georgia legal help, documents, case tools and AI guidance in one secure place.",15f).apply { gravity=Gravity.CENTER; setTextColor(Color.rgb(190,205,215)) },12)
        val email=field("Email address")
        val password=field("Password (15+ characters)",true)
        add(email,22); add(password,10)
        add(button("Log in",true){
            val emailValue=email.text.toString().trim(); val passwordValue=password.text.toString()
            if(validateCredentials(emailValue,passwordValue)) runTask("Signing in…") { api.auth("/auth/login",emailValue,passwordValue); openApp() }
        },14)
        add(button("Create account"){
            val emailValue=email.text.toString().trim(); val passwordValue=password.text.toString()
            if(validateCredentials(emailValue,passwordValue)) runTask("Creating account…") {
                val result=api.auth("/auth/register",emailValue,passwordValue)
                runOnUiThread { if(result.optBoolean("verification_required")) showVerification(emailValue) else openApp() }
            }
        },8)
        add(button("Browse Funny & Weird Georgia Laws free"){ showFreeLaws() },8)
        val links=LinearLayout(this).apply { orientation=LinearLayout.HORIZONTAL }
        links.addView(button("Verify email"){
            val emailValue=email.text.toString().trim()
            if(validEmail(emailValue)) showVerification(emailValue) else toast("Enter a valid email address first.")
        },LinearLayout.LayoutParams(0,-2,1f))
        links.addView(button("Forgot password"){
            val emailValue=email.text.toString().trim()
            if(validEmail(emailValue)) showReset(emailValue) else toast("Enter a valid email address first.")
        },LinearLayout.LayoutParams(0,-2,1f).apply{setMargins(dp(8),0,0,0)})
        add(links,8)
        add(text("GA.LAW.HELP provides legal information and assistance tools, not a substitute for a licensed attorney.",11f).apply { gravity=Gravity.CENTER; setTextColor(Color.rgb(135,158,176)) },18)
    }

    private fun showVerification(email:String){
        base(); add(text("VERIFY EMAIL",28f).apply{setTypeface(typeface,Typeface.BOLD)},0)
        add(text("Open the verification email sent to ${email.ifBlank{"your email address"}}, or paste the verification token below.",14f),8)
        val token=field("Verification token"); add(token,14)
        add(button("Verify",true){
            val tokenValue=token.text.toString().trim()
            if(tokenValue.isBlank()) toast("Enter the verification token.")
            else runTask("Verifying…"){api.verifyEmail(tokenValue);runOnUiThread{toast("Email verified. Log in now.");showAuth()}}
        },12)
        add(button("Resend verification email"){
            if(!validEmail(email)) toast("Enter a valid email on the login screen first.")
            else runTask("Sending…"){api.resendVerification(email);runOnUiThread{toast("If the account exists, a new email was sent.")}}
        },8)
        add(button("Back to login"){showAuth()},8)
    }

    private fun showReset(emailValue:String){
        base(); add(text("RESET PASSWORD",28f).apply{setTypeface(typeface,Typeface.BOLD)},0)
        val email=field("Email address").apply{setText(emailValue)}; val token=field("Reset token"); val password=field("New password (15+ characters)",true)
        add(email,12); add(button("Send reset email",true){
            val value=email.text.toString().trim()
            if(!validEmail(value)) toast("Enter a valid email address.")
            else runTask("Sending…"){api.forgotPassword(value);runOnUiThread{toast("If the account exists, a reset email was sent.")}}
        },8)
        add(token,16); add(password,8)
        add(button("Set new password",true){
            val tokenValue=token.text.toString().trim(); val passwordValue=password.text.toString()
            when {
                tokenValue.isBlank() -> toast("Enter the reset token.")
                passwordValue.length < 15 -> toast("Password must be at least 15 characters.")
                else -> runTask("Resetting…"){api.resetPassword(tokenValue,passwordValue);runOnUiThread{toast("Password changed. Log in now.");showAuth()}}
            }
        },10)
        add(button("Back to login"){showAuth()},8)
    }

    private fun showFreeLaws(){
        base(); add(text("FUNNY & WEIRD GEORGIA LAWS",27f).apply{setTypeface(typeface,Typeface.BOLD)},0)
        add(text("MYTH CHECKER — FREE",13f).apply{setTextColor(blue)},4)
        add(text("Many viral ‘weird law’ lists mix folklore, old local publicity stories and real law. Treat internet claims as myths until a current official Georgia or local source verifies them.",15f),14)
        add(text("• Fried chicken must be eaten by hand — commonly tied to Gainesville publicity lore, not a statewide criminal rule.\n\n• Donkey in a bathtub — widely repeated online; verify against current official law before relying on it.\n\n• Ice-cream cone in a back pocket on Sunday — another repeated internet claim that should not be treated as current statewide law without an official source.",15f),14)
        add(button("Back to login"){showAuth()},16)
    }

    private fun runTask(message:String,work:()->Unit){
        Toast.makeText(this,message,Toast.LENGTH_SHORT).show()
        thread {
            try { work() }
            catch(e:Exception){ runOnUiThread { toast(e.message ?: "Something went wrong. Please try again.") } }
        }
    }

    private fun openApp(){ runOnUiThread { startActivity(Intent(this,HomeActivity::class.java)); finish() } }
}
