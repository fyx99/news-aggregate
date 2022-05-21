from typing import List
import numpy as np

from recommend.factors.general import FactorSetupInput, BaseFactor
import numpy as np

from logger import get_logger
logger = get_logger()


class RankFactors(BaseFactor):
    

    def setup(self, setup_input: FactorSetupInput):
        # TODO here weight the like"ness of a article
        self.article_ids = np.array(setup_input.article_ids)
        self.articles = setup_input.articles
        self.article_index = setup_input.article_index
        self.ready = True




    def process(self, factors: List[BaseFactor], ranks: List[np.ndarray]):
        ranks_total = np.ones(len(self.article_ids))
        if len(ranks):
            ranks_to_mean = [rank for factor, rank in zip(factors, ranks) if not factor.is_mask]
            ranks_total = np.mean(ranks_to_mean, axis=0)

            ranks_to_mask = [rank for factor, rank in zip(factors, ranks) if factor.is_mask]


            [np.multiply(ranks_total, rank_mask, out=ranks_total) for rank_mask in ranks_to_mask]

        publishers = [article.publisher for article in  self.articles]
        pure_ordered = np.argsort(ranks_total)
        ordering_scores = {p: 0 for p in set(publishers)}


        for place in pure_ordered:
            art = self.articles[place]
            ordering_scores[art.publisher] = ordering_scores[art.publisher] + 1
            ranks_total[place] = ranks_total[place] * (1 / (1 * ordering_scores[art.publisher]))


        n = 10
        # ordered with highest last np.flip(similarityOutput.scores, axis=1) could make the change
        top_n_indices = np.argsort(ranks_total)[-n:]

        top_n_article_ids = self.article_ids[top_n_indices]


        return [{**self.articles[self.article_index[article_id]].to_json(), **{f.__class__.__name__: ranks[i][n] for i, f in enumerate(factors)}} for n, article_id in enumerate(top_n_article_ids)]