import asyncio
import time
from typing import List

from db.crud.article import Article, get_random_articles, refresh_article_materialized_views
from db.crud.feeds import Feed, get_feeds
from db.databaseinstance import DatabaseInterface
from db.s3 import Datalake
from db.rabbit import MessageBroker
from db.async_postgresql import AsyncDatabase
from db.http import Http
from rss.rsscrawler import RSSCrawler
from rss.htmlcrawler import HTMLCrawler
from queue import Queue
import threading, random
from logger import get_logger
logger = get_logger()




RSS_CRAWL = "RSS_CRAWL"
HTML_CRAWL = "HTML_CRAWL"
FEATURE_EXTRACTION = "FEATURE_EXTRACTION"

class Manager:
    q = Queue()
    
    #feature_thread = None

    f_job_count = 1

    last_time = time.time()

    def add_job(job):
        Manager.q.put(job)

    def get_job():
        return Manager.q.get()

    def empty():
        return Manager.q.empty()

    def run(db):
        # for _ in range(1):
        #     worker = threading.Thread(target=asyncio.run, args=(Manager.process(db),))
        #     worker.start()
            #Manager.feature_thread = worker
        
        logger.debug("JOINING")
        # Manager.q.join()
        logger.debug("ALL JOINED")

    # def process_async(db):
    #     loop = asyncio.new_event_loop()
    #     asyncio.set_event_loop(loop)
    #     loop.run_until_complete(Manager.process(db))
    #     loop.close()

    async def process(db):
        futures = []
        while not Manager.empty():
            job = Manager.q.get()

            futures.append(RssCrawlManager.process_job(db, job))

            logger.debug("PROCESSED")
            Manager.f_job_count += 1
            if Manager.f_job_count % 50 == 0:
                logger.info(f"MANAGER 100 JOBS AT {time.time() - Manager.last_time:.2f} TOTAL {(time.time() - Manager.last_time) / 50:.2f} / IT")
                Manager.last_time = time.time()
            Manager.q.task_done()
            logger.debug("TASK DONE")
        asyncio.gather(*futures)
        logger.debug(f"THREAD DONE")




async def add_initial_rss_crawl_jobs(db: DatabaseInterface):
    feeds: List[Feed] = await get_feeds(db)
    [Manager.add_job({"job_type": RSS_CRAWL, "feed": feed}) for feed in feeds]

async def add_random_status_crawl_jobs(db: DatabaseInterface):
    article_feeds = await get_random_articles(db)
    [Manager.add_job({"job_type": HTML_CRAWL, "article": article, "feed": feed}) for article, feed in article_feeds]
        

class RssCrawlManager:
    async def main():
        # execute
        db = AsyncDatabase()
        await db.connect()
        dl = Datalake()
        http = Http()
        await http.create_session()
        with Datalake() as dl, MessageBroker() as rb:
            di = DatabaseInterface(db, dl, rb, http)
            await HTMLCrawler.get_patterns(di)
            await add_initial_rss_crawl_jobs(di)
            #add_random_status_crawl_jobs(di)
            await Manager.process(di)
            
            #di.rb.disconnect()  # to prevent long waits without any doing
            
            logger.info("REFRESH MATERIALIZED VIEWS")
            await refresh_article_materialized_views(di)
            logger.info("REFRESH DONE")
        await db.close()

    async def process_job(db: DatabaseInterface, job):
        job_type: str = job["job_type"]
        job_feed: Feed = job["feed"]
        job_article: Feed = job["article"] if "article" in job else None
        if job_type == RSS_CRAWL:
            articles: List[Article] = await RSSCrawler.run_single(db, job_feed)

            for article in articles:
                if article.status != "CRAWL":
                    if random.random() > 0.05:
                        continue
                Manager.add_job({"job_type": HTML_CRAWL, "feed": job_feed, "article": article})

        elif job_type == HTML_CRAWL:
            await HTMLCrawler.run_single(db, job_article)
            db.rb.put_task("FEATURE", {"job_type": FEATURE_EXTRACTION, "article": job_article.to_json(), "feed": job_feed.to_json()})
            logger.debug("ADDED JOB TO RABBIT")


if __name__ == "__main__":
    asyncio.run(RssCrawlManager.main())

