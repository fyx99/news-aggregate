from db.postgresql import Database
from db.rabbit import MessageBroker
from db.s3 import Datalake


class DatabaseInterface:
    db: Database
    dl: Datalake
    rb: MessageBroker

    def __init__(self, db: Database=None, dl: Datalake=None, rb: MessageBroker=None) -> None:
        self.db = db
        self.dl = dl
        self.rb = rb