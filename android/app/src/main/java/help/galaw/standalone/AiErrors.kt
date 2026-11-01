package help.galaw.standalone

import java.io.InterruptedIOException
import java.net.SocketTimeoutException

/** Turns raw network failures (e.g. OkHttp's bare "timeout") into friendly, retryable messages. */
object AiErrors {
    const val TIMEOUT_MESSAGE =
        "GA.LAW.HELP is taking longer than usual to answer. Your question wasn’t lost — tap Retry to try again."
    const val NETWORK_MESSAGE =
        "Couldn’t reach GA.LAW.HELP. Check your internet connection, then tap Retry."
    const val GENERIC_MESSAGE = "Something went wrong. Please tap Retry."

    fun isTimeout(e: Throwable): Boolean {
        var c: Throwable? = e
        while (c != null) {
            if (c is SocketTimeoutException || c is InterruptedIOException) return true
            if (c.message?.trim()?.lowercase()?.let { it == "timeout" || it.contains("timed out") || it == "read timed out" } == true) return true
            c = c.cause
        }
        return false
    }

    /** True when a Retry button makes sense (timeouts, connection problems, server busy). */
    fun isRetryable(e: Throwable): Boolean = isTimeout(e) || e is ApiNetworkException || e is java.io.IOException ||
        (e is ApiException && e.statusCode in setOf(502, 503, 504))

    fun message(e: Throwable): String = when {
        isTimeout(e) -> TIMEOUT_MESSAGE
        e is ApiException || e is IllegalArgumentException -> e.message?.takeIf { it.isNotBlank() } ?: GENERIC_MESSAGE
        e is ApiNetworkException -> e.message ?: NETWORK_MESSAGE
        e is java.io.IOException -> NETWORK_MESSAGE
        else -> e.message?.takeIf { it.isNotBlank() && it.trim().lowercase() != "timeout" } ?: GENERIC_MESSAGE
    }
}
