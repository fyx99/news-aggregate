from db.databaseinstance import DatabaseInterface
from dataclasses import dataclass

from logger import get_logger
logger = get_logger()

@dataclass
class Embedding:
    id: str = ""
    processor: str = ""
    text_type: str = ""
    article_id: str = ""

    async def load(self, db):
        return get_embedding_by_id(db, self.id)

async def save_similarities(db: DatabaseInterface, similarity_data, index_data, type):
    blob_id = (await db.db.query("insert into similarities (id, type) values (nextval('blob_id'), $1) returning id", (type,), result=True))[0]["id"]
    db.dl.put_obj(f"testing/similarity/{blob_id}", similarity_data)
    db.dl.put_obj(f"testing/similarity_index/{blob_id}", index_data)
    logger.info(f"SAVED SIMILARITY MATRIX {blob_id}")


async def get_similarities(db: DatabaseInterface, type):
    blob_id = (await db.db.query("select id from similarities where type = $1 order by update_date desc limit 1", (type,), result=True))[0]["id"]
    return db.dl.get_obj(f"testing/similarity/{blob_id}"), db.dl.get_obj(f"testing/similarity_index/{blob_id}")
    

async def save_embeddings(db: DatabaseInterface, blob, processor, text_type, article_id):
    blob_id = (await db.db.query("insert into embeddings (id, processor, text_type, article_id) values (nextval('blob_id'), $1, $2, $3) returning id", (processor, text_type, article_id), result=True))[0]["id"]
    db.dl.put_obj(f"testing/embedding/{blob_id}", blob)


async def get_embeddings(db: DatabaseInterface, processor, text_type, article_id):
    blob_id = (await db.db.query("select id from embeddings where processor = $1 and text_type = $2 and article_id = $3 order by update_date desc limit 1", (processor, text_type, article_id), result=True))[0]["id"]
    return db.dl.get_obj(f"testing/embedding/{blob_id}")

async def get_embedding_by_id(db: DatabaseInterface, blob_id):
    return db.dl.get_obj(f"testing/embedding/{blob_id}")
