# News Aggregator Crawler & ML Pipelines

This repository contains the code for the **News Aggregator Crawler** and associated **Machine Learning (ML) Pipelines**. The crawler scrapes news articles from common RSS feeds and processes them through various stages, including natural language processing (NLP) and feature extraction. The system is backed by a **PostgreSQL** database and leverages **S3** for archiving models and data persistence.

The project is designed to handle large-scale crawling and processing tasks with a focus on scalability, using technologies like **Docker**, **RabbitMQ**, and **Threading** to ensure efficient operation.

## Overview

The **News Aggregator** consists of multiple components:
- **RSS Crawler**: Scrapes news articles from different RSS feeds.
- **HTML Crawler**: Extracts article content from the web when the RSS data is insufficient.
- **Feature Extraction**: Uses pre-trained **Sentence-Transformer** models to extract meaningful features from news articles for downstream tasks.
- **Database Integration**: Utilizes PostgreSQL for storing articles and S3 for storing models and archives.
- **ML Pipelines**: The system incorporates ML models for text analysis, including semantic similarity and text pattern recognition.

The project is modular, and each job (RSS crawling, HTML crawling, feature extraction) is processed by separate threads to maximize throughput.

## How to Run

### 1. Docker Setup

You can build and run the components using Docker. Here are some useful commands:

- **Build the project**:

```bash
docker build --target test -t fxxy/news-aggregate-test .
```
Run the main crawler with RSS feed task:
```bash
docker run -e TASK='RSS' --env-file local.env fxxy/news-aggregate
```
Run the ML pipeline (e.g., for feature extraction):
```bash
docker run -m 500m --memory-swap="2500m" -e TASK='FEED' --env-file /env/drop.env fxxy/news-aggregate-ml
```
Run the service with ML tasks:
```bash
docker run --env-file local.env -p 8000:8000 fxxy/news-aggregate-srv
```
Start PostgreSQL container:
```bash
docker run --restart=always --name postgres -p 5432:5432 -e POSTGRES_PASSWORD=u3fph3ßü98fg43f34f3 -d postgres:14.1-alpine
```
Start RabbitMQ container:
```bash
docker run -d --restart=always --hostname rabbit --name rabbitmq -e RABBITMQ_DEFAULT_USER=dog -e RABBITMQ_DEFAULT_PASS="20849hfibfcn82..SADFC" -p 5672:5672 -p 15672:15672 rabbitmq:3.10.0-rc.4-management
```
2. Running the Manager
The Manager class controls the job queue and handles the job processing. The jobs are processed by multiple threads that can be run as shown below:

```python
from rss.rsscrawler import RSSCrawler
from rss.htmlcrawler import HTMLCrawler
from db.databaseinstance import DatabaseInterface
from db.postgresql import Database
from db.s3 import Datalake
from db.rabbit import MessageBroker
from queue import Queue
import threading

class Manager:
    q = Queue()

    def add_job(job):
        Manager.q.put(job)

    def run(db):
        for _ in range(5):
            worker = threading.Thread(target=Manager.process, args=(db,))
            worker.start()
        Manager.q.join()

    def process(db):
        while not Manager.q.empty():
            job = Manager.q.get()
            try:
                RssCrawlManager.process_job(db, job)
            except Exception:
                logger.info("UNEXPECTED EXCEPTION IN PROCESSING JOB")
            Manager.q.task_done()
            
3. Preprocessing Jobs
You can add jobs for RSS crawling and HTML crawling manually by running:

```python
def add_initial_rss_crawl_jobs(db: DatabaseInterface):
    feeds = get_feeds(db)
    [Manager.add_job({"job_type": "RSS_CRAWL", "feed": feed}) for feed in feeds]

def add_random_status_crawl_jobs(db: DatabaseInterface):
    article_feeds = get_random_articles(db)
    [Manager.add_job({"job_type": "HTML_CRAWL", "article": article, "feed": feed}) for article, feed in article_feeds]
```
Dependencies
Core Dependencies
BeautifulSoup: For parsing HTML content.
requests: For making HTTP requests.
psycopg2: PostgreSQL database adapter.
S3: For storing archives and models.
RabbitMQ: For job queuing.
threading: For managing concurrent job processing.
ML & NLP Dependencies
Sentence-Transformers: For feature extraction using pre-trained BERT models.

Example:

```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('bert-base-nli-stsb-mean-tokens')
```
torch: For running the BERT-based models in Sentence-Transformers.

Installation
To install the necessary dependencies, create a virtual environment and install the Python packages:

```bash
pip install -r requirements.txt
Or, if using Docker, the dependencies are included in the Dockerfile.
```
