package help.galaw.standalone

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class PageBatchTest {
    @Test fun counterStartsAtZeroOfTen() {
        assertEquals(10, PageBatch.MAX)
        assertEquals("0 of 10", PageBatch.counter(0))
        assertEquals(10, PageBatch.remaining(0))
        assertEquals(3, PageBatch.remaining(7))
        assertEquals(0, PageBatch.remaining(10))
        assertFalse(PageBatch.canAdd(10))
        assertTrue(PageBatch.canAdd(9))
    }

    @Test fun laterPickIsCappedAndNeverWipesEarlierPages() {
        val first = PageBatch.cap(listOf("a", "b", "c"), listOf("d", "e"))
        assertEquals(listOf("a", "b", "c", "d", "e"), first.pages)
        assertEquals(0, first.dropped)

        val overflow = PageBatch.cap((1..8).map { "p$it" }, listOf("n1", "n2", "n3", "n4"))
        assertEquals((1..8).map { "p$it" } + listOf("n1", "n2"), overflow.pages)
        assertEquals(2, overflow.added)
        assertEquals(2, overflow.dropped)
        assertTrue(overflow.message.contains("kept the first 2"))
    }

    @Test fun selectingMoreThanTenAtOnceKeepsTheFirstTen() {
        val incoming = (1..15).map { "f$it" }
        val result = PageBatch.cap(emptyList(), incoming)
        assertEquals(incoming.take(10), result.pages)
        assertEquals(5, result.dropped)
        assertTrue(result.message.contains("10 pages at a time"))
    }

    @Test fun aFullBatchRejectsNewFilesWithoutClearingTheTenAlreadyChosen() {
        val existing = (1..10).map { "e$it" }
        val result = PageBatch.cap(existing, listOf("extra1", "extra2"))
        assertEquals(existing, result.pages)
        assertEquals(0, result.added)
        assertEquals(2, result.dropped)
        assertTrue(result.message.contains("already have 10"))
    }
}
