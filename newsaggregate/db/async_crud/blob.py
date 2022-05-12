



from db.async_postgresql import AsyncDatabase
from db.s3 import Datalake
import asyncio
from concurrent.futures import ThreadPoolExecutor

from db.async_s3 import AsyncDatalake


async def get_similarities(db: AsyncDatabase, dl: AsyncDatalake, type):
    blob_id = (await db.query("select id from similarities where type = $1 order by update_date desc limit 1", (type,), result=True))[0]["id"]
    # loop = asyncio.get_event_loop()
    # with ThreadPoolExecutor() as pool:

    #     blob1 = await loop.run_in_executor(pool, dl.get_obj, f"testing/similarity/{blob_id}")
    #     blob2 = await loop.run_in_executor(pool, dl.get_obj, f"testing/similarity_index/{blob_id}")
    #     return blob1, blob2
    return await dl.get_obj(f"testing/similarity/{blob_id}"), await dl.get_obj(f"testing/similarity_index/{blob_id}")



