import unittest
from db.databaseinstance import DatabaseInterface
from db.postgresql import Database
from test import CustomTestcase


class TestPostgres(CustomTestcase):

    def test_connection(self: unittest.TestCase):
        with Database() as db:
            di = DatabaseInterface(db, None, None)
            self.assertIsNotNone(di.db)


    def test_select(self: unittest.TestCase):
        with Database() as db:
            db = DatabaseInterface(db, None, None)

            res = await db.db.query("SELECT 4 as TEST;", result=True)
            self.assertEqual(len(res), 1)
            self.assertEqual(res[0]["test"], 4)

            res = await db.db.query("SELECT 4 as TEST;", result=True, raw=True)
            self.assertEqual(len(res), 1)
            self.assertEqual(res[0][0], 4)

if __name__ =="__main__":
    TestPostgres().test_select()