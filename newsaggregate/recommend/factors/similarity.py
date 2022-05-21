import numpy as np
from recommend.factors.general import FactorSetupInput, FactorProcessInput, BaseFactor


from logger import get_logger, timeit
logger = get_logger()


class SimilarityFactor(BaseFactor):
    
    @timeit
    def setup(self, setup_input: FactorSetupInput):
        super().setup()
        # TODO here weight the like"ness of a article
        #article_ids = set(article.id for article in setup_input.articles)
        if not setup_input.similarities:
            return logger.debug("SETUP INPUT NO SIMILARITIES")
        self.article_index = setup_input.article_index
        self.article_ids = setup_input.article_ids
        self.similarities = np.mean(setup_input.similarities, axis=0)

        if len(self.similarities.shape) and self.similarities.shape[0] == len(self.article_ids):
            self.ready = True



    @timeit
    def process(self, process_input: FactorProcessInput):

        read_article_ids = set(read.article_id for read in process_input.user_transactions)

        read_articles_in_current_batch = read_article_ids & set(self.article_ids)

        if len(read_articles_in_current_batch):
            return np.mean(self.similarities[[self.article_index[article_id] for article_id in read_articles_in_current_batch]], axis=0)
        return np.ones(len(self.article_ids))
        