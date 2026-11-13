package help.galaw.standalone

/** One paper-reader / upload batch is at most 10 pages. Extra picks never wipe pages already chosen. */
object PageBatch {
    const val MAX = DocumentLibrary.MAX_PAGES

    data class Cap<T>(val pages: List<T>, val added: Int, val dropped: Int, val message: String)

    fun remaining(count: Int, max: Int = MAX): Int = (max - count.coerceAtLeast(0)).coerceAtLeast(0)

    fun canAdd(count: Int, max: Int = MAX): Boolean = remaining(count, max) > 0

    fun counter(count: Int, max: Int = MAX): String = "$count of $max"

    fun overflowMessage(added: Int, dropped: Int): String {
        if (dropped <= 0) return ""
        if (added == 0) return "You already have $MAX pages in this batch. Send these first, then add more pages to this case."
        return "You can add $MAX pages at a time. I kept the first $added of this selection and left your earlier pages in place."
    }

    fun <T> cap(existing: List<T>, incoming: List<T>, max: Int = MAX): Cap<T> {
        val room = remaining(existing.size, max)
        val kept = incoming.take(room)
        val dropped = (incoming.size - kept.size).coerceAtLeast(0)
        return Cap(existing + kept, kept.size, dropped, overflowMessage(kept.size, dropped))
    }
}
