import unittest
from app.services.scraper_service import parse_title_artist_fallback

class TestScraperService(unittest.TestCase):
    def test_parse_title_artist_comma_by(self):
        title, artist = parse_title_artist_fallback("Cosmic Voyage, by Star Voyager")
        self.assertEqual(title, "Cosmic Voyage")
        self.assertEqual(artist, "Star Voyager")

    def test_parse_title_artist_hyphen(self):
        title, artist = parse_title_artist_fallback("Solaris - Deep Space EP")
        self.assertEqual(title, "Deep Space EP")
        self.assertEqual(artist, "Solaris")

    def test_parse_title_artist_by(self):
        title, artist = parse_title_artist_fallback("Lunar Drift by Night Runner")
        self.assertEqual(title, "Lunar Drift")
        self.assertEqual(artist, "Night Runner")

    def test_parse_title_artist_pipe(self):
        title, artist = parse_title_artist_fallback("Ambient Echoes | Sound Laboratory")
        self.assertEqual(title, "Ambient Echoes")
        self.assertEqual(artist, "Sound Laboratory")

    def test_parse_title_artist_plain_with_site_name(self):
        title, artist = parse_title_artist_fallback("Just An Album", site_name="Label Records")
        self.assertEqual(title, "Just An Album")
        self.assertEqual(artist, "Label Records")

if __name__ == "__main__":
    unittest.main()
