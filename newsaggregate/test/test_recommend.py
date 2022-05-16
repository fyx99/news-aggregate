import unittest
from db.crud.article import Article
from db.crud.interactions import Read, Preference
from feature.preprocessing.general import SimilarityMatrix
from recommend.factors.general import FactorSetupInput, FactorProcessInput
from test.custom_testcase import CustomTestcase
import numpy as np
import datetime

class TestRecommend(CustomTestcase):



    def setUp(self: unittest.TestCase):
        super().setUp()

        article_list = [
            Article(113, "https://outlet1.com/article1", "", "", "113", "Sum1", datetime.datetime(2020, 1, 1), "https://outlet1.com/feed", "asdasd", "ACTIVE", "Text1"),
            Article(114, "https://outlet1.com/article2", "", "", "114", "Sum1", datetime.datetime(2020, 1, 1), "https://outlet1.com/feed", "asdasd", "ACTIVE", "Text1"),
            Article(115, "https://outlet2.com/article1", "", "", "115", "Sum1", datetime.datetime(2020, 1, 1), "https://outlet2.com/feed", "asdasd", "ACTIVE", "Text1"),
            Article(116, "https://outlet2.com/article2", "", "", "116", "Sum1", datetime.datetime(2020, 1, 1), "https://outlet2.com/feed", "asdasd", "ACTIVE", "Text1"),
        ]
        total_read_counts = np.array([[113, 6], [114, 3]])


        user_reads = [
            Read("user1", 114, datetime.datetime(2020, 1, 1), datetime.datetime(2020, 1, 1), 0.8),
            Read("user1", 115, datetime.datetime(2020, 1, 1), datetime.datetime(2020, 1, 1), 0.8),
            Read("user1", 116, datetime.datetime(2020, 1, 1), datetime.datetime(2020, 1, 1), 0.8),
        ]

        user_prefs = [
            Preference("user1", "https://outlet1.com/feed", 1, "UNFOLLOW")
        ]
        similarity_matrix_db_index = np.array([113, 114])
        similarity_matrix_db = np.array([
                                            [  1, 0.5], 
                                            [0.5,   1]
                                        ])

        matrices = [
            SimilarityMatrix(similarity_matrix_db, similarity_matrix_db_index)
        ]
        self.factorSetupInput: FactorSetupInput = FactorSetupInput(article_list, matrices, total_read_counts)
        self.factorProcessInput = FactorProcessInput("user1", user_reads, user_prefs)


    def test_similaritymatrix(self: unittest.TestCase):
        factorSetupInput: FactorSetupInput = self.factorSetupInput
        self.assertEqual(factorSetupInput.article_ids, [113, 114, 115, 116])

if __name__ =="__main__":
    test = TestRecommend()
    test.setUp()
    test.test_similaritymatrix()