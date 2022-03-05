from newsaggregate.db.databaseinstance import DatabaseInterface
import json

class Article:
    url: str
    amp_url: str
    image_url: str
    title: str
    summary: str
    publish_date: str


def hash_text(s):
    return hash(s).to_bytes(8, "big", signed=True).hex()

def get_articles(db: DatabaseInterface):
    rows = db.db.query("SELECT url from Articles;", result=True)
    return [t[0] for t in rows]


def get_random_articles(db: DatabaseInterface, limit=100):
    rows = db.db.query(f"SELECT id, url from Articles where RANDOM() < 0.1 LIMIT {limit};", result=True)
    return rows

def get_articles_for_reprocessing(db: DatabaseInterface):
    rows = db.db.query("SELECT id, url from Articles where RANDOM() < 0.1 LIMIT 10;", result=True)
    print(rows)
    res = []
    for row in rows:
        #print(db.dl.get_json(f"testing/article_html/{row[0]}"))
        jso = db.dl.get_json(f"testing/article_html/{row[0]}")
        if jso:
            res.append(jso["html"])
    return res


def save_rss_article(db: DatabaseInterface, rss_feed: str, url: str, title: str, summary: str, publish_date):
    insert_sql = "INSERT INTO Articles (feed, url, title, summary, publish_date, title_hash) values (%s, %s, %s, %s, %s, %s) ON CONFLICT ON CONSTRAINT articles_url_key DO UPDATE SET title = %s, summary = %s, publish_date = %s, title_hash = %s  RETURNING id"
    insert_data = (rss_feed, url, title, summary[:5000], publish_date, hash_text(title), title, summary[:5000], publish_date, hash_text(title))
    id = db.db.query(insert_sql, insert_data, result=True)[0][0]
    return id

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

def refresh_articles_clean(db: DatabaseInterface):
    insert_sql = "REFRESH MATERIALIZED VIEW articles_clean";
    db.db.query(insert_sql)


def save_unnecessary_text(db: DatabaseInterface, url_pattern, tag_name, tag_attrs, tag_text):
    insert_sql = "INSERT INTO UnnecessaryText (url_pattern, tag_name, tag_attrs, tag_text) values (%s, %s, %s, %s)"
    insert_data = (url_pattern, tag_name, tag_attrs, tag_text)
    db.db.query(insert_sql, insert_data)



