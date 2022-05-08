from collections import Counter, defaultdict
import numpy as np
from db.databaseinstance import DatabaseInterface
from db.crud.interactions import get_read_counts
from recommend.factors.general import FactorSetupInput, FactorProcessInput, normalize_array

from logger import get_logger, timeit
logger = get_logger()

class OutletRelatedFactor:

    @timeit
    def setup(db: DatabaseInterface, setup_input: FactorSetupInput):

        OutletRelatedFactor.outlets = set(article.feed for article in setup_input.articles)
        OutletRelatedFactor.articles = setup_input.articles
        OutletRelatedFactor.article_index = setup_input.article_index
        feed_dict = defaultdict(list)
        [feed_dict[article.feed].append(index) for index, article in enumerate(setup_input.articles)]
        OutletRelatedFactor.feed_index = feed_dict

    @timeit
    def process(process_input: FactorProcessInput):

        read_article_ids = [read.article_id for read in process_input.user_transactions]
        # TODO how to handle weight of read with scroll etc
        read_article_ids = set(read_article_ids)


        feed_list = [OutletRelatedFactor.articles[OutletRelatedFactor.article_index[article_id]].feed for article_id in read_article_ids if article_id in OutletRelatedFactor.article_index]
        feed_count = Counter(feed_list)

        article_feeds = np.zeros(len(OutletRelatedFactor.article_index.keys()))

        for feed, count in feed_count.items():
            article_feeds[OutletRelatedFactor.feed_index[feed]] = count


      
        return normalize_array(article_feeds)