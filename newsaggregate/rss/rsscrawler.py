import requests, time, feedparser, traceback
from typing import List

from newsaggregate.db.config import HTTP_TIMEOUT
from newsaggregate.db.crud.article import save_rss_article
from newsaggregate.db.crud.feeds import save_feed_last_crawl
from newsaggregate.db.databaseinstance import DatabaseInterface
from newsaggregate.rss.util import Utils
from newsaggregate.logging import get_logger
logger = get_logger()


class RssEntry:
    title:str
    link:str
    entry_id: str
    summary:str
    author: str
    published: str
    published_parsed: any

class RSSCrawler:

    def parse_feed(rss_feeds):
        try:
            rss_texts = [requests.get(rss_url, timeout=HTTP_TIMEOUT, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"}).text for rss_url in rss_feeds]
            rss_texts_parsed = [feedparser.parse(text) for text in rss_texts]
            return rss_texts_parsed
        except Exception as e:
            logger.error(traceback.format_exc())
            return []
    
    def get_entries(rss_parsed):
        entries = []
        for entry in rss_parsed.entries:
            entries.append({field: entry[field] for field in ["title", "link", "id", "summary", "author", "published", "published_parsed"] if field in entry})
        return entries
    
    def clean_entries(entries: List[RssEntry], rss_feed):
        clean = []
        for entry in entries:
            try:
                clean_obj = { **entry }
                clean_obj["link"] = Utils.clean_link(clean_obj["link"], rss_feed)
                clean_obj["summary"] = Utils.clean_text(clean_obj["summary"])
                clean_obj["title"] = Utils.clean_text(clean_obj["title"]) 
                clean_obj["published_parsed"] = Utils.clean_date(clean_obj["published_parsed"])
                clean_obj["published"] = Utils.clean_date_string(clean_obj["published_parsed"])
                clean.append(clean_obj)
            except KeyError:
                pass
        return clean

    def save_entries(db: DatabaseInterface, entries: List[RssEntry], rss_feed: str):
        for entry in entries:
            job_id, article_status = save_rss_article(db, rss_feed, entry["link"], entry["title"], entry["summary"], entry["published_parsed"])
            db.dl.put_json(f"testing/article_rss/{job_id}", {"rss": {"url": entry["link"], "title": entry["title"], "summary": entry["summary"], "publish_date": entry["published"]}})
            yield (job_id, article_status)
    
    def run_single(db: DatabaseInterface, rss_feed: str) -> List[RssEntry]:
        try:
            start = time.time()
            feed = RSSCrawler.parse_feed([rss_feed])
            if not len(feed):
                raise Exception("Parse Feed return 0 Items")
            entries = RSSCrawler.get_entries(feed[0])
            clean_entries = RSSCrawler.clean_entries(entries, rss_feed)
            ids_statuses = RSSCrawler.save_entries(db, clean_entries, rss_feed)
            save_feed_last_crawl(db, rss_feed)
            logger.info(f"RSS TIME {time.time()-start}")
            return clean_entries, ids_statuses
        except Exception as e:
            logger.error(traceback.format_exc())
            return [], []
        

            
    def top_n_entries(feed_entries, n=2):
        return [feed[index] for index in range(n) for feed in feed_entries] 