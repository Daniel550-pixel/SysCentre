import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch

import repository_ingest


class RepositoryRegistryTests(unittest.TestCase):
    def test_catalog_has_unique_ids_and_urls(self):
        projects = repository_ingest.load_catalog()
        self.assertGreaterEqual(len(projects), 20)
        ids = [item["id"] for item in projects]
        urls = [item["url"] for item in projects]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(urls), len(set(urls)))
        self.assertIn("syscentre", ids)
        self.assertIn("networklab", ids)
        self.assertIn("experienceengine", ids)

    def test_unmatched_historical_projects_are_not_given_guessed_urls(self):
        from pathlib import Path
        import json
        inventory_path = Path(repository_ingest.__file__).with_name("project_inventory.json")
        with inventory_path.open("r", encoding="utf-8") as handle:
            inventory = json.load(handle)
        projects = inventory["projects"]
        self.assertGreaterEqual(len(projects), 10)
        self.assertTrue(all(item["status"] == "repository_match_required" for item in projects))
        self.assertTrue(all("url" not in item for item in projects))
        self.assertEqual(len({item["id"] for item in projects}), len(projects))

    def test_unknown_project_cannot_be_ingested(self):
        with self.assertRaises(ValueError):
            repository_ingest._repo_id("unknown-project")

    def test_sensitive_paths_are_excluded(self):
        for path in (".env", "config/.env.production", "keys/id_rsa", "certs/server.pem", "secrets/token.txt"):
            with self.subTest(path=path):
                self.assertTrue(repository_ingest._is_sensitive(path))

    def test_normal_source_files_are_not_marked_sensitive(self):
        for path in ("runtime/server.py", "README.md", "webapp/src/App.tsx"):
            with self.subTest(path=path):
                self.assertFalse(repository_ingest._is_sensitive(path))


    def test_blob_decoder_accepts_utf8_source(self):
        self.assertEqual(repository_ingest._decode_blob_text(b"print('syscentre')"), "print('syscentre')")

    def test_blob_decoder_rejects_nul_bytes(self):
        with self.assertRaises(UnicodeDecodeError):
            repository_ingest._decode_blob_text(b"header\x00payload")

    def test_blob_decoder_rejects_invalid_utf8(self):
        with self.assertRaises(UnicodeDecodeError):
            repository_ingest._decode_blob_text(b"\xff\xfe")

    def test_source_search_rejects_short_queries(self):
        with self.assertRaises(ValueError):
            repository_ingest.search_index("x")

    def test_ingest_status_is_persisted_and_empty_registry_is_valid(self):
        with tempfile.TemporaryDirectory() as directory:
            db_path = Path(directory) / "syscentre-test.db"
            with patch.object(repository_ingest.server, "DB_PATH", db_path):
                status = repository_ingest.ingest_status()
                self.assertEqual(status, {"jobs": [], "count": 0})
                self.assertTrue(db_path.exists())

    def test_ingest_status_rejects_unknown_project(self):
        with tempfile.TemporaryDirectory() as directory:
            db_path = Path(directory) / "syscentre-test.db"
            with patch.object(repository_ingest.server, "DB_PATH", db_path):
                with self.assertRaises(ValueError):
                    repository_ingest.ingest_status("not-a-real-project")

    def test_generated_and_dependency_folders_are_ignored(self):
        self.assertTrue(repository_ingest._is_ignored("webapp/node_modules/react/index.js"))
        self.assertTrue(repository_ingest._is_ignored("dist/assets/app.js"))
        self.assertFalse(repository_ingest._is_ignored("runtime/server.py"))


if __name__ == "__main__":
    unittest.main()
