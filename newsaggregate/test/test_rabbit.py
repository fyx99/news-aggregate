import unittest
from db.databaseinstance import DatabaseInterface
from db.rabbit import MessageBroker
from test.custom_testcase import CustomTestcase


class TestRabbit(CustomTestcase):



    def test_connection(self: unittest.TestCase):
        with MessageBroker() as rb:
            di = DatabaseInterface(None, None, rb)
            self.assertIsNotNone(di.rb)


    def test_messages(self: unittest.TestCase):
        
        with MessageBroker() as rb:
            db = DatabaseInterface(None, None, rb)
            db.rb.put_task("TEST", {"job_type": "TEST", "feed": "TEST1"})
            task = db.rb.get_task("TEST")
            self.assertEqual(task["feed"], "TEST1")
            # expect no second message in queue
            self.assertFalse(db.rb.get_task("TEST"))
            
        # but on reconnect it is back because not ack
        with MessageBroker() as rb:
            db = DatabaseInterface(None, None, rb)
            
            task = db.rb.get_task("TEST")
            self.assertEqual(task["feed"], "TEST1")
            self.assertTrue("delivery_tag" in task)
            db.rb.ack_message(task["delivery_tag"])
            self.assertFalse(db.rb.get_task("TEST"))


    def clear_queue(self: unittest.TestCase):
        with MessageBroker() as rb:
            db = DatabaseInterface(None, None, rb)
            while True:
                task = db.rb.get_task("TEST")
                if not task:
                    break
                db.rb.ack_message(task["delivery_tag"])

if __name__ =="__main__":
    TestRabbit().clear_queue()
    TestRabbit().test_messages()