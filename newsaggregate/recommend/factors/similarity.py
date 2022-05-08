from collections import Counter, defaultdict
import numpy as np
from db.databaseinstance import DatabaseInterface
from db.crud.interactions import get_read_counts
from recommend.factors.general import FactorSetupInput, FactorProcessInput, normalize_array


from logger import get_logger, timeit
logger = get_logger()


class SimilarityFactor:
    
    @timeit
    def setup(db: DatabaseInterface, setup_input: FactorSetupInput):
        # TODO here weight the like"ness of a article
        #article_ids = set(article.id for article in setup_input.articles)
        SimilarityFactor.article_index = setup_input.article_index
        SimilarityFactor.article_ids = setup_input.article_ids
        SimilarityFactor.similarities = np.mean(setup_input.similarities, axis=0)



    @timeit
    def process(process_input: FactorProcessInput):

        read_article_ids = set(read.article_id for read in process_input.user_transactions)

        read_articles_in_current_batch = read_article_ids & set(SimilarityFactor.article_ids)

        return np.mean(SimilarityFactor.similarities[[SimilarityFactor.article_index[article_id] for article_id in read_articles_in_current_batch]], axis=0)