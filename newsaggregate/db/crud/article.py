from newsaggregate.db.databaseinstance import DatabaseInterface
import json
import re
from newsaggregate.logging import get_logger
logger = get_logger()

from newsaggregate.rss.articleutils import Match

class Article:
    url: str
    amp_url: str
    image_url: str
    title: str
    summary: str
    publish_date: str


def hash_text(s):
    #clean up before hash
    s_clean = re.compile('[\W_]+').sub('', s)
    return hash(s_clean).to_bytes(8, "big", signed=True).hex()

def get_articles(db: DatabaseInterface):
    rows = db.db.query("SELECT url from Articles;", result=True)
    return [t[0] for t in rows]


def get_random_articles(db: DatabaseInterface, limit=2000):
    rows = db.db.query(f"SELECT id, url from Articles where status = 'CRAWL' LIMIT {limit};", result=True)
    return rows

def get_articles_for_reprocessing(db: DatabaseInterface):
    #where feed = (select feed from articles  group by feed having count(url) > 100 order by random() limit 1)
    rows = db.db.query("""
                        SELECT id, url from articles_recent 
                        where feed = (select feed from articles_recent group by feed having count(url) > 100 order by random() limit 1) 
                        order by random() limit 200;
                        """,
                        result=True)
    return rows

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


def save_rss_article(db: DatabaseInterface, rss_feed: str, url: str, title: str, summary: str, publish_date):
    insert_sql = "INSERT INTO Articles (feed, url, title, summary, publish_date, title_hash, status) values (%s, %s, %s, %s, %s, %s, 'CRAWL') ON CONFLICT ON CONSTRAINT articles_url_key DO UPDATE SET title = %s, summary = %s, publish_date = %s, title_hash = %s  RETURNING id, status"
    insert_data = (rss_feed, url, title, summary[:5000], publish_date, hash_text(title), title, summary[:5000], publish_date, hash_text(title))
    id, status = db.db.query(insert_sql, insert_data, result=True)[0]
    return id, status

def save_html_article(db: DatabaseInterface, id: str, amp_url: str, image_url: str, storage_key: str, status: str, title: str, text: str):
    insert_sql = "UPDATE Articles SET amp_url = %s, image_url = %s, storage_key = %s, status = %s, title = %s, text = %s, title_hash = %s WHERE id = %s";
    insert_data = (amp_url, image_url, storage_key, status, title, text, hash_text(title), id)
    db.db.query(insert_sql, insert_data)


def save_article(db: DatabaseInterface, job_id, markup, meta, html, article_text, article_title, status):
    db.dl.put_json(f"testing/article_markup/{job_id}", {"markup": markup})
    db.dl.put_json(f"testing/article_html/{job_id}", {"html": html})
    db.dl.put_json(f"testing/article_text/{job_id}", {"text": article_text, "title": article_title})
    save_html_article(db, job_id, meta["amp_url"], meta["image_url"], "", status, article_title, article_text)

def set_article_status(db: DatabaseInterface, id: str, status: str):
    insert_sql = "UPDATE Articles SET status = %s WHERE id = %s";
    insert_data = (status, id)
    db.db.query(insert_sql, insert_data)

def refresh_article_materialized_views(db: DatabaseInterface):
    insert_sql = "REFRESH MATERIALIZED VIEW articles_clean";
    db.db.query(insert_sql)
    insert_sql = "REFRESH MATERIALIZED VIEW articles_recent";
    db.db.query(insert_sql)


def save_unnecessary_text_pattern(db: DatabaseInterface, url_pattern, match: Match):
    insert_sql = "INSERT INTO UnnecessaryText (url_pattern, tag_name, tag_attrs, tag_identifyable, tag_text) values (%s, %s, %s, %s, %s) ON CONFLICT ON CONSTRAINT unique_constraint DO UPDATE SET tag_identifyable = %s, tag_text = %s"
    insert_data = (url_pattern, match.tag_name, match.tag_attrs, match.tag_identifyable, match.tag_text, match.tag_identifyable, match.tag_text)
    db.db.query(insert_sql, insert_data)

def get_unnecessary_text_pattern(db: DatabaseInterface):
    insert_sql = "SELECT url_pattern, tag_name, tag_attrs, tag_text, tag_identifyable from UnnecessaryText where tag_identifyable = 'TRUE'"
    rows = db.db.query(insert_sql, result=True)
    return rows



