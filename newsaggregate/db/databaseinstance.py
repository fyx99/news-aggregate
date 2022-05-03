from newsaggregate.db.postgresql import Database
from newsaggregate.message.rabbit import MessageBroker
from newsaggregate.storage.s3 import Datalake


class DatabaseInterface:
    db: Database
    dl: Datalake
    rb: MessageBroker

    def __init__(self, db: Database=None, dl: Datalake=None, rb: MessageBroker=None) -> None:
        self.db = db
        self.dl = dl
        self.rb = rb