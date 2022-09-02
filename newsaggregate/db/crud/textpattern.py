from typing import List
from db.databaseinstance import DatabaseInterface
from dataclasses import dataclass
import json

from logger import get_logger
logger = get_logger()

@dataclass       
class Match:
    tag_name: str = ""
    tag_attrs: any = ""
    tag_text: str = ""
    tag_xpath: str = ""
    tag_identifyable: str = ""
    url_pattern: str  = ""

    def __eq__(self, other):
        return self.tag_name == other.tag_name and self.tag_attrs == other.tag_attrs
    def __hash__(self):
        return hash(self.tag_name + self.tag_attrs)
    def __repr__(self) -> str:
        return f"{self.tag_name} {self.tag_attrs} {self.tag_xpath} {self.tag_identifyable}"

def save_unnecessary_text_pattern(db: DatabaseInterface, match: Match):
    insert_sql = "INSERT INTO UnnecessaryText (url_pattern, tag_name, tag_attrs, tag_identifyable, tag_text) values (%s, %s, %s, %s, %s) ON CONFLICT ON CONSTRAINT unique_constraint DO UPDATE SET tag_identifyable = %s, tag_text = %s"
    insert_data = (match.url_pattern, match.tag_name, match.tag_attrs, match.tag_identifyable, match.tag_text, match.tag_identifyable, match.tag_text)
    db.db.query(insert_sql, insert_data)

def get_unnecessary_text_pattern(db: DatabaseInterface) -> List[Match]:
    insert_sql = "SELECT url_pattern, tag_name, tag_attrs, tag_text, tag_identifyable from UnnecessaryText where tag_identifyable = 'TRUE'"
    rows = db.db.query(insert_sql, result=True)
    patterns = []
    for pattern in rows:
        try:
            loaded_pattern = json.loads(pattern["tag_attrs"])
            patterns.append(Match(**{**pattern, "tag_attrs": loaded_pattern}))
        except:
            logger.debug(f"""FAILED LOADING PATTERN {pattern["tag_attrs"]}""")
    return patterns
