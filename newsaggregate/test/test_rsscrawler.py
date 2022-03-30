import unittest
from unittest import mock

from newsaggregate.db.databaseinstance import DatabaseInterface

from newsaggregate.rss.rsscrawler import RSSCrawler
from bs4 import BeautifulSoup
from newsaggregate.test.testdata import MOCK_FILE_TO_ARTICLE_MAPPING
from newsaggregate.test.test_utils import get_datalake_test_data, mock_data, test_data_func
from types import SimpleNamespace


class TestRSSCrawler(unittest.TestCase):

    @mock.patch('requests.get', side_effect=lambda *args, **kwargs: SimpleNamespace(text=test_data_func("ft.rss.xml")))
    def test_parse_feed(self, _):
        feed = RSSCrawler.parse_feed(["http://test.com/xml"])
        self.assertEqual(len(feed), 1)
        self.assertEqual(len(feed[0].entries), 28)

        entries  = RSSCrawler.get_entries(feed[0])
        self.assertEqual(entries[0]["link"], "/content/0706d6f4-6668-4f67-ab1c-d535d847caf7")

        clean_entries = RSSCrawler.clean_entries(entries, "http://test.com/content")
        self.assertEqual(len(clean_entries), 27)
        self.assertEqual(clean_entries[0]["link"], "http://test.com/content/0706d6f4-6668-4f67-ab1c-d535d847caf7")
        self.assertEqual(clean_entries[0]["published"], "2022-03-30 11:10:16")

        clean_entries = RSSCrawler.clean_entries(entries, "http://test.com/content")
        self.assertEqual(clean_entries[0]["link"], "http://test.com/content/0706d6f4-6668-4f67-ab1c-d535d847caf7")


    @mock.patch('requests.get', side_effect=lambda *args, **kwargs: SimpleNamespace(text=test_data_func("t3n.rss.xml")))
    def test_parse_feed_2(self, _):
        feed = RSSCrawler.parse_feed(["http://test.com/xml"])
        self.assertEqual(len(feed), 1)
        self.assertEqual(len(feed[0].entries), 20)

        entries  = RSSCrawler.get_entries(feed[0])
        self.assertEqual(entries[0]["link"], "https://t3n.de/news/gif-suchmaschinen-websites-679637/?utm_source=rss&utm_medium=feed&utm_campaign=buzz & memes")

        clean_entries = RSSCrawler.clean_entries(entries, "http://test.com/content")
        self.assertEqual(len(clean_entries), 20)
        self.assertEqual(clean_entries[0]["link"], "https://t3n.de/news/gif-suchmaschinen-websites-679637/")




if __name__ =="__main__":
    TestRSSCrawler().test_parse_feed_2()