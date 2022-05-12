from typing import List
from db.databaseinstance import DatabaseInterface
import numpy as np
from dataclasses import dataclass

from logger import get_logger
logger = get_logger()

@dataclass
class Impression:
    user_id: str = ""
    article_id: str = ""
    start_date: str = ""
    end_date: str = ""
    rank: str = ""
    
@dataclass
class Read:
    user_id: str = ""
    article_id: str = ""
    start_date: str = ""
    end_date: str = ""
    max_scroll: str = ""

@dataclass
class Preference:
    user_id: str = ""
    feed_url: str = ""
    weight: str = ""
    type: str = ""


@dataclass
class ReadCount:
    article_id: str = ""
    count: int = 0


def get_reads_for_user(db: DatabaseInterface, user_id) -> List[Read]:
    rows = db.db.query("select user_id, article_id, start_date, end_date, max_scroll from reads where user_id = %s", (user_id,), result=True)
    return [Read(**read) for read in rows]


def get_impressions(db: DatabaseInterface, user_id) -> List[Impression]:
    rows = db.db.query("select user_id, article_id, start_date, end_date, rank from impressions where user_id = %s", (user_id,), result=True)
    return [Impression(**impression) for impression in rows]
    

def get_read_counts(db: DatabaseInterface) -> np.ndarray:
    read_count = db.db.query("select article_id, count(article_id) as read_count from reads group by article_id", result=True, raw=True)
    return np.array(read_count)
