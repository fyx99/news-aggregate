import unittest
import warnings
class CustomTestcase(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        warnings.simplefilter("ignore", ResourceWarning)