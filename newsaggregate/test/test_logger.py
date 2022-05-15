import unittest
from test.custom_testcase import CustomTestcase
        
from logger import get_logger

class TestLogger(CustomTestcase):

    def test_get_logger(self: unittest.TestCase):
        logger = get_logger()
        self.assertIsNotNone(logger.info)



if __name__ =="__main__":
    TestLogger().test_get_logger()