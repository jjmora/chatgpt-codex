import unittest
from unittest.mock import patch

from web_app import app


class WebAppTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_index_renders(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"YouTube Script Extractor", response.data)

    def test_extract_requires_video(self):
        response = self.client.post("/extract", data={"video": ""})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Debes pegar una URL o ID de YouTube", response.data)

    @patch("web_app.extract_script", return_value="# Video: x\ntexto\n")
    def test_extract_success(self, _mock_extract):
        response = self.client.post("/extract", data={"video": "dQw4w9WgXcQ", "langs": "es en"})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"# Video: x", response.data)


if __name__ == "__main__":
    unittest.main()
