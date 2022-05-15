import traceback
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from db.async_crud.blob import get_similarities
from db.crud.blob import get_embeddings, save_embeddings, save_similarities

from logger import get_logger
logger = get_logger()

class TextEmbedding:
    def __init__(self, embedding):
        self.embedding = embedding


    def similarity(self):
        pass

    def cosine_similarity(self, index):
        return SimilarityMatrix(cosine_similarity(self.embedding, self.embedding).astype(np.float16), np.array(index, dtype=int))

    
    def save(self, db, processor, text_type, article_id):
        save_embeddings(db, self.embedding, processor, text_type, article_id)

    def load_by_ids(db, processor, text_type, ids):
        return TextEmbedding(np.array([get_embeddings(db, processor, text_type, id.item()) for id in ids]))

    
    def load_by_objs(objs):
        return TextEmbedding(np.array(objs))


class SimilarityMatrix:
    def __init__(self, similarities, index):
        self.similarities = similarities
        self.index = index
        if self.similarities.shape[0] != self.similarities.shape[1]:
            raise Exception("Not a Similarity Matrix")
        if self.similarities.shape[0] != index.shape[0]:
            raise Exception("Not a Index to this Similarity Matrix")
        np.fill_diagonal(self.similarities, 0)

    def top_n(self, n):
        # ordered with highest last np.flip(similarityOutput.scores, axis=1) could make the change
        top_n_indices = np.apply_along_axis(lambda x: np.argsort(x)[-n:], 0, self.similarities).T
        top_n_scores = np.array([self.similarities[i][top_n_indices[i]] for i in range(len(top_n_indices))])
        return SimilarityOutput(self.index[top_n_indices], top_n_scores)

    def top_n_reference(self, n, ref):
        # ordered with highest last np.flip(similarityOutput.scores, axis=1) could make the change
        top_n_indices = np.apply_along_axis(lambda x: np.argsort(x)[-n:], 0, self.similarities).T
        top_n_scores = np.array([self.similarities[i][top_n_indices[i]] for i in range(len(top_n_indices))])
        return SimilarityOutput(self.index[top_n_indices], top_n_scores)

    async def load(db, dl, embedding_type):
        try:
            similarities, index = await get_similarities(db, dl, embedding_type)
        except IndexError:
            logger.error(traceback.format_exc())
            return False
        return SimilarityMatrix(similarities, index)

    def save(self, db, type):
        save_similarities(db, self.similarities, self.index, type)







class SimilarityOutput:
    def __init__(self, indices, scores):
        self.indices = indices
        self.scores = scores

    def __len__(self):
        return len(self.indices)

