from logger import get_logger
from db.postgresql import Database
from db.s3 import Datalake

logger = get_logger()


from db.databaseinstance import DatabaseInterface


def delete_old_embeddings(db: DatabaseInterface):
    logger.info(f"START DELETE OLD EMBEDDINGS")
    db.db.query(
        "delete from embeddings where update_date > current_timestamp - INTERVAL '30' DAY"
    )
    logger.info(f"DELETED OLD EMBEDDINGS")


def move_old_articles(db: DatabaseInterface):
    logger.info(f"START MOVE OLD ARTICLES")
    rows = db.db.query(
        """select id, url, amp_url, image_url, title, summary,
            to_char(publish_date, 'YYYY-MM-DD"T"HH24:MI:SS"Z"') as publish_date, to_char(update_date, 'YYYY-MM-DD"T"HH24:MI:SS"Z"') as update_date, feed, title_hash, status, text 
            from articles where update_date < current_timestamp - INTERVAL '100' DAY limit 10000""",
        raw=True,
        result=True,
    )

    for row in rows:
 
        db.dl.put_json(f"testing/article_archive/{row[0]}", {"article": row})
        db.db.query("insert into archive (id, type) values (%s, 'ARTICLE')", (row[0],))
        db.db.query("delete from articles where id = %s", (row[0],))
    
    logger.info(f"BATCH OF {len(rows)} OLD ARTICLES MOVED")


def main():
    with Database() as db, Datalake() as dl:
        di = DatabaseInterface(db, dl)

        #delete_old_embeddings(di)
        move_old_articles(di)

    return


if __name__ == "__main__":
    main()