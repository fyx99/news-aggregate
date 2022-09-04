from typing import List
from db import BaseDataClass
from db.crud.blob import Embedding
from db.crud.feeds import Feed
from db.databaseinstance import DatabaseInterface
from dataclasses import dataclass
import re
from logger import get_logger
from feature.numpy_utils import npy_to_numpy_array
logger = get_logger()




@dataclass
class Article(BaseDataClass):
    id: str = ""
    url: str = ""
    amp_url: str = ""
    image_url: str = ""
    title: str = ""
    summary: str = ""
    publish_date: any = ""
    update_date: any = ""
    feed: str = ""
    title_hash: str = ""
    status: str = ""
    text: str = ""
    publisher: str = ""
    icon_url: str = "" 
 
@dataclass
class FeedArticle(Article):
    rank: int = 0
    feed_id: str = ""


def get_articles(db: DatabaseInterface):
    rows = db.db.query("SELECT id, url, amp_url, image_url, title, summary, update_date, feed, title_hash, status, text from Articles;", result=True)
    return [Article(**r) for r in rows]

def get_article(db: DatabaseInterface, id):
    row = db.db.query("SELECT id, url, amp_url, image_url, title, summary, update_date, feed, title_hash, status, text from Articles where id = %s;", (id,), result=True)[0]
    return Article(**row)


def get_random_articles(db: DatabaseInterface, limit=200):
    rows = db.db.query(f"SELECT id, a.url, amp_url, image_url, a.title, summary, update_date, feed, title_hash, status, text, publisher, language, recommend, category, tier, region from Articles as a left join Feeds as f on f.url = feed limit {limit};", result=True)
    return [(Article(r["id"], r["url"], r["amp_url"], r["image_url"], r["title"], r["summary"], r["update_date"], r["feed"], r["title_hash"], r["status"], r["text"], ""), 
        Feed(r["publisher"], r["feed"], r["category"], r["language"], r["tier"], r["recommend"], r["region"])) for r in rows]

def get_articles_for_reprocessing(db: DatabaseInterface):
    #where feed = (select feed from articles  group by feed having count(url) > 100 order by random() limit 1)
    #(select feed from articles_recent group by feed having count(url) > 100 order by random() limit 1) 
    #db.db.query("""select setseed(0.8);""")
    rows = db.db.query("""
                        SELECT id, url from articles_recent 
                        where feed = (select feed from articles_recent group by feed having count(url) > 100 order by random() limit 1)
                        order by random() limit 30;
                        """,
                        result=True)
    return [(r["id"], r["url"]) for r in rows]


def get_articles_for_feed(db: DatabaseInterface, type, limit=None):
    
                        #     SELECT id, url, amp_url, image_url, title, summary, update_date, feed, title_hash, status, text from Articles FROM articles as aa 
                        # left join feeds as f on feed = f.url
                        # where f.language = 'EN' and aa.feed in ('https://www.washingtonexaminer.com/tag/news.rss')
                        # and length(aa.text) > 1500 and aa.text is not null
                        # order by random()
                        # LIMIT 10000
    rows = db.db.query("""
                        SELECT a.id, url, amp_url, image_url, title, summary, a.update_date, feed, title_hash, status, text, publisher, e.id as blob_id, text_type, processor, blob
                        from articles_clean as a
                        inner join embeddings as e on a.id = e.article_id and e.text_type = 'Article' and e.processor = %s where blob is not Null limit %s
                        """, (type, limit or 5000),
                        result=True)
    return ([Article(r["id"], r["url"], r["amp_url"], r["image_url"], r["title"], r["summary"], r["update_date"], r["feed"], r["title_hash"], r["status"], r["text"], r["publisher"]) for r in rows],
            [Embedding(r["blob_id"], r["processor"], r["text_type"], r["id"], npy_to_numpy_array(r["blob"])) for r in rows])




def get_articles_clean(db: DatabaseInterface) -> List[Article]:
    rows = db.db.query("""
                        SELECT id, url, amp_url, image_url, title, summary, update_date, feed, title_hash, status, text, publisher from articles_clean
                        """, 
                        result=True)
    return [Article(**article) for article in rows]



def get_articles_clean_language(db: DatabaseInterface, language) -> List[Article]:
    rows = db.db.query("""
                        SELECT id, c.url, amp_url, image_url, c.title, summary, update_date, feed, title_hash, status, text from articles_clean as c inner join feeds as f on f.url = feed and f.language = %s
                        """, (language,),
                        result=True)
    return [Article(**article) for article in rows]
            

def get_article_html(db: DatabaseInterface, key: str):
    try:
        payload = db.dl.get_json(f"testing/article_html/{key}")
    except:
        return None
    return payload.get("html", None)

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


def save_rss_article(db: DatabaseInterface, article: FeedArticle):
    insert_sql = "INSERT INTO Articles (feed, url, title, summary, publish_date, title_hash, status) values (%s, %s, %s, %s, %s, %s, 'CRAWL') ON CONFLICT ON CONSTRAINT articles_url_key DO UPDATE SET title = %s, summary = %s, title_hash = %s  RETURNING id, status"
    insert_data = (article.feed, article.url, article.title[:1000], article.summary[:50000], article.publish_date, hash_text(article.title), 
        article.title, article.summary[:5000], hash_text(article.title))
    row = db.db.query(insert_sql, insert_data, result=True)[0]
    db.dl.put_json(f"testing/article_rss/{row['id']}", {"rss": {"url": article.url, "title": article.title, "summary": article.summary, "update_date": article.update_date}})
    article.id = row["id"]
    article.status = row["status"]

    #insert feedlog
    insert_sql = "INSERT INTO Feedlogs (feed_id, rank, article_id) values (%s, %s, %s) ON CONFLICT ON CONSTRAINT feedlogs_feed_rank_article DO NOTHING"
    db.db.query(insert_sql, (article.feed_id, article.rank, article.id))

    return article

def save_html_article(db: DatabaseInterface, article: Article):
    insert_sql = "UPDATE Articles SET amp_url = %s, image_url = %s, storage_key = '', status = %s, title = %s, text = %s, title_hash = %s WHERE id = %s";
    insert_data = (article.amp_url, article.image_url, article.status, article.title[:1000], article.text[:300000], hash_text(article.title), article.id)
    db.db.query(insert_sql, insert_data)

def save_html_keywords(db: DatabaseInterface, article: Article, keywords):
    #insert keywords
    insert_sql = "INSERT INTO Keywords (article_id, keyword) values (%s, %s) ON CONFLICT ON CONSTRAINT keywords_unique DO NOTHING"
    [db.db.query(insert_sql, (article.id, kw)) for kw in keywords]


def save_article(db: DatabaseInterface, article: Article, markup, html, keywords):
    db.dl.put_json(f"testing/article_markup/{article.id}", {"markup": markup})
    db.dl.put_json(f"testing/article_html/{article.id}", {"html": html})
    db.dl.put_json(f"testing/article_text/{article.id}", {"text": article.text, "title": article.title})
    save_html_article(db, article)
    save_html_keywords(db, article, keywords)


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