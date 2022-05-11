import unittest
from db.databaseinstance import DatabaseInterface
from db.rabbit import MessageBroker
from test import CustomTestcase


class TestRabbit(CustomTestcase):



    def test_connection(self: unittest.TestCase):
        with MessageBroker() as rb:
            di = DatabaseInterface(None, None, rb)
            self.assertIsNotNone(di.rb)


    def test_messages(self: unittest.TestCase):
        with MessageBroker() as rb:
            db = DatabaseInterface(None, None, rb)
            db.rb.put_task("RSS", {"job_type": "RSS", "feed": "TEST1"})
            task = db.rb.get_task("RSS")

            self.assertEqual(task["feed"], "TEST1")


if __name__ =="__main__":
    TestRabbit().test_messages()