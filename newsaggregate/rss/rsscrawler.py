import asyncio
import time, feedparser, traceback
from typing import List
import aiohttp

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

    client = None

    async def parse_feed(db: DatabaseInterface, rss_feed):
        try:
            res = await db.http.session.get(rss_feed)
            rss_content = await res.content.read()
            rss_parsed = feedparser.parse(rss_content) 
            return rss_parsed
        except Exception as e:
            logger.debug("HTTP ERROR")
            return None
    
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

    async def save_entries(db: DatabaseInterface, articles: List[Article]):
        article_futures =  [save_rss_article(db, article) for article in articles]
        return await asyncio.gather(*article_futures)
    
    async def run_single(db: DatabaseInterface, feed: Feed) -> List[RssEntry]:
        logger.debug(f"RSS RUN SINGLE {feed.url}")
        try:
            start = time.time()
            parsed_feed = await RSSCrawler.parse_feed(db, feed.url)
            if not parsed_feed:
                logger.debug("PARSE FEED RETURNED NOTHING")
                return []
            entries = RSSCrawler.get_entries(parsed_feed)
            entries_articles = RSSCrawler.clean_entries(entries, feed.url)
            rss_articles = await RSSCrawler.save_entries(db, entries_articles)
            await save_feed_last_crawl(db, feed)
            logger.debug(f"RSS TIME {time.time()-start:.2f}")
            return rss_articles
        except Exception as e:
            logger.error(traceback.format_exc())
            return []
        