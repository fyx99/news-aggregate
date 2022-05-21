from collections import Counter, defaultdict
import numpy as np
from db.databaseinstance import DatabaseInterface
from db.crud.interactions import get_read_counts
from recommend.factors.general import FactorSetupInput, FactorProcessInput, normalize_array, BaseFactor

from logger import get_logger, timeit
logger = get_logger()

class OutletRelatedFactor(BaseFactor):

    

    @timeit
    def setup(self, setup_input: FactorSetupInput):
        super().setup()
        self.outlets = set(article.feed for article in setup_input.articles)
        self.articles = setup_input.articles
        self.article_index = setup_input.article_index
        feed_dict = defaultdict(list)
        [feed_dict[article.feed].append(index) for index, article in enumerate(setup_input.articles)]
        self.feed_index = feed_dict

        self.ready = True

    @timeit
    def process(self, process_input: FactorProcessInput):

        read_article_ids = [read.article_id for read in process_input.user_transactions]
        # TODO how to handle weight of read with scroll etc
        read_article_ids = set(read_article_ids)


        feed_list = [self.articles[self.article_index[article_id]].feed for article_id in read_article_ids if article_id in self.article_index]
        feed_count = Counter(feed_list)

        article_feeds = np.zeros(len(self.article_index.keys()))

        for feed, count in feed_count.items():
            article_feeds[self.feed_index[feed]] = count


        return normalize_array(article_feeds)