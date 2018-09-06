import unittest

from project.domain.model import Config
from project.domain.search import SearchPreferences, Matcher
from project.service.scrapper import Rutracker

tracker = Rutracker(Config.get("RUTR_USER"), Config.get("RUTR_PASS"))
tracker.login()


class TestScrapper(unittest.TestCase):
    def test_rutr_login(self):
        self.assertTrue(tracker.is_logged())

    def test_rutr_search(self):
        preferences = SearchPreferences(['The Shawshank Redemption'], year=1994)
        search_page_content = tracker.get_search_result_page(preferences.generated_keywords[0])
        matches = tracker.get_matches_from_search_result(search_page_content, preferences)
        self.assertGreater(len(matches), 10)

        bests = Matcher.get_best(matches, 3)
        self.assertEquals(len(bests), 3)

        current_score = bests[0].get_quality()
        for best in bests:
            self.assertGreater(best.get_quality(), 10)
            self.assertLessEqual(best.get_quality(), current_score, "matches came not in DESC order")
            current_score = best.get_quality()
