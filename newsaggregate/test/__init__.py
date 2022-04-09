import unittest
import warnings
class CustomTestcase(unittest.TestCase):

    def setUp(self):
        warnings.simplefilter("ignore", ResourceWarning)