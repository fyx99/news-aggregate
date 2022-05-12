






from typing import List
from db.crud.article import Article
from db.async_postgresql import AsyncDatabase


async def get_articles_clean(db: AsyncDatabase) -> List[Article]:
    rows = await db.query("""
                        SELECT id, url, amp_url, image_url, title, summary, publish_date, feed, title_hash, status, text from articles_clean
                        """, 
                        result=True)
    return [Article(**article) for article in rows]