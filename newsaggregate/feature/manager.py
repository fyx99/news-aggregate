from collections import defaultdict
import threading
import traceback
import numpy as np
from db.crud.article import Article, get_article, get_articles_for_feed
from db.crud.blob import save_similarities
from db.crud.feeds import Feed
from db.databaseinstance import DatabaseInterface
from db.postgresql import Database
from feature.preprocessing.bert import BertProcessorBaseEN, BertProcessorDistDE
from feature.preprocessing.general import TextEmbedding
from feature.preprocessing.tfidf import TfidfProcessor
from db.rabbit import MessageBroker
from db.s3 import Datalake
import time

from logger import get_logger
logger = get_logger()

class FeedManager:

    
    def main():
        with Database() as db, Datalake() as dl, MessageBroker() as rb:
            di = DatabaseInterface(db, dl, rb)
            done = False
            n = 100
            while not done:
                tasks = di.rb.get_task_batch("FEATURE", n)
                if len(tasks) < n:
                    done = True

                
                articles = [Article(**task["article"]) for task in tasks]
                feeds = [Feed(**task["feed"]) for task in tasks]

                language_group_tasks = defaultdict(list)

                for article, feed in zip(articles, feeds):
                    language_group_tasks[feed.language].append((article, feed))
                
                list_ordered = []
                [list_ordered.extend(language_group_tasks[key]) for key in language_group_tasks.keys()]

                [FeedManager.run_single_article(di, article, feed) for article, feed in list_ordered]

            logger.info("ALL SINGLE TASKS DONE")

            articles, embeddings = get_articles_for_feed(di)
            ids = [a.id for a in articles]
            texts = [a.text for a in articles]
            textembeddings = TextEmbedding.load_by_objs([e.load(di) for e in embeddings])

            FeedManager.process_embedding_batches(di, ids, textembeddings, embeddings[0].processor)
            FeedManager.process_text_batches(di, ids, texts)
            logger.info("ALL BATCH TASKS DONE")




    def load_text_single(db: DatabaseInterface, id):
        article: Article = get_article(db, id)

        return article.text, article.title, article.summary


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
        logger.info(f"BERT PROCESSOR {time.time() - start:.2f}")

    def process_text_batches(db, ids, texts):
        batch_processors = [TfidfProcessor()]

        for processor in batch_processors:
            processor.setup()
            textembeddings = processor.process(texts)
            similarties = textembeddings.cosine_similarity(ids)
            similarties.save(db, type(processor).__name__ + "Similarity")

    def process_embedding_batches(db, ids, embeddings: TextEmbedding, processor):
        similarties = embeddings.cosine_similarity(ids)
        similarties.save(db, processor + "Similarity")
    

    def run_single(db, id, text, language):
        # if not text:
        #     text, _, _ = FeedManager.load_text_single(db, id, "EN")
        FeedManager.process_single(db, id, text, language)


    def run_single_article(db, article: Article, feed: Feed):
        logger.info(f"LANGUAGE {feed.language}")
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

    FeedManager.main()

