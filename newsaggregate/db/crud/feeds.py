from db import BaseDataClass
from db.databaseinstance import DatabaseInterface
from dataclasses import dataclass


@dataclass
class Feed(BaseDataClass):
    id: str = ""
    publisher: str = ""
    url: str = ""
    category: str = ""
    language: str = ""
    tier: int = ""
    recommend: bool = True
    region: str = ""

def get_feeds(db: DatabaseInterface):
    rows = db.db.query("SELECT id, publisher, url, category, language, tier, recommend, region from Feeds", result=True)
    return [Feed(**r) for r in rows]
    


def save_feed_last_crawl(db: DatabaseInterface, feed: Feed):
    db.db.query(f"UPDATE feeds SET last_crawl_date = current_timestamp WHERE url = %s", (feed.url,))

