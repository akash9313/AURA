import os
import tempfile
import unittest
from memory.manager import MemoryManager
from memory.persistence import SQLiteDatabase
from memory.store import SQLiteMemoryRepository


class TestMemoryEngine(unittest.TestCase):

    def setUp(self):
        # Create a temporary database file for isolated testing
        self.temp_db_file = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_db_file.close()

        self.db = SQLiteDatabase(db_path=self.temp_db_file.name)
        self.repo = SQLiteMemoryRepository(db=self.db)
        self.memory = MemoryManager(repo=self.repo)

    def tearDown(self):
        # Remove temporary database file
        if os.path.exists(self.temp_db_file.name):
            os.remove(self.temp_db_file.name)

    def test_remember_name_and_recall(self):
        # "Remember my name is Akash."
        self.memory.remember("name", "Akash", category="identity")
        recalled_name = self.memory.recall("name")
        self.assertEqual(recalled_name, "Akash")

    def test_remember_language_preference_and_recall(self):
        # "Remember I like Python."
        self.memory.remember("favorite_language", "Python", category="preference")
        recalled_lang = self.memory.recall("favorite_language")
        self.assertEqual(recalled_lang, "Python")

    def test_forget_fact(self):
        # "Forget my name."
        self.memory.remember("name", "Akash", category="identity")
        self.assertEqual(self.memory.recall("name"), "Akash")

        forget_success = self.memory.forget("name")
        self.assertTrue(forget_success)
        self.assertIsNone(self.memory.recall("name"))

    def test_profile_listing(self):
        self.memory.remember("name", "Akash")
        self.memory.remember("favorite_language", "Python")
        self.memory.remember("timezone", "IST")

        prof = self.memory.profile()
        self.assertEqual(prof.get("name"), "Akash")
        self.assertEqual(prof.get("favorite_language"), "Python")
        self.assertEqual(prof.get("timezone"), "IST")

    def test_working_memory_lifecycle(self):
        self.memory.working.set_task("Writing a Python script")
        self.memory.working.set_goal("Fix memory engine unit tests")
        self.memory.working.set_variable("user_lang", "Python")
        self.memory.working.add_message("user", "Help me code in Python")

        snapshot = self.memory.working.snapshot()
        self.assertEqual(snapshot.task, "Writing a Python script")
        self.assertEqual(snapshot.goal, "Fix memory engine unit tests")
        self.assertEqual(snapshot.temp_variables.get("user_lang"), "Python")

        self.memory.working.clear()
        cleared_snapshot = self.memory.working.snapshot()
        self.assertIsNone(cleared_snapshot.task)
        self.assertEqual(len(cleared_snapshot.messages), 0)

    def test_conversation_summary_generation(self):
        cid = "test-conv-123"
        self.memory.conversation.start_conversation(cid)
        self.memory.conversation.add_message("user", "Hello AURA, can you launch Notepad?")
        self.memory.conversation.add_message("assistant", "Sure! Notepad opened.")

        record = self.memory.summarize(cid)
        self.assertIsNotNone(record)
        self.assertEqual(record.conversation_id, cid)
        self.assertIsNotNone(record.title)
        self.assertIsNotNone(record.summary)
        self.assertGreater(len(record.keywords), 0)

    def test_search_memories(self):
        self.memory.remember("favorite_language", "Python")
        self.memory.conversation.start_conversation("search-conv-1")
        self.memory.conversation.add_message("user", "How do I build a search engine?")
        self.memory.conversation.finish_conversation(
            title="Search Engine Discussion",
            summary="Discussion about building search index",
            keywords=["search", "python"]
        )

        results = self.memory.search("Python")
        self.assertGreater(len(results), 0)

        type_found = [r.memory_type for r in results]
        self.assertIn("profile", type_found)


if __name__ == "__main__":
    unittest.main()
