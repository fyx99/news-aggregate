from db import BaseDataClass
from db.databaseinstance import DatabaseInterface
from dataclasses import dataclass


@dataclass
class Feed(BaseDataClass):
    publisher: str
    url: str
    category: str
    language: str
    tier: int
    recommend: bool
    region: str

async def get_feeds(db: DatabaseInterface):
    rows = await db.db.query("SELECT publisher, url, category, language, tier, recommend, region from Feeds", result=True)
    return [Feed(**r) for r in rows]
    


async def save_feed_last_crawl(db: DatabaseInterface, feed: Feed):
    await db.db.query(f"UPDATE feeds SET last_crawl_date = current_timestamp WHERE url = $1", (feed.url,))

