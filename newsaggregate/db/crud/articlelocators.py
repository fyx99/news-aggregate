from typing import List
from db.databaseinstance import DatabaseInterface
from dataclasses import dataclass
import json

from logger import get_logger
logger = get_logger()

@dataclass       
class ArticleLocator:
    tag_name: str = ""
    tag_attrs: any = ""
    url_pattern: str  = ""


def get_article_locators(db: DatabaseInterface) -> List[ArticleLocator]:
    insert_sql = "SELECT url_pattern, tag_name, tag_attrs from ArticleLocators"
    rows = db.db.query(insert_sql, result=True)
    patterns = []
    for pattern in rows:
        try:
            loaded_pattern = json.loads(pattern["tag_attrs"])
            patterns.append(ArticleLocator(**{**pattern, "tag_attrs": loaded_pattern}))
        except:
            logger.debug(f"""FAILED LOADING PATTERN {pattern["tag_attrs"]}""")
    return patterns
