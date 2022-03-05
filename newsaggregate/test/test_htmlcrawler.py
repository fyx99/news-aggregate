import unittest

from newsaggregate.rss.htmlcrawler import HTMLCrawler
from bs4 import BeautifulSoup
from newsaggregate.test.testdata import MOCK_FILE_TO_ARTICLE_MAPPING


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


    def mock_data(self, prefix, filetype=None):
        if filetype == "html":
            with open(f"newsaggregate/test/testdata/{prefix}.html") as htmlfile:
                return htmlfile.read()
        try:
            with open(f"newsaggregate/test/testdata/{prefix}.txt") as txtfile, open(f"newsaggregate/test/testdata/{prefix}.html") as htmlfile:
                return txtfile.read(), htmlfile.read()
        except FileNotFoundError:
            print("File not found")
            return "", ""

    def test_article_location(self):
        text = """<!DOCTYPE html><p>Lonely P</p>"""
        self.assertEqual(HTMLCrawler.locate_article(BeautifulSoup(text, "html.parser")).name, "[document]")

        
        text = """<!DOCTYPE html><main><p>Lonely P</p></main>"""
        self.assertEqual(HTMLCrawler.locate_article(BeautifulSoup(text, "html.parser")).name, "main")

        text = """<!DOCTYPE html><body><p>Lonely P</p></body>"""
        self.assertEqual(HTMLCrawler.locate_article(BeautifulSoup(text, "html.parser")).name, "body")

        text = """<!DOCTYPE html><body><main><p>Lonely P</p></main></body>"""
        self.assertEqual(HTMLCrawler.locate_article(BeautifulSoup(text, "html.parser")).name, "main")

        text = """<!DOCTYPE html><body><main><article><p>Lonely P</p></article></main></body>"""
        self.assertEqual(HTMLCrawler.locate_article(BeautifulSoup(text, "html.parser")).name, "article")

        text = """<!DOCTYPE html><body><div><article class="1"><p>300chars_12345678998234ß23874ß23974ß2374ß32ß4897ßj8TB0aGQQaXOGvjhBWJzGRWL1jhEk0YNiR9sUl0vyZ0q5U3SPpeZtL6P070AhJshDuiLgCzAn0PriU1kW6ZKFo5CJvSGTRG8LsSrk7yPZHll0GDVGHQF9f5mVvFtvUSnjVVujTT86hVZn2jaShQgYL9GN9iAMCIOIVhop3X4xXqBFAsJN3nEWPVB4RYdCT8iZUqTW7HfeP6wbv4sHbRu3JnXe473jR9w40FSIqTAUAxWmygF3yhJV6FUceUpP</p></article><article class="2"><p>Lonely P</p></article></div></body>"""
        self.assertEqual(HTMLCrawler.locate_article(BeautifulSoup(text, "html.parser")).name, "article")
        self.assertEqual(HTMLCrawler.locate_article(BeautifulSoup(text, "html.parser")).attrs["class"], ["1"])

        tag = HTMLCrawler.locate_article(BeautifulSoup(self.mock_data("ajz01", "html"), "html.parser"))
        self.assertEqual(tag.name, "main")



        #print(HTMLCrawler.locate_article(BeautifulSoup(HTMLCrawler.get_html("https://www.sueddeutsche.de/meinung/krieg-ukraine-russland-kiew-waffen-1.5537278")[0], "html.parser")).name)




    def test_article_extraction(self):
        for _, prefix in MOCK_FILE_TO_ARTICLE_MAPPING.items():
            txt, html = self.mock_data(prefix)
            soup  = BeautifulSoup(html, "html.parser")
            article_text, _ = HTMLCrawler.parse_article(soup)
            self.assertEqual(txt, article_text, msg=f"Issue with {prefix}")



        