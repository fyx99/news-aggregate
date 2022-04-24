from typing import List
from newsaggregate.db.crud.article import Article, get_random_articles, refresh_article_materialized_views
from newsaggregate.db.crud.feeds import Feed, get_feeds
from newsaggregate.db.databaseinstance import DatabaseInterface
from newsaggregate.db.postgresql import Database
from newsaggregate.feed.manager import FeedManager
from newsaggregate.rss.rsscrawler import RSSCrawler
from newsaggregate.rss.htmlcrawler import HTMLCrawler
from queue import Queue
import threading, random
from newsaggregate.logging import get_logger
logger = get_logger()

from newsaggregate.storage.s3 import Datalake


class Manager:
    q = Queue()

    def add_job(job):
        Manager.q.put(job)

    def get_job():
        return Manager.q.get()

    def empty():
        return Manager.q.empty()

    def run(db):
        for _ in range(2):
            worker = threading.Thread(target=Manager.process, args=(db,))
            worker.start()
        Manager.q.join()
        logger.info("ALL JOINED")

    def process(db):
        while not Manager.empty():
            job = Manager.q.get()
            RssCrawlManager.process_job(db, job)
            Manager.q.task_done()
        logger.info(f"{threading.get_ident()} DONE")


RSS_CRAWL = "RSS_CRAWL"
HTML_CRAWL = "HTML_CRAWL"
FEATURE_EXTRACTION = "FEATURE_EXTRACTION"


def add_initial_rss_crawl_jobs(db: DatabaseInterface):
    feeds: List[Feed] = get_feeds(db)
    [Manager.add_job({"job_type": RSS_CRAWL, "feed": feed}) for feed in feeds]

def add_random_status_crawl_jobs(db: DatabaseInterface):
    article_feeds = get_random_articles(db)
    [Manager.add_job({"job_type": HTML_CRAWL, "article": article, "feed": feed}) for article, feed in article_feeds]
        

class RssCrawlManager:
    def main():
        # execute
        with Database() as db, Datalake() as dl:
            di = DatabaseInterface(db, dl)
            HTMLCrawler.get_patterns(di)
            add_initial_rss_crawl_jobs(di)
            add_random_status_crawl_jobs(di)
            Manager.run(di)
            refresh_article_materialized_views(di)

    def process_job(db: DatabaseInterface, job):
        job_type: str = job["job_type"]
        job_feed: Feed = job["feed"]
        job_article: Feed = job["article"] if "article" in job else None
        if job_type == RSS_CRAWL:
            articles: List[Article] = RSSCrawler.run_single(db, job_feed)

            for article in articles:
                if article.status != "CRAWL":
                    if random.random() > 0.2:
                        continue
                Manager.add_job({"job_type": HTML_CRAWL, "feed": job_feed, "article": article})

        elif job_type == HTML_CRAWL:
            HTMLCrawler.run_single(db, job_article)
            Manager.add_job({"job_type": FEATURE_EXTRACTION, "article": job_article, "feed": job_feed})
        
        elif job_type == FEATURE_EXTRACTION:
            if job_feed.language != 'EN' and job_feed.language != 'DE':
                a = 1
            FeedManager.run_single_article(db, job_article, job_feed)
        # extra für jeden logger.info(f"""SIZE {Manager.q.qsize()} RAN JOB {job_type} {job["link"]}""")


if __name__ == "__main__":
    RssCrawlManager.main()

