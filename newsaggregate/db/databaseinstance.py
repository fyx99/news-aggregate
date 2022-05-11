from db.async_postgresql import AsyncDatabase
from db.rabbit import MessageBroker
from db.s3 import Datalake
from db.http import Http


class DatabaseInterface:
    db: AsyncDatabase
    dl: Datalake
    rb: MessageBroker

    def __init__(self, db: AsyncDatabase=None, dl: Datalake=None, rb: MessageBroker=None, http: Http=None) -> None:
        self.db = db
        self.dl = dl
        self.rb = rb
        self.http = http