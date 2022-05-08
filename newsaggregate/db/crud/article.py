from typing import List
from db import BaseDataClass
from db.crud.blob import Embedding
from db.crud.feeds import Feed
from db.databaseinstance import DatabaseInterface
from dataclasses import dataclass
import re
from logger import get_logger
logger = get_logger()




@dataclass
class Article(BaseDataClass):
    id: str = ""
    url: str = ""
    amp_url: str = ""
    image_url: str = ""
    title: str = ""
    summary: str = ""
    publish_date: str = ""
    feed: str = ""
    title_hash: str = ""
    status: str = ""
    text: str = ""

        

    def article_from_entry(entry, feed):
        return Article(title=entry.title, url=entry.link, summary=entry.summary, publish_date=entry.published_parsed, feed=feed)


def get_articles(db: DatabaseInterface):
    rows = db.db.query("SELECT id, url, amp_url, image_url, title, summary, publish_date, feed, title_hash, status, text from Articles;", result=True)
    return [Article(**r) for r in rows]

def get_article(db: DatabaseInterface, id):
    row = db.db.query("SELECT id, url, amp_url, image_url, title, summary, publish_date, feed, title_hash, status, text from Articles where id = %s;", (id,), result=True)[0]
    return Article(**row)


def get_random_articles(db: DatabaseInterface, limit=200):
    rows = db.db.query(f"SELECT id, a.url, amp_url, image_url, a.title, summary, publish_date, feed, title_hash, status, text, publisher, language, recommend, category, tier, region from Articles as a left join Feeds as f on f.url = feed limit {limit};", result=True)
    return [(Article(r["id"], r["url"], r["amp_url"], r["image_url"], r["title"], r["summary"], r["publish_date"], r["feed"], r["title_hash"], r["status"], r["text"]), 
        Feed(r["publisher"], r["feed"], r["category"], r["language"], r["tier"], r["recommend"], r["region"])) for r in rows]

def get_articles_for_reprocessing(db: DatabaseInterface):
    #where feed = (select feed from articles  group by feed having count(url) > 100 order by random() limit 1)
    rows = db.db.query("""
                        SELECT id, url from articles_recent 
                        where feed = (select feed from articles_recent group by feed having count(url) > 100 order by random() limit 1) 
                        order by random() limit 200;
                        """,
                        result=True)
    return [(r["id"], r["url"]) for r in rows]


def get_articles_for_feed(db: DatabaseInterface, type):
                        #     SELECT id, url, amp_url, image_url, title, summary, publish_date, feed, title_hash, status, text from Articles FROM articles as aa 
                        # left join feeds as f on feed = f.url
                        # where f.language = 'EN' and aa.feed in ('https://www.washingtonexaminer.com/tag/news.rss')
                        # and length(aa.text) > 1500 and aa.text is not null
                        # order by random()
                        # LIMIT 10000
    rows = db.db.query("""
                        SELECT a.id, url, amp_url, image_url, title, summary, publish_date, feed, title_hash, status, text, e.id as blob_id, text_type, processor
                        from articles_clean as a
                        inner join embeddings_latest as e on a.id = e.article_id and e.text_type = 'Article' and e.processor = %s
                        """, (type,),
                        result=True)
    return ([Article(r["id"], r["url"], r["amp_url"], r["image_url"], r["title"], r["summary"], r["publish_date"], r["feed"], r["title_hash"], r["status"], r["text"]) for r in rows],
            [Embedding(r["blob_id"], r["processor"], r["text_type"], r["id"]) for r in rows])




def get_articles_clean(db: DatabaseInterface) -> List[Article]:
    rows = db.db.query("""
                        SELECT id, url, amp_url, image_url, title, summary, publish_date, feed, title_hash, status, text from articles_clean
                        """, 
                        result=True)
    return [Article(**article) for article in rows]
            

def get_article_html(db: DatabaseInterface, key: str):
    try:
        payload = db.dl.get_json(f"testing/article_html/{key}")
    except:
        return None
    return payload["html"] if "html" in payload else None

def get_articles_for_reprocessing_id_list(db: DatabaseInterface, ids):
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


def save_rss_article(db: DatabaseInterface, article: Article):
    insert_sql = "INSERT INTO Articles (feed, url, title, summary, publish_date, title_hash, status) values (%s, %s, %s, %s, %s, %s, 'CRAWL') ON CONFLICT ON CONSTRAINT articles_url_key DO UPDATE SET title = %s, summary = %s, publish_date = %s, title_hash = %s  RETURNING id, status"
    insert_data = (article.feed, article.url, article.title, article.summary[:5000], article.publish_date, hash_text(article.title), 
        article.title, article.summary[:5000], article.publish_date, hash_text(article.title))
    row = db.db.query(insert_sql, insert_data, result=True)[0]
    db.dl.put_json(f"testing/article_rss/{row['id']}", {"rss": {"url": article.url, "title": article.title, "summary": article.summary, "publish_date": article.publish_date}})
    article.id = row["id"]
    article.status = row["status"]
    return article

def save_html_article(db: DatabaseInterface, article: Article):
    insert_sql = "UPDATE Articles SET amp_url = %s, image_url = %s, storage_key = '', status = %s, title = %s, text = %s, title_hash = %s WHERE id = %s";
    insert_data = (article.amp_url, article.image_url, article.status, article.title, article.text, hash_text(article.title), article.id)
    db.db.query(insert_sql, insert_data)


def save_article(db: DatabaseInterface, markup, html, article: Article):
    db.dl.put_json(f"testing/article_markup/{article.id}", {"markup": markup})
    db.dl.put_json(f"testing/article_html/{article.id}", {"html": html})
    db.dl.put_json(f"testing/article_text/{article.id}", {"text": article.text, "title": article.title})
    save_html_article(db, article)


def set_article_status(db: DatabaseInterface, article: Article):
    insert_sql = "UPDATE Articles SET status = %s WHERE id = %s";
    insert_data = (article.status, article.id)
    db.db.query(insert_sql, insert_data)

def refresh_article_materialized_views(db: DatabaseInterface):
    insert_sql = "REFRESH MATERIALIZED VIEW articles_clean"
    db.db.query(insert_sql)
    insert_sql = "REFRESH MATERIALIZED VIEW articles_recent"
    db.db.query(insert_sql)








# def get_fields_to_dict(data, names):
#     if isinstance(data, list):
#         return [{
#             name: row[name] for name in names
#         } for row in data]
#     return { name: data[name] for name in names }

def hash_text(s):
    #clean up before hash
    s_clean = re.compile('[\W_]+').sub('', s)
    return hash(s_clean).to_bytes(8, "big", signed=True).hex()