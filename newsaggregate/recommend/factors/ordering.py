from typing import List
import numpy as np

from recommend.factors.general import FactorSetupInput, BaseFactor
import numpy as np

from logger import get_logger
logger = get_logger()


class RankFactors:
    

    def setup(setup_input: FactorSetupInput):
        # TODO here weight the like"ness of a article
        RankFactors.article_ids = np.array(setup_input.article_ids)
        RankFactors.articles = setup_input.articles
        RankFactors.article_index = setup_input.article_index




    def process(factors: List[BaseFactor], ranks: List[np.ndarray]):
        ranks_total = np.ones(len(RankFactors.article_ids))
        if len(ranks):
            ranks_to_mean = [rank for factor, rank in zip(factors, ranks) if not factor.is_mask]
            ranks_mean = np.mean(ranks_to_mean, axis=0)

            ranks_to_mask = [rank for factor, rank in zip(factors, ranks) if factor.is_mask]
            ranks_total = ranks_to_mask

            [np.multiply(ranks_total, rank_mask, out=ranks_total) for rank_mask in ranks_to_mask]



        n = 10
        # ordered with highest last np.flip(similarityOutput.scores, axis=1) could make the change
        top_n_indices = np.argsort(ranks_mean)[-n:]
        top_n_scores = ranks_mean[top_n_indices]
        top_n_article_ids = RankFactors.article_ids[top_n_indices]


        return [RankFactors.articles[RankFactors.article_index[article_id]].to_json() for article_id in top_n_article_ids]