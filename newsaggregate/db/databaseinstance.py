from newsaggregate.db.postgresql import Database
from newsaggregate.storage.s3 import Datalake


class DatabaseInterface:
    db: Database
    dl: Datalake

    def __init__(self, db: Database, dl: Datalake) -> None:
        self.db = db
        self. dl = dl