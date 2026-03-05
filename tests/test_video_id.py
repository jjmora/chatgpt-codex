import unittest

from youtube_script_extractor import extract_video_id


class ExtractVideoIdTests(unittest.TestCase):
    def test_plain_id(self):
        self.assertEqual(extract_video_id("dQw4w9WgXcQ"), "dQw4w9WgXcQ")

    def test_watch_url(self):
        self.assertEqual(
            extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ"),
            "dQw4w9WgXcQ",
        )

    def test_short_url(self):
        self.assertEqual(extract_video_id("https://youtu.be/dQw4w9WgXcQ"), "dQw4w9WgXcQ")

    def test_invalid(self):
        with self.assertRaises(ValueError):
            extract_video_id("https://example.com/video")


if __name__ == "__main__":
    unittest.main()
