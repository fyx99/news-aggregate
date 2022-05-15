import unittest
from db.async_postgresql import AsyncDatabase
from test.custom_testcase import CustomTestcase


class TestPostgres(CustomTestcase):

    async def test_connection(self: unittest.IsolatedAsyncioTestCase):
        db = AsyncDatabase()
        await db.connect()
        self.assertIsNotNone(db.connection)
        await db.close()
        self.assertTrue(db.connection._closed)


    async def test_select(self: unittest.IsolatedAsyncioTestCase):
        db = AsyncDatabase()
        await db.connect()

        res = await db.query("SELECT 4 as TEST;", result=True)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["test"], 4)

        res = await db.query("SELECT 4 as TEST;", result=True)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0][0], 4)

if __name__ =="__main__":
    import asyncio
    asyncio.get_event_loop().run_until_complete(TestPostgres().test_select())
