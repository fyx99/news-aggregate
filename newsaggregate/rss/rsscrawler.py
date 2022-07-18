import requests, time, feedparser, traceback
from typing import List

from db.config import HTTP_TIMEOUT
from db.crud.article import save_rss_article, FeedArticle
from db.crud.feeds import Feed, save_feed_last_crawl
from db.databaseinstance import DatabaseInterface
from rss.util import Utils

from logger import get_logger
logger = get_logger()


class RSSCrawler:

    def parse_feed(rss_feed: str):
        try:
            rss_text = requests.get(rss_feed, timeout=HTTP_TIMEOUT, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"}).text
            rss_text_parsed = feedparser.parse(rss_text)
            return rss_text_parsed

        except Exception as e:
            logger.debug("HTTP ERROR")
            return None

    
    def clean_entries(entries: List[dict], rss_feed: Feed) -> List[FeedArticle]:

        clean_feed_articles = []
        for rank, entry in enumerate(entries):
            try:
                clean_feed_articles.append(FeedArticle(
                    title=Utils.clean_text(entry.get("title", "")),
                    url=Utils.clean_link(entry.get("link", ""), rss_feed.url),
                    summary=Utils.clean_text(entry.get("summary", "")),
                    publish_date=Utils.clean_date_direct_string(entry.get("published_parsed", "")),
                    feed=rss_feed.url,
                    rank=rank+1,
                    feed_id=rss_feed.id
                ))
                
            except (KeyError, AttributeError) as e:
                print(e)
                continue
        return clean_feed_articles

        

    def save_entries(db: DatabaseInterface, articles: List[FeedArticle]):
        for article in articles:
            article = save_rss_article(db, article)
            yield article
    
    def run_single(db: DatabaseInterface, feed: Feed):
        try:
            start = time.time()
            parsed_feed = RSSCrawler.parse_feed(feed.url)
            if not parsed_feed:
                logger.debug("FEED PARSE RETURNED NO ARTICLES")
                return []
            feedarticles: FeedArticle = RSSCrawler.clean_entries(parsed_feed.entries, feed)
            rss_articles = RSSCrawler.save_entries(db, feedarticles)
            save_feed_last_crawl(db, feed)
            logger.debug(f"RSS TIME {time.time()-start:.2f}")
            return rss_articles
        except Exception as e:
            logger.error(traceback.format_exc())
            return []
        
