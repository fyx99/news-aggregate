import unittest
from unittest import mock
from db.crud.feeds import Feed
from rss.util import Utils
from rss.rsscrawler import RSSCrawler
from test.test_utils import get_datalake_test_data, mock_data, test_data_func
from types import SimpleNamespace
from test.custom_testcase import CustomTestcase



class TestRSSCrawler(CustomTestcase):

    @mock.patch('requests.get', side_effect=lambda *args, **kwargs: SimpleNamespace(text=test_data_func("ft.rss.xml")))
    def test_parse_feed(self, _):
        feed = RSSCrawler.parse_feed("http://test.com/xml")
        self.assertEqual(len(feed.entries), 28)


        clean_entries = RSSCrawler.clean_entries(feed.entries, Feed(url="http://test.com/rss", id="100"))
        self.assertEqual(len(clean_entries), 28)
        self.assertEqual(clean_entries[0].url, "http://test.com/content/0706d6f4-6668-4f67-ab1c-d535d847caf7")
        self.assertEqual(clean_entries[0].publish_date, "2022-03-30 11:10:16")

        clean_entries = RSSCrawler.clean_entries(feed.entries, Feed(url="http://test.com/rss", id="100"))
        self.assertEqual(clean_entries[0].url, "http://test.com/content/0706d6f4-6668-4f67-ab1c-d535d847caf7")


    @mock.patch('requests.get', side_effect=lambda *args, **kwargs: SimpleNamespace(text=test_data_func("t3n.rss.xml")))
    def test_parse_feed_2(self, _):
        feed = RSSCrawler.parse_feed("http://test.com/xml")
        self.assertEqual(len(feed.entries), 20)

        clean_entries = RSSCrawler.clean_entries(feed.entries, Feed(url="http://test.com/rss", id="100"))
        self.assertEqual(len(clean_entries), 20)
        self.assertEqual(clean_entries[0].url, "https://t3n.de/news/gif-suchmaschinen-websites-679637/")



    def test_clean_text_whites(self):
        text = """Liveblog zum Ukraine-Krieg

                    Schweiz nimmt keine 'Verletzten'  is'nt aus der Ukraine auf\n  nervige extra‘ “zitate„      """

        clean_text = Utils.clean_text(text)
        self.assertEqual(clean_text, """Liveblog zum Ukraine-Krieg Schweiz nimmt keine 'Verletzten' is'nt aus der Ukraine auf nervige extra" "zitate\"""")
      
    





if __name__ =="__main__":
    TestRSSCrawler().test_clean_text_whites()