import unittest
from unittest import mock
from newsaggregate.db.databaseinstance import DatabaseInterface
from newsaggregate.rss.articleutils import Match
from newsaggregate.rss.articleutils import locate_article

from newsaggregate.rss.htmlcrawler import HTMLCrawler
from bs4 import BeautifulSoup
from newsaggregate.test.testdata import MOCK_FILE_TO_ARTICLE_MAPPING
from newsaggregate.test.test_utils import get_datalake_test_data, mock_data


class TestHTMLCrawler(unittest.TestCase):

    def test_get_html(self):
        html, active = HTMLCrawler.get_html('https://www.bbc.com/news/uk-politics-58552389')
        self.assertTrue(isinstance(html, str))
        
    def test_find_tag_with_names(self):
        class TestTag:
            def __init__(self, name, attrs):
                self.name = name
                self.attrs = attrs
        tag = TestTag("meta", { "content": "url1", "name": "twitter:image" })
        self.assertEqual(HTMLCrawler.find_tag_with_names(tag, ["twitter:image", "twitter:image:src"]), True)
        tag = TestTag("meta", { "content": "url1", "name": "facebook:image" })
        self.assertEqual(HTMLCrawler.find_tag_with_names(tag, ["twitter:image", "twitter:image:src"]), False)
    
    def test_get_metadata(self):
        text = """<!DOCTYPE html><html><meta property="og:image" content="imageurl1" /><picture class="bw-image"/></html>"""
        self.assertEqual(HTMLCrawler.get_metadata(text)['image_url'], "imageurl1")
        text = """<!DOCTYPE html><html><meta property="twitter:image" content="imageurl2" /><picture class="bw-image"/></html>"""
        self.assertEqual(HTMLCrawler.get_metadata(text)['image_url'], "imageurl2")
        text = """<!DOCTYPE html><html><meta property="twitter:image" content="imageurl2" /><meta property="og:image" content="imageurl1" /></html>"""
        self.assertEqual(HTMLCrawler.get_metadata(text)['image_url'], "imageurl2")
    
    def test_get_json_plus_metadata(self):
        text = """<!DOCTYPE html><html><script type="application/ld+json">
                    {"@context":"http://schema.org","@type":"NewsArticle","description":"The news"}
                </script></html>"""
        self.assertEqual(HTMLCrawler.get_json_plus_metadata(BeautifulSoup(text, "html.parser"))["description"], "The news")
        text = """<!DOCTYPE html><html><script type="application/ld+json">
                    {"@context":"http://schema.org","@type":"Menu","description":"The news"}
                </script></html>"""
        self.assertFalse(HTMLCrawler.get_json_plus_metadata(BeautifulSoup(text, "html.parser")))
        text = """<!DOCTYPE html>
        <script type="application/ld+json">{"@type":"Article","description":"The news2"}</script>
        """
        self.assertEqual(HTMLCrawler.get_json_plus_metadata(BeautifulSoup(text, "html.parser"))["description"], "The news2")



    def test_article_location(self):
        text = """<!DOCTYPE html><p>Lonely P</p>"""
        self.assertEqual(locate_article(BeautifulSoup(text, "html.parser")).name, "[document]")

        
        text = """<!DOCTYPE html><main><p>Lonely P</p></main>"""
        self.assertEqual(locate_article(BeautifulSoup(text, "html.parser")).name, "main")

        text = """<!DOCTYPE html><body><p>Lonely P</p></body>"""
        self.assertEqual(locate_article(BeautifulSoup(text, "html.parser")).name, "body")

        text = """<!DOCTYPE html><body><main><p>Lonely P</p></main></body>"""
        self.assertEqual(locate_article(BeautifulSoup(text, "html.parser")).name, "main")

        text = """<!DOCTYPE html><body><main><article><p>Lonely P</p></article></main></body>"""
        self.assertEqual(locate_article(BeautifulSoup(text, "html.parser")).name, "article")

        text = """<!DOCTYPE html><body><div><article class="1"><p>300chars_12345678998234ß23874ß23974ß2374ß32ß4897ßj8TB0aGQQaXOGvjhBWJzGRWL1jhEk0YNiR9sUl0vyZ0q5U3SPpeZtL6P070AhJshDuiLgCzAn0PriU1kW6ZKFo5CJvSGTRG8LsSrk7yPZHll0GDVGHQF9f5mVvFtvUSnjVVujTT86hVZn2jaShQgYL9GN9iAMCIOIVhop3X4xXqBFAsJN3nEWPVB4RYdCT8iZUqTW7HfeP6wbv4sHbRu3JnXe473jR9w40FSIqTAUAxWmygF3yhJV6FUceUpP</p></article><article class="2"><p>Lonely P</p></article></div></body>"""
        self.assertEqual(locate_article(BeautifulSoup(text, "html.parser")).name, "article")
        self.assertEqual(locate_article(BeautifulSoup(text, "html.parser")).attrs["class"], ["1"])

        tag = locate_article(BeautifulSoup(mock_data("ajz01", "html"), "html.parser"))
        self.assertEqual(tag.name, "main")



        #print(locate_article(BeautifulSoup(HTMLCrawler.get_html("https://www.sueddeutsche.de/meinung/krieg-ukraine-russland-kiew-waffen-1.5537278")[0], "html.parser")).name)




    def test_article_extraction(self):
        for _, prefix in MOCK_FILE_TO_ARTICLE_MAPPING.items():
            txt, html = mock_data(prefix)
            soup  = BeautifulSoup(html, "html.parser")
            article_text, _ = HTMLCrawler.parse_article(soup, "")
            self.assertEqual(txt, article_text, msg=f"Issue with {prefix}")


    def test_article_extraction_single(self):
        html = get_datalake_test_data("3227205")
        soup  = BeautifulSoup(html, "html.parser")
        article_text, _ = HTMLCrawler.parse_article(soup, "")


    def test_clean_unnecessary(self):
        test5 = """<!DOCTYPE html><body><main><article><p>Veröffentlicht 2022-01-02</p>
            <p>34r34r3f3 4 34 t3t 54 45 45 q  gt uz665 </p>
            <div class="alaa">o<span>Das ist recht 1234 unique </span><div class="test"><p>Das ist Werbung und unnötig</p></div></div>
            <p>unique sdöflmd dsm fds klfkdslfsd fnopsdfds foksd fklsd flk sdfklj sdf</p>
            <p>N i ds jdsoi  ds üiodnd sdü äoin dsd säüdjjkk jö  oä jk dsft</p>
            <div class="alaa">o<span>Das ist recht 1234 unique </span><div class="test"><p>Das ist Werbung und unnötig</p></div></div>
            </article></main></body>"""
        testsoup5 = BeautifulSoup(test5, "html.parser")
        HTMLCrawler.patterns["example.com"] = [Match("div", {"class": "alaa"}, "", "txt", "TRUE")]

        res = HTMLCrawler.clean_unnecessary(testsoup5, "http://example.com")
        self.assertNotIn("Das ist recht 1234 unique", res.get_text())

        testsoup5 = BeautifulSoup(test5, "html.parser")
        res = HTMLCrawler.clean_unnecessary(testsoup5, "http://sub.example.com")
        self.assertIn("Das ist recht 1234 unique", res.get_text())


    @mock.patch('newsaggregate.rss.htmlcrawler.get_unnecessary_text_pattern', side_effect=lambda _: [("url_pattern1", "tag_name2", "{}", "tag_text", "true"), ("url_pattern4", "tag_name5", "{}", "tag_text", "true")])
    def test_get_patterns(self, _):
        HTMLCrawler.get_patterns(0)
        print(HTMLCrawler.patterns)
        self.assertEqual(len(HTMLCrawler.patterns.items()), 2)
        patterns_for_one = HTMLCrawler.patterns["url_pattern1"]
        self.assertEqual(len(patterns_for_one), 1)
        self.assertEqual(patterns_for_one[0].tag_name, "tag_name2")
        self.assertEqual(patterns_for_one[0].tag_text, "tag_text")
        self.assertEqual(HTMLCrawler.patterns["url_pattern4"][0].tag_name, "tag_name5")


if __name__ =="__main__":
    TestHTMLCrawler().test_article_extraction_single()