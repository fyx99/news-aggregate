import traceback, json
from aiobotocore.session import AioSession, get_session
from logger import get_logger

logger = get_logger()

secret = {
    "access_key_id": "AKIAQT4HBU75VQSE6IET",
    "bucket": "hcp-1a9ec634-dfdf-40cd-8a08-d40904f2d00e",
    "host": "s3-eu-central-1.amazonaws.com",
    "region": "eu-central-1",
    "secret_access_key": "Gv60dgVPFwsJb7sycb2DaOqMASK+3K26BzrPq/3k",
    "uri": "s3://AKIAQT4HBU75VQSE6IET:Gv60dgVPFwsJb7sycb2DaOqMASK%2B3K26BzrPq%2F3k@s3-eu-central-1.amazonaws.com/hcp-1a9ec634-dfdf-40cd-8a08-d40904f2d00e",
    "username": "hcp-s3-d0043d7c-fdf5-40de-894c-a8987ae03d4f",
}

from contextlib import AsyncExitStack

class AsyncDatalake:
    connection = None
    bucket = ""

    def __init__(self) -> None:
        self._exit_stack = AsyncExitStack()

    async def connect(self):
        """Connect to S3"""
        try:

            s3key = secret

            session = AioSession()
            self.connection = await self._exit_stack.enter_async_context(
                session.create_client(
                    "s3",
                    aws_access_key_id=s3key["access_key_id"],
                    aws_secret_access_key=s3key["secret_access_key"],
                    region_name=s3key["region"],
                )
            )


            self.bucket = s3key["bucket"]
            logger.debug(f"S3 CONNECTION UP {self.connection}")

        except Exception as e:
            logger.error("*** CONNECTION PROBLEM " + repr(e))

    async def close(self):
        await self._exit_stack.__aexit__(None, None, None)

    async def put_obj(self, path, obj=()):
        # query db with reconnect error handling
        try:
            await self.connection.put_object(Body=obj, Bucket=self.bucket, Key=path)

        except Exception as e:
            logger.error(traceback.format_exc())

    async def get_obj(self, path):

        response = await self.connection.get_object(Bucket=self.bucket, Key=path)
        # this will ensure the connection is correctly re-used/closed

        try:
            return await response["Body"].read()
        except:
            logger.error(traceback.format_exc())
        return {}


# import asyncio


# async def go():
#     dl = AsyncDatalake()
#     await dl.connect()
#     await dl.put_obj("test7.txt", "test5")
#     print(await dl.get_obj("test7.txt"))
#     await dl.close()


# loop = asyncio.get_event_loop()
# loop.run_until_complete(go())