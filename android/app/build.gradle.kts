plugins { id("com.android.application"); id("org.jetbrains.kotlin.android") }

android {
    namespace = "help.galaw.standalone"
    compileSdk = 35
    defaultConfig {
        applicationId = "help.galaw.standalone"
        minSdk = 26
        targetSdk = 35
        versionCode = 23
        versionName = "1.5.8"
        val apiBaseUrl = providers.gradleProperty("GALAW_API_BASE_URL").orElse("https://api-production-60cc.up.railway.app").get()
        buildConfigField("String", "API_BASE_URL", "\"$apiBaseUrl\"")
    }

    val releaseKeystorePath = providers.gradleProperty("GALAW_RELEASE_KEYSTORE_PATH").orNull
    val releaseStorePassword = providers.gradleProperty("GALAW_RELEASE_STORE_PASSWORD").orNull
    val releaseKeyAlias = providers.gradleProperty("GALAW_RELEASE_KEY_ALIAS").orNull
    val releaseKeyPassword = providers.gradleProperty("GALAW_RELEASE_KEY_PASSWORD").orNull
    val hasReleaseSigning = listOf(
        releaseKeystorePath,
        releaseStorePassword,
        releaseKeyAlias,
        releaseKeyPassword,
    ).all { !it.isNullOrBlank() }

    // Stable debug signing: a committed debug keystore (standard Android debug credentials, not a
    // secret) so debug APKs from any machine or CI run upgrade in place without uninstalling.
    signingConfigs {
        getByName("debug") {
            storeFile = rootProject.file("debug.keystore")
            storePassword = "android"
            keyAlias = "androiddebugkey"
            keyPassword = "android"
        }
    }

    if (hasReleaseSigning) {
        signingConfigs {
            create("release") {
                storeFile = file(releaseKeystorePath!!)
                storePassword = releaseStorePassword
                keyAlias = releaseKeyAlias
                keyPassword = releaseKeyPassword
            }
        }
        buildTypes {
            getByName("release") {
                signingConfig = signingConfigs.getByName("release")
            }
        }
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
