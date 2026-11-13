package help.galaw.standalone

import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFalse
import kotlin.test.assertNull
import kotlin.test.assertTrue

class UsageAnalyticsTest {
    @Test
    fun promptWaitsForAFewUsesAndTwoWeeks() {
        val now = 1_000_000_000_000L
        assertFalse(UsageAnalytics.shouldPrompt(UsageAnalytics.PROMPT_AFTER_OPENS - 1, 0, 0, now))
        assertTrue(UsageAnalytics.shouldPrompt(UsageAnalytics.PROMPT_AFTER_OPENS, 0, 0, now))
        assertFalse(UsageAnalytics.shouldPrompt(10, now - UsageAnalytics.PROMPT_GAP_MS + 1000, 0, now))
        assertFalse(UsageAnalytics.shouldPrompt(10, 0, now - UsageAnalytics.PROMPT_GAP_MS + 1000, now))
        assertTrue(UsageAnalytics.shouldPrompt(10, now - UsageAnalytics.PROMPT_GAP_MS - 1000, 0, now))
    }

    @Test
    fun feedbackRequiresRatingOrCommentAndValidEmail() {
        assertTrue(UsageAnalytics.validateFeedback(null, "idea", "", "") != null)
        assertNull(UsageAnalytics.validateFeedback(4, "idea", "", ""))
        assertNull(UsageAnalytics.validateFeedback(null, "bug", "It crashed.", ""))
        assertTrue(UsageAnalytics.validateFeedback(5, "other", "ok", "bad") != null)
        assertNull(UsageAnalytics.validateFeedback(5, "other", "ok", "a@b.co"))
        assertEquals(listOf("bug", "design", "idea", "slow", "other"), UsageAnalytics.CATEGORIES.map { it.first })
    }
}
