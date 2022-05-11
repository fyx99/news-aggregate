from typing import List
from db import BaseDataClass
from db.crud.blob import Embedding
from db.crud.feeds import Feed
from db.databaseinstance import DatabaseInterface
from dataclasses import dataclass
import re
from logger import get_logger
logger = get_logger()
from datetime import datetime


@dataclass
class Article(BaseDataClass):
    id: str = ""
    url: str = ""
    amp_url: str = ""
    image_url: str = ""
    title: str = ""
    summary: str = ""
    publish_date: datetime = None
    feed: str = ""
    title_hash: str = ""
    status: str = ""
    text: str = ""

        

    def article_from_entry(entry, feed):
        return Article(title=entry.title, url=entry.link, summary=entry.summary, publish_date=entry.published_parsed, feed=feed)


async def get_articles(db: DatabaseInterface):
    rows = await db.db.query("SELECT id, url, amp_url, image_url, title, summary, publish_date, feed, title_hash, status, text from Articles;", result=True)
    return [Article(**r) for r in rows]

async def get_article(db: DatabaseInterface, id):
    row = await db.db.query("SELECT id, url, amp_url, image_url, title, summary, publish_date, feed, title_hash, status, text from Articles where id = $1;", (id,), result=True)[0]
    return Article(**row)


async def get_random_articles(db: DatabaseInterface, limit=200):
    rows = await db.db.query(f"SELECT id, a.url, amp_url, image_url, a.title, summary, publish_date, feed, title_hash, status, text, publisher, language, recommend, category, tier, region from Articles as a left join Feeds as f on f.url = feed limit {limit};", result=True)
    return [(Article(r["id"], r["url"], r["amp_url"], r["image_url"], r["title"], r["summary"], r["publish_date"], r["feed"], r["title_hash"], r["status"], r["text"]), 
        Feed(r["publisher"], r["feed"], r["category"], r["language"], r["tier"], r["recommend"], r["region"])) for r in rows]

async def get_articles_for_reprocessing(db: DatabaseInterface):
    #where feed = (select feed from articles  group by feed having count(url) > 100 order by random() limit 1)
    rows = await db.db.query("""
                        SELECT id, url from articles_recent 
                        where feed = (select feed from articles_recent group by feed having count(url) > 100 order by random() limit 1) 
                        order by random() limit 200;
                        """,
                        result=True)
    return [(r["id"], r["url"]) for r in rows]


async def get_articles_for_feed(db: DatabaseInterface, type):
                        #     SELECT id, url, amp_url, image_url, title, summary, publish_date, feed, title_hash, status, text from Articles FROM articles as aa 
                        # left join feeds as f on feed = f.url
                        # where f.language = 'EN' and aa.feed in ('https://www.washingtonexaminer.com/tag/news.rss')
                        # and length(aa.text) > 1500 and aa.text is not null
                        # order by random()
                        # LIMIT 10000
    rows = await db.db.query("""
                        SELECT a.id, url, amp_url, image_url, title, summary, publish_date, feed, title_hash, status, text, e.id as blob_id, text_type, processor
                        from articles_clean as a
                        inner join embeddings_latest as e on a.id = e.article_id and e.text_type = 'Article' and e.processor = $1
                        """, (type,),
                        result=True)
    return ([Article(r["id"], r["url"], r["amp_url"], r["image_url"], r["title"], r["summary"], r["publish_date"], r["feed"], r["title_hash"], r["status"], r["text"]) for r in rows],
            [Embedding(r["blob_id"], r["processor"], r["text_type"], r["id"]) for r in rows])




async def get_articles_clean(db: DatabaseInterface) -> List[Article]:
    rows = await db.db.query("""
                        SELECT id, url, amp_url, image_url, title, summary, publish_date, feed, title_hash, status, text from articles_clean
                        """, 
                        result=True)
    return [Article(**article) for article in rows]
            

async def get_article_html(db: DatabaseInterface, key: str):
    try:
        payload = db.dl.get_json(f"testing/article_html/{key}")
    except:
        return None
    return payload["html"] if "html" in payload else None

async def get_articles_for_reprocessing_id_list(db: DatabaseInterface, ids):
    rows = [(i, "www.example.com") for i in ids]
    article_html = []
    for i, row in enumerate(rows):
        if i % 20 == 0 and i != 0:
            logger.info(f"Loaded {i} from {len(rows)}")
        try:
            jso = db.dl.get_json(f"testing/article_html/{row[0]}")
            article_html.append((*row, jso["html"])) if jso else 0
        except:
            logger.info("Key")
    return article_html


async def save_rss_article(db: DatabaseInterface, article: Article):
    insert_sql = "INSERT INTO Articles (feed, url, title, summary, publish_date, title_hash, status) values ($1, $2, $3, $4, $5, $6, 'CRAWL') ON CONFLICT ON CONSTRAINT articles_url_key DO UPDATE SET title = $3, summary = $4, publish_date = $5, title_hash = $6  RETURNING id, status"
    insert_data = (article.feed, article.url, article.title, article.summary[:5000], datetime.strptime(article.publish_date, "%Y-%m-%d %H:%M:%S"), hash_text(article.title))
    row = (await db.db.query(insert_sql, insert_data, result=True))
    if not len(row):
        a = 1
    row = row[0]
    db.dl.put_json(f"testing/article_rss/{row['id']}", {"rss": {"url": article.url, "title": article.title, "summary": article.summary, "publish_date": article.publish_date}})
    article.id = row["id"]
    article.status = row["status"]
    return article

async def save_html_article(db: DatabaseInterface, article: Article):
    insert_sql = "UPDATE Articles SET amp_url = $1, image_url = $2, storage_key = '', status = $3, title = $4, text = $5, title_hash = $6 WHERE id = $7";
    insert_data = (article.amp_url, article.image_url, article.status, article.title, article.text, hash_text(article.title), article.id)
    await db.db.query(insert_sql, insert_data)


async def save_article(db: DatabaseInterface, markup, html, article: Article):
    db.dl.put_json(f"testing/article_markup/{article.id}", {"markup": markup})
    db.dl.put_json(f"testing/article_html/{article.id}", {"html": html})
    db.dl.put_json(f"testing/article_text/{article.id}", {"text": article.text, "title": article.title})
    await save_html_article(db, article)


async def set_article_status(db: DatabaseInterface, article: Article):
    insert_sql = "UPDATE Articles SET status = $1 WHERE id = $2";
    insert_data = (article.status, article.id)
    await db.db.query(insert_sql, insert_data)

async def refresh_article_materialized_views(db: DatabaseInterface):
    insert_sql = "REFRESH MATERIALIZED VIEW articles_clean"
    await db.db.query(insert_sql)
    insert_sql = "REFRESH MATERIALIZED VIEW articles_recent"
    await db.db.query(insert_sql)




def hash_text(s):
    #clean up before hash
    s_clean = re.compile('[\W_]+').sub('', s)
    return hash(s_clean).to_bytes(8, "big", signed=True).hex()