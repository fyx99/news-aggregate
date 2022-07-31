import unittest
from db.crud.article import get_articles_for_feed
from db.databaseinstance import DatabaseInterface
from db.postgresql import Database
from db.s3 import Datalake
from feature.preprocessing.bert import BertProcessorDistDE
from test.custom_testcase import CustomTestcase


class TestCrud(CustomTestcase):

    def test_get_articles_for_feed(self: unittest.TestCase):

        with Database() as db:
            di = DatabaseInterface(db)
            articles, embeddings = get_articles_for_feed(di, BertProcessorDistDE.__name__, 10)
            self.assertIsNotNone(articles)
            self.assertIsNotNone(embeddings)
            self.assertEqual(len(articles), len(embeddings))
            self.assertEqual(len(articles), 10)




if __name__ =="__main__":
    TestCrud().test_get_articles_for_feed()