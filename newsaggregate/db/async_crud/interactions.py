


from typing import List
import numpy as np

from db.async_postgresql import AsyncDatabase
from db.crud.interactions import Read


async def get_read_counts(db: AsyncDatabase) -> np.ndarray:
    read_count = await db.query("select article_id, count(article_id) as read_count from reads group by article_id", result=True)
    return np.array(read_count)


async def get_reads_for_user(db: AsyncDatabase, user_id) -> List[Read]:
    rows = await db.query("select user_id, article_id, start_date, end_date, max_scroll from reads where user_id = $1", (user_id,), result=True)
    return [Read(**read) for read in rows]