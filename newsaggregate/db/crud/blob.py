from newsaggregate.db.databaseinstance import DatabaseInterface

from newsaggregate.logging import get_logger
logger = get_logger()


def save_similarities(db: DatabaseInterface, similarity_data, index_data, type):
    blob_id = db.db.query("insert into similarities (id, type) values (nextval('blob_id'), %s) returning id", (type,), result=True)[0]["id"]
    db.dl.put_obj(f"testing/similarity/{blob_id}", similarity_data)
    db.dl.put_obj(f"testing/similarity_index/{blob_id}", index_data)


def get_similarities(db: DatabaseInterface, type):
    blob_id = db.db.query("select id from similarities where type = %s order by update_date desc limit 1", (type,), result=True)[0]["id"]
    return db.dl.get_obj(f"testing/similarity/{blob_id}"), db.dl.get_obj(f"testing/similarity/{blob_id}")

def save_embeddings(db: DatabaseInterface, blob, processor, text_type, article_id):
    blob_id = db.db.query("insert into embeddings (id, processor, text_type, article_id) values (nextval('blob_id'), %s, %s, %s) returning id", (processor, text_type, article_id), result=True)[0]["id"]
    db.dl.put_obj(f"testing/embedding/{blob_id}", blob)


def get_embeddings(db: DatabaseInterface, processor, text_type, article_id):
    blob_id = db.db.query("select id from embeddings where processor = %s and text_type = %s and article_id = %s order by update_date desc limit 1", (processor, text_type, article_id), result=True)[0]["id"]
    return db.dl.get_obj(f"testing/embedding/{blob_id}")
