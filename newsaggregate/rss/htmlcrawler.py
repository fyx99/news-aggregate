from collections import defaultdict
import difflib
import re
import traceback
from typing import Dict, List
from bs4 import BeautifulSoup, Tag
import requests
import json
from db.config import HTTP_TIMEOUT
from db.crud.article import Article, save_article, set_article_status
from db.crud.textpattern import get_unnecessary_text_pattern
from db.databaseinstance import DatabaseInterface
from db.postgresql import Database
from db.crud.textpattern import Match
from db.crud.articlelocators import get_article_locators, ArticleLocator
from rss.articleutils import locate_article
import time
import urllib.request
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module='bs4')

from logger import get_logger
logger = get_logger()


from rss.util import Utils

headers = {
    "User-Agent": "Googlebot/2.1 (+http://www.google.com/bot.html)"
}
#{"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"}

class HTMLCrawler:

    patterns: Dict[str, List[Match]] = defaultdict(list)
    article_locators: Dict[str, ArticleLocator] = {}

    def get_patterns(db):
        patterns_list = get_unnecessary_text_pattern(db)
        HTMLCrawler.patterns = defaultdict(list)
        [HTMLCrawler.patterns[pattern.url_pattern].append(pattern) for pattern in patterns_list]

    def get_article_locators(db):
        article_locators_list = get_article_locators(db)
        HTMLCrawler.article_locators = {al.url_pattern: al for al in article_locators_list}

    def preload(db):
        HTMLCrawler.get_patterns(db)
        HTMLCrawler.get_article_locators(db)

    def get_html(url):
        try:
            res = requests.get(url, headers=headers, timeout=HTTP_TIMEOUT)
            if res.status_code == 200:
                return res.text, "ACTIVE"
            return res.text, "INACTIVE"
        except:
            return "", "INACTIVE"

    def get_url_status_code(url):
        try:
            req = urllib.request.Request(url, headers=headers)
            res = urllib.request.urlopen(req, timeout=HTTP_TIMEOUT).getcode()
            if res == 200:
                return "ACTIVE"
            return "INACTIVE"
        except:
            return "INACTIVE"

    
    def find_tag_with_names(tag: Tag, names):
        if tag.name == "meta":
            for attr in tag.attrs.values():
                if attr in names:
                    return True
        return False
    
    def get_metadata(text):
        parser = "html.parser"
        soup = BeautifulSoup(text, parser)
    
        image_tags: List[Tag] = soup.findAll(lambda t: HTMLCrawler.find_tag_with_names(t, ["twitter:image", "twitter:image:src", "og:image", "og:image:url"]))
        image_url = image_tags[0].attrs["content"] if len(image_tags) else ""
        
        amp_tag: List[Tag] = soup.findAll("link", {"rel": "amphtml"})
        amp_url = amp_tag[0].attrs["href"] if amp_tag else ""

        keyword_tag: List[Tag] = soup.findAll(lambda t: HTMLCrawler.find_tag_with_names(t, ["keywords", "news_keywords"]))
        keywords_raw = keyword_tag[0].attrs["content"].split(",") if keyword_tag else []
        keywords = [str(e).strip() for e in keywords_raw]
        keywords = [e for e in keywords  if e != ""]

        return image_url, amp_url, keywords

    
    def parse_json_tags(json_scripts):
        json_parsed = []
        for script in json_scripts:
            try:
                json_parsed.append(json.loads(script.text))
            except Exception as e:
                logger.error(e)
        return json_parsed

    
    def any_news_article(markups):
        for entry in markups:
            if '@type' in entry and entry['@type'] in ["Article", "ReportageNewsArticle", "NewsArticle"]:
                return entry
        return False
    
    def get_json_plus_metadata(soup):
        markups_flat = []
        try:
            markups = [json.loads("".join(e.contents)) for e in soup.findAll("script", {"type":"application/ld+json"})]
            for m in markups:
                if isinstance(m, dict):
                    markups_flat.append(m)
                    continue
                for n in m:
                    markups_flat.append(n)
        except json.decoder.JSONDecodeError as e:
            logger.error("JSON DECODE ERROR")
        return HTMLCrawler.any_news_article(markups_flat)

    
    def clean_unnecessary(soup: BeautifulSoup, url):
        for pattern in HTMLCrawler.patterns[Utils.get_domain(url)]:
            if pattern.tag_identifyable == "TRUE":
                ps: List[Tag] = soup.find_all(pattern.tag_name, attrs=pattern.tag_attrs)
                combined_text =  re.sub('\s+',' ', "".join([p.get_text() for p in ps]))[:1000]
                if len(combined_text) > 500:
                    a = 1
                if len(combined_text) > 500 and difflib.SequenceMatcher(None, pattern.tag_text, combined_text).ratio() < 0.8:
                    # this is a indicator, that elements are sometimes trash, but sometimes not -> only clear if text is trash
                    continue
                [p.clear() for p in ps]
            else:
                raise NotImplementedError
        return soup
        

    def parse_article(soup: BeautifulSoup, url: str):
        
        article = locate_article(soup, HTMLCrawler.article_locators.get(Utils.get_domain(url), None))
        article = HTMLCrawler.clean_unnecessary(article, url)
        if not article:
            raise Exception("No Article")

        article_text = " ".join([" ".join(p.get_text().split()) for p in article.findAll("p")])
        article_text = article_text.strip()
        article_h1 = soup.findAll("h1")
        article_title = article_h1[0].get_text() if len(article_h1) else ""
        article_title_clean = Utils.clean_text(article_title)
        return article_text, article_title_clean


    def run_single(db: DatabaseInterface, article: Article):
        try:
            start = time.time()
            html, article.status = HTMLCrawler.get_html(article.url)
            get_html_time = time.time() - start
            if article.status == "INACTIVE":
                logger.debug(f"INACTIVE {article.url}")
                return set_article_status(db, article)
                
            parser = "html.parser"
            soup = BeautifulSoup(html, parser)
            markups = HTMLCrawler.get_json_plus_metadata(soup)
            article.image_url, article.amp_url, keywords = HTMLCrawler.get_metadata(html)

            article.text, article.title = HTMLCrawler.parse_article(soup, article.url)
            parse_html_time = time.time() - start - get_html_time

            img_status = HTMLCrawler.get_url_status_code(article.image_url)
            if img_status == "INACTIVE":
                logger.debug(f"INACTIVE IMAGE {article.url}")
                status = img_status

            img_html_time = time.time() - start - get_html_time - parse_html_time
            save_article(db, article, markups, html, keywords)
            save_article_time = time.time() - start - parse_html_time - get_html_time - img_html_time
            logger.debug(f"HTML {get_html_time=:.2f} {parse_html_time=:.2f} {img_html_time=:.2f} {save_article_time=:.2f}")
        except Exception as e:
            logger.error("ERROR FOR " + article.url + " " + repr(e)) 
            logger.error(traceback.format_exc())   
            

if __name__ == "__main__":

    with Database() as db:
        di = DatabaseInterface(db) 
        HTMLCrawler.preload(di)


    url = "https://www.mdr.de/nachrichten/sachsen/leipzig/leipzig-leipzig-land/lastenraeder-mieten-ausleihe-modell-oeko-verkehrswende-100.html"
    HTMLCrawler.run_single(di, Article(url=url))