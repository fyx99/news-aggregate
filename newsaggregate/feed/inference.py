

import numpy as np
from newsaggregate.db.crud.blob import get_similarities

from newsaggregate.feed.preprocessing.general import SimilarityMatrix, TextEmbedding

class SimilarityInference:

    def setup(self):
        
        self.similarities = SimilarityMatrix(get_similarities("Similarity"))


    def process(self, texts):

        
        embeddings = [self.model.encode(article, show_progress_bar=False) for article in texts]
        embeddings_array = np.array(embeddings)
        return TextEmbedding(embeddings_array)