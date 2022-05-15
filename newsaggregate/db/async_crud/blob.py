from db.async_postgresql import AsyncDatabase

from db.async_s3 import AsyncDatalake
from feature.numpy_utils import npy_to_numpy_array


async def get_similarities(db: AsyncDatabase, dl: AsyncDatalake, type):
    rows = await db.query("select id from similarities where type = $1 order by update_date desc limit 1", (type,), result=True)
    if not len(rows):
        raise IndexError("NO SIMILARITIES FOR TYPE")
    blob_id = rows[0]["id"]
    # loop = asyncio.get_event_loop()
    # with ThreadPoolExecutor() as pool:

    #     blob1 = await loop.run_in_executor(pool, dl.get_obj, f"testing/similarity/{blob_id}")
    #     blob2 = await loop.run_in_executor(pool, dl.get_obj, f"testing/similarity_index/{blob_id}")
    #     return blob1, blob2
    return  npy_to_numpy_array(await dl.get_obj(f"testing/similarity/{blob_id}")),  npy_to_numpy_array(await dl.get_obj(f"testing/similarity_index/{blob_id}"))



