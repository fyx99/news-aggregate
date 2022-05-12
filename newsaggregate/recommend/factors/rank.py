import numpy as np
from recommend.factors.general import FactorSetupInput, FactorProcessInput
import numpy as np

from logger import get_logger, timeit
logger = get_logger()


class RankFactors:
    

    def setup(setup_input: FactorSetupInput):
        # TODO here weight the like"ness of a article
        RankFactors.article_ids = np.array(setup_input.article_ids)
        RankFactors.articles = setup_input.articles
        RankFactors.article_index = setup_input.article_index




    def process(factors, ranks):

        ranks_mean = np.mean(ranks, axis=0)



        n = 10
        # ordered with highest last np.flip(similarityOutput.scores, axis=1) could make the change
        top_n_indices = np.argsort(ranks_mean)[-n:]
        top_n_scores = ranks_mean[top_n_indices]
        top_n_article_ids = RankFactors.article_ids[top_n_indices]


        return [RankFactors.articles[RankFactors.article_index[article_id]].title for article_id in top_n_article_ids]