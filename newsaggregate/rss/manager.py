from newsaggregate.db.crud.article import get_random_articles, refresh_articles_clean
from newsaggregate.db.crud.feeds import get_feeds
from newsaggregate.db.databaseinstance import DatabaseInterface
from newsaggregate.db.postgresql import Database
from newsaggregate.rss.rsscrawler import RSSCrawler
from newsaggregate.rss.htmlcrawler import HTMLCrawler
from queue import Queue
import threading
import random

from newsaggregate.storage.s3 import Datalake


class Manager:
    q = Queue(maxsize=3000)

    def add_job(job):
        Manager.q.put(job)

    def get_job():
        return Manager.q.get()

    def empty():
        return Manager.q.empty()

    # def timeout():
    #     return time.time() < (Manager.start_time + TIMEOUT)

    def run(db):
        #Manager.start_time = time.time()
        for _ in range(10):
            worker = threading.Thread(target=Manager.process, args=(db,))
            worker.start()
        Manager.q.join()
        print("ALL JOINED")

    def process(db):
        while not Manager.empty():# and not Manager.timeout():
            job = Manager.q.get()
            RssCrawlManager.process_job(db, job)
            Manager.q.task_done()
        print(f"{threading.get_ident()} DONE")


RSS_CRAWL = "RSS_CRAWL"
HTML_CRAWL = "HTML_CRAWL"


def add_initial_rss_crawl_jobs(db):
    feed_urls = get_feeds(db)
    for url in feed_urls:
        Manager.add_job({"job_type": RSS_CRAWL, "link": url})

def add_random_status_crawl_jobs(db):
    article_urls = get_random_articles(db)
    for id, url in article_urls:
        Manager.add_job({"job_type": HTML_CRAWL, "link": url, "article_id": id})


class RssCrawlManager:
    def main():
        # execute
        with Database() as db, Datalake() as dl:
            di = DatabaseInterface(db, dl)
            HTMLCrawler.get_patterns(di)
            add_initial_rss_crawl_jobs(di)
            add_random_status_crawl_jobs(di)
            Manager.run(di)
            refresh_articles_clean(di)

    def process_job(db: DatabaseInterface, job):
        if job["job_type"] == RSS_CRAWL:
            results, ids = RSSCrawler.run_single(db, job["link"])
            print(len(results))
            for item, article_id_status in zip(results, ids):
                article_id, article_status = article_id_status
                if article_status != "CRAWL":
                    if random.random() > 0.2:
                        continue
                else:
                    a = 1
                Manager.add_job(
                    {"job_type": HTML_CRAWL, "link": item["link"], "article_id": article_id}
                )
        elif job["job_type"] == HTML_CRAWL:
            HTMLCrawler.run_single(db, job["link"], job["article_id"])
        print("RAN JOB " + job["job_type"] + " " + job["link"])


if __name__ == "__main__":
    RssCrawlManager.main()

### get rss feeds from db, sequentially request them (possibly many for one site = delay), save rss info
### check if new rss info, request html (crawl safe), transform data, save site data
