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
        super.onCreate(savedInstanceState); SystemBars.apply(this);api = ApiClient(this)
        // Sign-in is optional (Account tab). Anonymous device sessions stay on this screen.
        if (api.token != null && !api.isAnonymous) openApp() else showAuth()
    }

    private fun dp(v:Int)=(v*resources.displayMetrics.density).toInt()
    private fun text(value:String,size:Float=16f)=TextView(this).apply { text=value; textSize=size; setTextColor(Color.WHITE) }
    private val ui by lazy { GaUi(this) }
    private fun field(hintText:String,password:Boolean=false)=ui.input(hintText).apply {
        setPadding(dp(16),dp(14),dp(16),dp(14))
        if(password) inputType=129
    }
    private fun button(title:String,primary:Boolean=false,onClick:()->Unit):TextView = if(primary) ui.primaryButton(title){ onClick() } else ui.secondaryButton(title){ onClick() }
    private fun add(view:View,top:Int=10){ root.addView(view,LinearLayout.LayoutParams(-1,-2).apply{setMargins(0,dp(top),0,0)}) }
    private fun toast(message:String)=Toast.makeText(this,message,Toast.LENGTH_LONG).show()

    private fun validEmail(value:String):Boolean = value.isNotBlank() && Patterns.EMAIL_ADDRESS.matcher(value).matches()
    /** Login accepts any existing password; the backend Login schema has no length rule. */
    private fun validateLogin(email:String,password:String):Boolean {
        if(!validEmail(email)) { toast("Enter a valid email address."); return false }
        if(password.isEmpty()) { toast("Enter your password."); return false }
        return true
    }
    /** Registration and reset keep the backend 15-128 character policy (UserCreate / reset schema). */
    private fun validateRegistration(email:String,password:String):Boolean {
        if(!validEmail(email)) { toast("Enter a valid email address."); return false }
        if(password.length < 15) { toast("Password must be at least 15 characters."); return false }
        if(password.length > 128) { toast("Password must be no more than 128 characters."); return false }
        return true
    }

    private fun base(){
        root=LinearLayout(this).apply { orientation=LinearLayout.VERTICAL; setPadding(dp(22),dp(24),dp(22),dp(30)) }
        setContentView(ScrollView(this).apply { background=ui.screenBackground(); isFillViewport=true; addView(root) })
    }

    private fun showAuth(){
        base()
        root.addView(ui.ladyJustice(),LinearLayout.LayoutParams(dp(130),dp(156)).apply{gravity=Gravity.CENTER_HORIZONTAL})
        add(ui.wordmark(30f),2)
        add(ui.tagline(10f),2)
        add(ui.headline("LEGAL ANSWERS ","ANYTIME",22f),16)
        add(text("Georgia legal help, documents, case tools and AI guidance in one secure place.",15f).apply { gravity=Gravity.CENTER; setTextColor(Color.rgb(190,205,215)) },12)
        val email=field("Email address")
        val password=field("Password (new accounts: 15+ characters)",true)
        add(email,22); add(password,10)
        add(button("Log in",true){
            val emailValue=email.text.toString().trim(); val passwordValue=password.text.toString()
            if(validateLogin(emailValue,passwordValue)) runTask("Signing in…") { api.auth("/auth/login",emailValue,passwordValue); openApp() }
        },14)
        add(button("Create account"){
            val emailValue=email.text.toString().trim(); val passwordValue=password.text.toString()
            if(validateRegistration(emailValue,passwordValue)) runTask("Creating account…") {
                val result=api.auth("/auth/register",emailValue,passwordValue)
                runOnUiThread { if(result.optBoolean("verification_required")) showVerification(emailValue) else openApp() }
            }
        },8)
        add(button("Continue without an account"){ openApp() },8)
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
        add(text("An account is optional. Without one, your cases are saved to this device's anonymous ID. This is legal information, not a substitute for a licensed attorney. Stay calm. Do not resist, lie, or destroy evidence.",11f).apply { gravity=Gravity.CENTER; setTextColor(Color.rgb(135,158,176)) },18)
    }

    private fun showVerification(email:String){
        base(); add(ui.title("Verify Email"),0)
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
        base(); add(ui.title("Reset Password"),0)
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
                passwordValue.length > 128 -> toast("Password must be no more than 128 characters.")
                else -> runTask("Resetting…"){api.resetPassword(tokenValue,passwordValue);runOnUiThread{toast("Password changed. Log in now.");showAuth()}}
            }
        },10)
        add(button("Back to login"){showAuth()},8)
    }

    private fun showFreeLaws(){
        startActivity(android.content.Intent(this, FunnyLawsActivity::class.java))
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
