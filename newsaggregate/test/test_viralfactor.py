import unittest
from db.crud.article import Article
from recommend.factors.viral import ViralFactor
from recommend.factors.general import FactorSetupInput, FactorProcessInput
from test.custom_testcase import CustomTestcase
import numpy as np
import datetime

class TestViralFactor(CustomTestcase):

    article_list = [
        Article(113, "https://outlet1.com/article1", "", "", "113", "Sum1", datetime.datetime(2020, 1, 1), "https://outlet1.com/feed", "asdasd", "ACTIVE", "Text1"),
        Article(114, "https://outlet1.com/article2", "", "", "114", "Sum1", datetime.datetime(2020, 1, 1), "https://outlet1.com/feed", "asdasd", "ACTIVE", "Text1"),
        Article(115, "https://outlet2.com/article1", "", "", "115", "Sum1", datetime.datetime(2020, 1, 1), "https://outlet2.com/feed", "asdasd", "ACTIVE", "Text1"),
        Article(116, "https://outlet2.com/article2", "", "", "116", "Sum1", datetime.datetime(2020, 1, 1), "https://outlet2.com/feed", "asdasd", "ACTIVE", "Text1"),
    ]

    def setUp(self: unittest.TestCase):
        super().setUp()

        


        # total_read_counts = np.array([[113, 6], [114, 3]])


        # self.factorSetupInput: FactorSetupInput = FactorSetupInput(article_list, matrices, total_read_counts)
        # self.factorProcessInput = FactorProcessInput("user1", user_reads, user_prefs)


    def test_empty_setup_input(self: unittest.TestCase):
        
        factorSetupInput: FactorSetupInput = FactorSetupInput(self.article_list, [], np.array([]))
        factorProcessInput: FactorProcessInput = FactorProcessInput(None, None, None)

        factor = ViralFactor()
        factor.setup(factorSetupInput)
        self.assertTrue(factor.ready)
        result = factor.process(factorProcessInput)

        self.assertTrue(np.array_equal(result, np.zeros(4)))
        self.assertEqual(factorSetupInput.article_ids, [113, 114, 115, 116])

                
        factorSetupInput: FactorSetupInput = FactorSetupInput([], [], np.array([]))
        factorProcessInput: FactorProcessInput = FactorProcessInput(None, None, None)

        factor = ViralFactor()
        factor.setup(factorSetupInput)
        self.assertFalse(factor.ready)
        result = factor.process(factorProcessInput)

        self.assertTrue(np.array_equal(result, np.array([])))
        self.assertEqual(factorSetupInput.article_ids, [])



    def test_read_counts(self: unittest.TestCase):
        total_read_counts = np.array([[113, 1], [114, 1], [115, 0]])
        factorSetupInput: FactorSetupInput = FactorSetupInput(self.article_list, [], total_read_counts)
        factorProcessInput: FactorProcessInput = FactorProcessInput(None, None, None)
        self.assertEqual(factorSetupInput.article_ids, [113, 114, 115, 116])        
        factor = ViralFactor()
        factor.setup(factorSetupInput)
        self.assertTrue(factor.ready)
        result = factor.process(factorProcessInput)

        self.assertTrue(np.array_equal(result, np.array([1,1,0,0])))
    
        total_read_counts = np.array([[113, 10], [114, 1], [115, 0]])
        factorSetupInput: FactorSetupInput = FactorSetupInput(self.article_list, [], total_read_counts)
        factorProcessInput: FactorProcessInput = FactorProcessInput(None, None, None)
        self.assertEqual(factorSetupInput.article_ids, [113, 114, 115, 116])        
        factor = ViralFactor()
        factor.setup(factorSetupInput)
        self.assertTrue(factor.ready)
        result = factor.process(factorProcessInput)

        self.assertTrue(np.array_equal(result, np.array([1,0.1,0,0])))

        total_read_counts = np.array([[113, 100], [114, 100], [115, 100]])
        factorSetupInput: FactorSetupInput = FactorSetupInput(self.article_list, [], total_read_counts)
        factorProcessInput: FactorProcessInput = FactorProcessInput(None, None, None)
        self.assertEqual(factorSetupInput.article_ids, [113, 114, 115, 116])        
        factor = ViralFactor()
        factor.setup(factorSetupInput)
        self.assertTrue(factor.ready)
        result = factor.process(factorProcessInput)

        self.assertTrue(np.array_equal(result, np.array([1,1,1,0])))



        
if __name__ =="__main__":
    test = TestViralFactor()()
    test.setUp()
    test.test_read_counts()