import unittest
from db.databaseinstance import DatabaseInterface
from db.s3 import Datalake
from test import CustomTestcase


class TestS3(CustomTestcase):

    def test_connection(self: unittest.TestCase):
        with Datalake() as dl:
            di = DatabaseInterface(None, dl, None)
            self.assertIsNotNone(di.dl)


    def test_get(self: unittest.TestCase):
        with Datalake() as dl:
            di = DatabaseInterface(None, dl, None)

            di.dl.put_json("test.test.json", {"json": 1})
            res = di.dl.get_json("test.test.json")
            self.assertEqual(res["json"], 1)
            res = di.dl.get_obj("test.test.json")
            self.assertEqual(res, b"""{"json": 1}""")


if __name__ =="__main__":
    TestS3().test_get()