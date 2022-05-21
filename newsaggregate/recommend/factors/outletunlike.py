from collections import Counter, defaultdict
import numpy as np
from db.databaseinstance import DatabaseInterface
from db.crud.interactions import get_read_counts
from recommend.factors.general import FactorSetupInput, FactorProcessInput, normalize_array

from logger import get_logger, timeit
logger = get_logger()

class OutletUnlike:

    is_mask = True

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

        unlike_feeds = [pref.feed_url for pref in process_input.user_preferences]

        article_feeds = np.ones(len(self.article_index.keys()))

        [np.put(article_feeds, self.feed_index[feed], 0) for feed in unlike_feeds]

        return normalize_array(article_feeds)