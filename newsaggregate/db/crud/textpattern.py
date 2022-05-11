from db.databaseinstance import DatabaseInterface
from dataclasses import dataclass


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

async def save_unnecessary_text_pattern(db: DatabaseInterface, match: Match):
    insert_sql = "INSERT INTO UnnecessaryText (url_pattern, tag_name, tag_attrs, tag_identifyable, tag_text) values ($1, $2, $3, $4, $5) ON CONFLICT ON CONSTRAINT unique_constraint DO UPDATE SET tag_identifyable = $4, tag_text = $5"
    insert_data = (match.url_pattern, match.tag_name, match.tag_attrs, match.tag_identifyable, match.tag_text)
    await db.db.query(insert_sql, insert_data)

async def get_unnecessary_text_pattern(db: DatabaseInterface):
    insert_sql = "SELECT url_pattern, tag_name, tag_attrs, tag_text, tag_identifyable from UnnecessaryText where tag_identifyable = 'TRUE'"
    rows = await db.db.query(insert_sql, result=True)
    return [Match(**r) for r in rows]
