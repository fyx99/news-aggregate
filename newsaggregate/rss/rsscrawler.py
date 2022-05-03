import requests, time, feedparser, traceback
from typing import List

from db.config import HTTP_TIMEOUT
from db.crud.article import Article, save_rss_article
from db.crud.feeds import Feed, save_feed_last_crawl
from db.databaseinstance import DatabaseInterface
from rss.util import Utils
from logger import get_logger
logger = get_logger()


class RssEntry:
    title:str = ""
    link:str = ""
    entry_id: str = ""
    summary:str = ""
    author: str = ""
    published: str = ""
    published_parsed: any = ""

    def dict_to_entry(entry_dict):
        entry = RssEntry()
        [setattr(entry, field, entry_dict[field]) for field in ["title", "link", "id", "summary", "author", "published", "published_parsed"] if field in entry_dict]
        return entry

class RSSCrawler:

    def parse_feed(rss_feeds):
        try:
            rss_texts = [requests.get(rss_url, timeout=HTTP_TIMEOUT, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"}).text for rss_url in rss_feeds]
            rss_texts_parsed = [feedparser.parse(text) for text in rss_texts]
            return rss_texts_parsed
        except Exception as e:
            logger.info("HTTP ERROR")
            return []
    
    def get_entries(rss_parsed):
        return [RssEntry.dict_to_entry(entry_dict) for entry_dict in rss_parsed.entries]
    
    def clean_entries(entries: List[RssEntry], rss_feed):
        clean_entries = []
        for entry in entries:
            try:
                entry.link = Utils.clean_link(entry.link, rss_feed)
                entry.summary = Utils.clean_text(entry.summary)
                entry.title = Utils.clean_text(entry.title) 
                entry.published_parsed = Utils.clean_date_direct_string(entry.published_parsed)
                #entry.published = Utils.clean_date_string(entry.published_parsed)
                clean_entries.append(entry)
            except (KeyError, AttributeError):
                pass
        return [Article.article_from_entry(e, rss_feed) for e in clean_entries]

    def save_entries(db: DatabaseInterface, articles: List[Article]):
        for article in articles:
            article = save_rss_article(db, article)
            yield article
    
    def run_single(db: DatabaseInterface, feed: Feed) -> List[RssEntry]:
        try:
            start = time.time()
            parsed_feed = RSSCrawler.parse_feed([feed.url])
            if not len(parsed_feed):
                logger.info("Parse Feed returned 0 Items")
                return []
            entries = RSSCrawler.get_entries(parsed_feed[0])
            entries_articles = RSSCrawler.clean_entries(entries, feed.url)
            rss_articles = RSSCrawler.save_entries(db, entries_articles)
            save_feed_last_crawl(db, feed)
            logger.info(f"RSS TIME {time.time()-start:.2f}")
            return rss_articles
        except Exception as e:
            logger.error(traceback.format_exc())
            return []
        

            
    # def top_n_entries(feed_entries, n=2):
    #     return [feed[index] for index in range(n) for feed in feed_entries] 