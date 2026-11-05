package help.galaw.standalone

import java.io.File
import kotlin.test.Test
import kotlin.test.assertTrue
import kotlin.test.assertEquals

class FunnyGeorgiaDataTest {
    private fun assetFile(): File {
        val candidates = listOf(
            File("app/src/main/assets/funny_georgia.json"),
            File("src/main/assets/funny_georgia.json"),
            File("../app/src/main/assets/funny_georgia.json")
        )
        return candidates.firstOrNull { it.exists() }
            ?: File(".").walkTopDown().maxDepth(6).first { it.name == "funny_georgia.json" && it.path.contains("assets") }
    }

    private fun funnySrc(): String {
        val candidates = listOf(
            File("app/src/main/java/help/galaw/standalone/FunnyLawsActivity.kt"),
            File("src/main/java/help/galaw/standalone/FunnyLawsActivity.kt"),
            File("../app/src/main/java/help/galaw/standalone/FunnyLawsActivity.kt")
        )
        return candidates.firstOrNull { it.exists() }?.readText()
            ?: File(".").walkTopDown().maxDepth(8).first { it.name == "FunnyLawsActivity.kt" }.readText()
    }

    @Test
    fun corpusHasAtLeast150VerifiedEntriesWithFullText() {
        val json = assetFile().readText()
        val lawBlocks = Regex("\"citation\"\\s*:\\s*\"O\\.C\\.G\\.A\\.").findAll(json).count()
        // laws use O.C.G.A. citations; cases use reporter citations — count full_text fields
        val fullTexts = Regex("\"full_text\"\\s*:\\s*\"").findAll(json).count()
        val titles = Regex("\"title\"\\s*:").findAll(json).count()
        assertTrue(fullTexts >= 150, "full_text count $fullTexts")
        assertTrue(lawBlocks >= 100, "OCGA citations $lawBlocks")
        assertTrue(titles >= 100)
        assertTrue(json.contains("\"categories\""))
        assertTrue(json.contains("State symbols"))
        assertTrue(json.contains("Cars & roads"))
        assertTrue(json.contains("Weird local rules"))
        assertTrue(!json.contains("dumb laws", ignoreCase = true))
        // every law source_url https
        Regex("\"source_url\"\\s*:\\s*\"([^\"]+)\"").findAll(json).forEach {
            assertTrue(it.groupValues[1].startsWith("https://"), it.groupValues[1])
        }
    }

    @Test
    fun screenDefaultsToDeckModeAndCategories() {
        val src = funnySrc()
        assertTrue(src.contains("deckMode = true"))
        assertTrue(src.contains("Shuffle"))
        assertTrue(src.contains("Share"))
        assertTrue(src.contains("attachSwipe"))
        assertTrue(src.contains("From STANDALONE ASSISTANT"))
        assertEquals(7, FunnyGeorgiaData.CATEGORIES.size)
    }
}
