import unittest
import base64
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

    def test_interrupted_ingest_resumes_from_saved_file_checkpoints(self):
        with tempfile.TemporaryDirectory() as directory:
            db_path = Path(directory) / "syscentre-test.db"
            nodes = [
                {"type": "blob", "path": f"src/file-{index:03}.py", "sha": f"blob-{index:03}", "size": 12}
                for index in range(51)
            ]
            failed_once = {"value": False}
            blob_calls = {}

            def fake_api(url):
                if url.endswith("/repos/Daniel550-pixel/SysCentre"):
                    return {"default_branch": "main", "description": "test", "private": False}
                if url.endswith("/commits/main"):
                    return {"sha": "commit-test"}
                if url.endswith("/git/trees/commit-test?recursive=1"):
                    return {"truncated": False, "sha": "tree-test", "tree": nodes}
                if "/git/blobs/" in url:
                    blob_sha = url.rsplit("/", 1)[-1]
                    blob_calls[blob_sha] = blob_calls.get(blob_sha, 0) + 1
                    if blob_sha == "blob-050" and not failed_once["value"]:
                        failed_once["value"] = True
                        raise RuntimeError("simulated transient fetch failure")
                    return {"content": base64.b64encode(b"print('indexed')").decode("ascii")}
                raise AssertionError("Unexpected GitHub URL: " + url)

            with patch.object(repository_ingest.server, "DB_PATH", db_path), patch.object(repository_ingest, "_api_json", side_effect=fake_api):
                with self.assertRaisesRegex(RuntimeError, "simulated transient"):
                    repository_ingest.ingest_repository("syscentre")

                progress = repository_ingest.ingest_status("syscentre")["jobs"][0]
                self.assertEqual(progress["status"], "failed")
                self.assertEqual(progress["files_processed"], 50)

                result = repository_ingest.ingest_repository("syscentre")
                self.assertTrue(result["resumed"])
                self.assertEqual(result["files_processed"], 51)
                self.assertEqual(blob_calls["blob-000"], 1)
                self.assertEqual(blob_calls["blob-049"], 1)
                self.assertEqual(blob_calls["blob-050"], 2)

                with repository_ingest.server._DB_LOCK:
                    with repository_ingest.server._database() as connection:
                        count = connection.execute(
                            "SELECT COUNT(*) FROM repository_files WHERE project_id = 'syscentre'"
                        ).fetchone()[0]
                self.assertEqual(count, 51)
                self.assertEqual(repository_ingest.ingest_status("syscentre")["jobs"][0]["status"], "indexed")

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
