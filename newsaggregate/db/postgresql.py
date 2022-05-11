import psycopg2
from psycopg2 import sql, InterfaceError
import traceback
from db.config import POSTGRES_CONNECTION_DETAILS
from psycopg2.errors import UniqueViolation, AdminShutdown, OperationalError
import psycopg2.extras

from logger import get_logger

logger = get_logger()


class Database:
    connection = None
    instance = None

    def __init__(self):
        self.connect()
        Database.instance = self

    def __enter__(self):
        return self

    def __exit__(self,  *args):
        """Close Postgres Connection"""
        self.close()

    def close(self):
        if self.connection is not None and self.connection is not None:
            self.connection.close()

    def get():
        return Database.instance

    def connect(self):
        """Connect to Postgres"""
        self.connection = psycopg2.connect(**POSTGRES_CONNECTION_DETAILS)
        self.connection.set_isolation_level(
            psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT
        )
        cursor = self.connection.cursor()
        cursor.execute("select 1;")
        rows = cursor.fetchall()
        cursor.close()
        assert str(rows) == "[(1,)]"
        logger.debug(f"POSTGRES CONNECTION UP {self.connection}")

        # logger.info("*** Connection Problem " + repr(e))

    def query(self, sql, data=(), result=False, raw=False):
        # query db with reconnect error handling
        # logger.info("Query: " + str(sql)[0:100] + " ... " + str(len(str(sql))))
        rows = []
        try:
            options = {} if raw else {"cursor_factory": psycopg2.extras.RealDictCursor}
            cursor = self.connection.cursor(**options)
            cursor.execute(sql, data)
            if result:
                rows = cursor.fetchall()
            cursor.close()
        except (InterfaceError, AdminShutdown, OperationalError) as e:
            logger.error(sql, data)
            logger.error(traceback.format_exc())
            logger.error(e.pgcode)
            if self.closed != 0:
                self.connect()
                logger.error("*** RECONNECT ***")
        except Exception as e:
            logger.error(repr(e))
            logger.error(traceback.format_exc())
        finally:
            if result:
                return rows
            return "Saved"
