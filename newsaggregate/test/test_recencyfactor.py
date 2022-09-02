import unittest
from db.crud.article import Article
from recommend.factors.recency import RecencyFactor
from recommend.factors.viral import ViralFactor
from recommend.factors.general import FactorSetupInput, FactorProcessInput
from test.custom_testcase import CustomTestcase
import numpy as np
import datetime

class TestRecencyFactor(CustomTestcase):


    def setUp(self: unittest.TestCase):
        super().setUp()
        RecencyFactor.ready = False


    def test_recency_empty(self: unittest.TestCase):

        factorSetupInput: FactorSetupInput = FactorSetupInput([], [], np.array([]))
        factorProcessInput: FactorProcessInput = FactorProcessInput(None, None, None)

        factor = RecencyFactor()
        with self.assertRaises(ValueError):
            factor.setup(factorSetupInput)
        self.assertFalse(factor.ready)

        self.assertEqual(factorSetupInput.article_ids, [])



    def test_recency(self: unittest.TestCase):

        article_list = [
            Article(113, "https://outlet1.com/article1", "", "", "113", "Sum1", datetime.datetime(2020, 1, 1), datetime.datetime(2020, 1, 1), "https://outlet1.com/feed", "asdasd", "ACTIVE", "Text1"),
            Article(114, "https://outlet1.com/article2", "", "", "114", "Sum1", datetime.datetime(2020, 2, 1), datetime.datetime(2020, 2, 1), "https://outlet1.com/feed", "asdasd", "ACTIVE", "Text1"),
            Article(115, "https://outlet2.com/article1", "", "", "115", "Sum1", datetime.datetime(2020, 3, 1), datetime.datetime(2020, 3, 1), "https://outlet2.com/feed", "asdasd", "ACTIVE", "Text1"),
            Article(116, "https://outlet2.com/article2", "", "", "116", "Sum1", datetime.datetime(2020, 3, 3), datetime.datetime(2020, 3, 3), "https://outlet2.com/feed", "asdasd", "ACTIVE", "Text1"),
            Article(116, "https://outlet2.com/article2", "", "", "116", "Sum1", datetime.datetime(2020, 3, 3), datetime.datetime(2020, 3, 3), "https://outlet2.com/feed", "asdasd", "ACTIVE", "Text1"),
            Article(116, "https://outlet2.com/article2", "", "", "116", "Sum1", datetime.datetime(2020, 3, 4), datetime.datetime(2020, 3, 4), "https://outlet2.com/feed", "asdasd", "ACTIVE", "Text1"),
            Article(116, "https://outlet2.com/article2", "", "", "116", "Sum1", datetime.datetime(2020, 3, 5), datetime.datetime(2020, 3, 5), "https://outlet2.com/feed", "asdasd", "ACTIVE", "Text1"),
            Article(116, "https://outlet2.com/article2", "", "", "116", "Sum1", datetime.datetime(2020, 3, 6), datetime.datetime(2020, 3, 6), "https://outlet2.com/feed", "asdasd", "ACTIVE", "Text1"),
        ]
        
        factorSetupInput: FactorSetupInput = FactorSetupInput(article_list, [], np.array([]))
        factorProcessInput: FactorProcessInput = FactorProcessInput(None, None, None)

        factor = RecencyFactor()
        factor.setup(factorSetupInput)
        self.assertTrue(factor.ready)
        result = factor.process(factorProcessInput)

        # self.assertEqual(result[0], 0)
        # self.assertEqual(result[7], 1)
        # self.assertEqual(result[3] > 0.99, True)
        
        




if __name__ =="__main__":
    test = TestRecencyFactor()
    test.test_recency_empty()