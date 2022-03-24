from newsaggregate.db.databaseinstance import DatabaseInterface


def get_feeds(db: DatabaseInterface):
    rows = db.db.query("SELECT url from Feeds limit 2;", result=True)
    return [t[0] for t in rows]


def save_feed_last_crawl(db: DatabaseInterface, feed):
    print("UPDATE TIME")
    db.db.query(f"UPDATE feeds SET last_crawl_date = current_timestamp WHERE url = '{feed}'")

