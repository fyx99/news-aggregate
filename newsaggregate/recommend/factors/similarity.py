import numpy as np
from recommend.factors.general import FactorSetupInput, FactorProcessInput, BaseFactor


from logger import get_logger, timeit
logger = get_logger()


class SimilarityFactor(BaseFactor):
    
    @timeit
    def setup(setup_input: FactorSetupInput):
        # TODO here weight the like"ness of a article
        #article_ids = set(article.id for article in setup_input.articles)
        if not setup_input.similarities:
            SimilarityFactor.ready = False
            return 
        SimilarityFactor.article_index = setup_input.article_index
        SimilarityFactor.article_ids = setup_input.article_ids
        SimilarityFactor.similarities = np.mean(setup_input.similarities, axis=0)

        if len(SimilarityFactor.similarities.shape) and SimilarityFactor.similarities.shape[0] == len(SimilarityFactor.article_ids):
            SimilarityFactor.ready = True



    @timeit
    def process(process_input: FactorProcessInput):

        read_article_ids = set(read.article_id for read in process_input.user_transactions)

        read_articles_in_current_batch = read_article_ids & set(SimilarityFactor.article_ids)

        if len(read_articles_in_current_batch):
            return np.mean(SimilarityFactor.similarities[[SimilarityFactor.article_index[article_id] for article_id in read_articles_in_current_batch]], axis=0)
        return np.ones(len(SimilarityFactor.article_ids))
        