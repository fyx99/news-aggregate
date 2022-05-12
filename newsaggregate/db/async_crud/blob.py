



from db.async_postgresql import AsyncDatabase
from db.s3 import Datalake


async def get_similarities(db: AsyncDatabase, dl: Datalake, type):
    blob_id = (await db.query("select id from similarities where type = $1 order by update_date desc limit 1", (type,), result=True))[0]["id"]
    return dl.get_obj(f"testing/similarity/{blob_id}"), dl.get_obj(f"testing/similarity_index/{blob_id}")
    