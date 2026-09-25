plugins { id("com.android.application"); id("org.jetbrains.kotlin.android") }

android {
    namespace = "help.galaw.standalone"
    compileSdk = 35
    defaultConfig {
        applicationId = "help.galaw.standalone"
        minSdk = 26
        targetSdk = 35
        versionCode = 14
        versionName = "1.4.0"
        val apiBaseUrl = providers.gradleProperty("GALAW_API_BASE_URL").orElse("https://api-production-60cc.up.railway.app").get()
        buildConfigField("String", "API_BASE_URL", "\"$apiBaseUrl\"")
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions { jvmTarget = "17" }
    buildFeatures { buildConfig = true }
}

dependencies {
    implementation("androidx.core:core-ktx:1.15.0")
    implementation("androidx.appcompat:appcompat:1.7.0")
    implementation("androidx.activity:activity-ktx:1.10.0")
    implementation("com.google.android.material:material:1.12.0")
    implementation("androidx.security:security-crypto:1.1.0-alpha06")
}
