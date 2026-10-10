import unittest

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

    def test_generated_and_dependency_folders_are_ignored(self):
        self.assertTrue(repository_ingest._is_ignored("webapp/node_modules/react/index.js"))
        self.assertTrue(repository_ingest._is_ignored("dist/assets/app.js"))
        self.assertFalse(repository_ingest._is_ignored("runtime/server.py"))


if __name__ == "__main__":
    unittest.main()
