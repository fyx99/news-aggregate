from collections import defaultdict
import threading
import traceback
import numpy as np
from newsaggregate.db.crud.article import Article, get_article, get_articles_for_feed
from newsaggregate.db.crud.blob import save_similarities
from newsaggregate.db.crud.feeds import Feed
from newsaggregate.db.databaseinstance import DatabaseInterface
from newsaggregate.db.postgresql import Database
from newsaggregate.feed.preprocessing.bert import BertProcessorBaseEN, BertProcessorDistDE
from newsaggregate.feed.preprocessing.general import TextEmbedding
from newsaggregate.feed.preprocessing.tfidf import TfidfProcessor
from newsaggregate.storage.s3 import Datalake
import time

from newsaggregate.logging import get_logger
logger = get_logger()

class FeedManager:

    
    def main():
        with Database() as db, Datalake() as dl:
            di = DatabaseInterface(db, dl)

            demo = ["3299713", "8056613", "7939462", "8060665"]
            [FeedManager.run_single(di, d) for d in demo]
            FeedManager.run_batch(di, demo)

    # def load_text(db: DatabaseInterface):
    #     rows = get_articles_for_feed(db)
    #     articles = [r[12] for r in rows]
    #     titles = [r[4] for r in rows]
    #     summaries = [r[5] for r in rows]

        # return articles, titles, summaries


    def load_text_single(db: DatabaseInterface, id):
        article: Article = get_article(db, id)

        return article.text, article.title, article.summary

    # def preprocess_text()


    # def calculate_similarities(texts):

    #     bert_processor = BertProcessor()
    #     bert_processor.setup()
    #     bert_textembedding = bert_processor.process(texts)
    #     similarity_matrix = bert_textembedding.cosine_similarity()
    #     return similarity_matrix

    def process_single(db, id, text, language:str):
        #this function performs all processing tasks that are possible with single texts
        start = time.time()
        single_processors = defaultdict(list, {
            "EN": [BertProcessorBaseEN()],
            "DE": [BertProcessorDistDE()]
        })
        for processor in single_processors[language]:
            processor.setup()
            textembedding = processor.process(text)
            textembedding.save(db, type(processor).__name__, "Article", id)
            # hier muss das nur noch gespeichert werden
        logger.info(f"BERT PROCESSOR {time.time() - start}")
    
    def process_batch(db, ids, texts):
        #this function performs all processing tasks that are possible with multiuple texts
        batch_processors = [TfidfProcessor()]
        for processor in batch_processors:
            processor.setup()
            textembeddings = processor.process(texts)
            similarties = textembeddings.cosine_similarity(ids)
            similarties.save(db, type(processor).__name__ + "Similarity")

        single_processors = [BertProcessorDistDE()]
        for processor in single_processors:
            # -> get all relevant embeddings
            textembeddings = TextEmbedding.load_by_ids(db, type(processor).__name__, "Article", ids)
            similarties = textembeddings.cosine_similarity(ids)
            similarties.save(db, type(processor).__name__ + "Similarity")

    def run_single(db, id, text, language):
        # if not text:
        #     text, _, _ = FeedManager.load_text_single(db, id, "EN")
        FeedManager.process_single(db, id, text, language)


    def run_single_article(db, article: Article, feed: Feed):
        logger.info(f"{threading.get_ident()}: BERT {feed.language}")
        try:
            FeedManager.run_single(db, article.id, article.text, feed.language)
        except:
            logger.error(traceback.format_exc())

    
    def run_batch(db, ids):
        texts = []
        for id in ids:
            article, _, _ = FeedManager.load_text_single(db, id)
            texts.append(article)
        FeedManager.process_batch(db, np.array(ids).astype(int), texts)
        return
    

if __name__ == "__main__":


    with Database() as db, Datalake() as dl:
        di = DatabaseInterface(db, dl)

        demo = ["3299713", "8056613", "7939462", "8060665"]
        [FeedManager.run_single(di, d) for d in demo]
        FeedManager.run_batch(di, demo)

