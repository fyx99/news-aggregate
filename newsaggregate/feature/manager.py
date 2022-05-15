from collections import defaultdict
import traceback
import numpy as np
from db.crud.article import Article, get_article, get_articles_for_feed, get_articles_clean_language
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


    single_processors = defaultdict(list, {
        "EN": [BertProcessorBaseEN()],
        "DE": [BertProcessorDistDE()]
    })

    def setup():
        [processor.setup() for processorlist in FeedManager.single_processors.values() for processor in processorlist]

    def clear():
        [processor.clear() for processorlist in FeedManager.single_processors.values() for processor in processorlist]

    def process_all_tasks_by_language(db: DatabaseInterface, language: str):
        while True:
            task = db.rb.get_task(f"FEATURE.{language}")
            if not task:
                break
            FeedManager.run_single_article(db, Article(**task["article"]), Feed(**task["feed"]), task["delivery_tag"])
    
    def main():
        with Database() as db, Datalake() as dl, MessageBroker() as rb:
            di = DatabaseInterface(db, dl, rb)

            ### Process Rabbit Queue for different languages until empty
            FeedManager.setup()
            languages = ["DE", "EN"]
            [FeedManager.process_all_tasks_by_language(di, language) for language in languages]
            
            FeedManager.clear()   # dereference model for memory saving
            logger.info("ALL SINGLE TASKS DONE")

            embedding_names = [BertProcessorBaseEN.__name__, BertProcessorDistDE.__name__]
            
            all_texts = []
            all_ids = [] # todo stupid workaround
            for embedding_type in embedding_names:
                logger.info(f"PROCESS {embedding_type}")
                articles, embeddings = get_articles_for_feed(di, embedding_type)
                ids = [a.id for a in articles]
                all_ids.extend(ids)
                all_texts.extend([a.text for a in articles])
                logger.info(f"LOADED {len(embeddings)}")
                textembeddings = TextEmbedding.load_by_objs([e.blob for e in embeddings])
                logger.info("Loaded Text Embeddings")
                FeedManager.process_embedding_batches(di, ids, textembeddings, embedding_type)
                logger.info("Processed Embedding Batches")
            FeedManager.process_text_batches(di, all_ids, all_texts)
            logger.info("ALL BATCH TASKS DONE")




    def load_text_single(db: DatabaseInterface, id):
        article: Article = get_article(db, id)

        return article.text, article.title, article.summary


    def process_single(db, id, text, language:str):
        #this function performs all processing tasks that are possible with single texts
        start = time.time()

        
        for processor in FeedManager.single_processors[language]:

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
    


    def run_single_article(db: DatabaseInterface, article: Article, feed: Feed, tag: str):
        logger.info(f"LANGUAGE {feed.language}")
        try:
            FeedManager.process_single(db, article.id, article.text, feed.language)
            db.rb.ack_message(tag)
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
    # with Database() as db, Datalake() as dl, MessageBroker() as rb:
    #     di = DatabaseInterface(db, dl, rb)
    #     FeedManager.setup()
    #     for article in get_articles_clean_language(di, "EN"):
    #         FeedManager.process_single(di, article.id, article.text, "EN")

        
    #     for article in get_articles_clean_language(di, "DE"):
    #         FeedManager.process_single(di, article.id, article.text, "DE")

