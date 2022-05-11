import traceback
from db.config import ASYNC_POSTGRES_CONNECTION_DETAILS
import asyncpg
import asyncio



from logger import get_logger

logger = get_logger()


class AsyncDatabase:
    connection: asyncpg.Connection = None
    instance = None

    def __init__(self):
        pass

    async def __aenter__(self):
        await self.connect()
        return AsyncDatabase.instance

    async def __aexit__(self, *args):
        """Close Postgres Connection"""
        pass
        #await self.close()

    
    async def __await__(self):
        return self.__aenter__().__await__()

    async def close(self):
        if self.connection is not None and self.connection is not None:
            await self.connection.close()

    def get():
        return AsyncDatabase.instance

    async def connect(self, min_size=10, max_size=10):
        """Connect to Postgres"""
        # if AsyncDatabase.instance:
        #     return
        self.connection: asyncpg.Connection = await asyncpg.create_pool(**ASYNC_POSTGRES_CONNECTION_DETAILS, min_size=min_size, max_size=max_size)
        rows = await self.connection.fetch("SELECT 1;")
        assert len(rows) == 1
        logger.debug(f"POSTGRES CONNECTION UP {self.connection}")
        # AsyncDatabase.instance = self

    async def query(self, sql, data=(), result=False):

        rows = []
        try:
            
            if result:
                rows = await self.connection.fetch(sql, *data)
            else:
                await self.connection.execute(sql)
        # except (InterfaceError, AdminShutdown, OperationalError) as e:
        #     logger.error(sql, data)
        #     logger.error(traceback.format_exc())
        #     logger.error(e.pgcode)
        #     if self.closed != 0:
        #         self.connect()
        #         logger.error("*** RECONNECT ***")
        except Exception as e:
            logger.error(repr(e))
            logger.error(traceback.format_exc())
        finally:
            if result:
                return rows
            return "Saved"
