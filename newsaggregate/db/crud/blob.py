import psycopg2
from db.databaseinstance import DatabaseInterface
from dataclasses import dataclass

from logger import get_logger
from feature.numpy_utils import npy_to_numpy_array, numpy_array_as_npy
logger = get_logger()

@dataclass
class Embedding:
    id: str = ""
    processor: str = ""
    text_type: str = ""
    article_id: str = ""
    blob: any = None


def save_similarities(db: DatabaseInterface, similarity_data, index_data, type):
    similarity_blob = numpy_array_as_npy(similarity_data)
    index_blob = numpy_array_as_npy(index_data)
    blob_id = db.db.query("insert into similarities (id, type) values (nextval('blob_id'), %s) returning id", (type,), result=True)[0]["id"]
    db.dl.put_obj(f"testing/similarity/{blob_id}", similarity_blob)
    db.dl.put_obj(f"testing/similarity_index/{blob_id}", index_blob)
    logger.info(f"SAVED SIMILARITY MATRIX {blob_id}")


def get_similarities(db: DatabaseInterface, type):
    blob_id = db.db.query("select id from similarities where type = %s order by update_date desc limit 1", (type,), result=True)[0]["id"]
    return npy_to_numpy_array(db.dl.get_obj(f"testing/similarity/{blob_id}")), npy_to_numpy_array(db.dl.get_obj(f"testing/similarity_index/{blob_id}"))
    

def save_embeddings(db: DatabaseInterface, embedding, processor, text_type, article_id):
    blob = numpy_array_as_npy(embedding)
    blob_id = db.db.query("""insert into embeddings (id, processor, text_type, article_id, blob) values (nextval('blob_id'), %s, %s, %s, %s) 
            ON CONFLICT ON CONSTRAINT processor_text_type_article DO UPDATE SET blob = %s, update_date = CURRENT_TIMESTAMP
            returning id""", 
        (processor, text_type, article_id, psycopg2.Binary(blob), psycopg2.Binary(blob)), result=True)[0]["id"]
    db.dl.put_obj(f"testing/embedding/{blob_id}", blob)


def get_embeddings(db: DatabaseInterface, processor, text_type, article_id):
    blob = db.db.query("select blob from embeddings where processor = %s and text_type = %s and article_id = %s limit 1", (processor, text_type, article_id), result=True)[0]["blob"]
    return npy_to_numpy_array(blob)

def get_embedding_by_id(db: DatabaseInterface, blob_id):
    logger.info(f"Load {blob_id}")
    blob = db.db.query("select id, blob from embeddings where id = %s", (blob_id,), result=True)[0]["blob"]
    return npy_to_numpy_array(blob)