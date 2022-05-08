import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from db.crud.blob import get_embeddings, get_similarities, save_embeddings, save_similarities
from feature.numpy_utils import numpy_2d_array_as_text, text_to_numpy_2d



class TextEmbedding:
    def __init__(self, embedding):
        self.embedding = embedding


    def similarity(self):
        pass

    def cosine_similarity(self, index):
        return SimilarityMatrix(cosine_similarity(self.embedding, self.embedding), np.array(index))

    
    def save(self, db, processor, text_type, article_id):
        save_embeddings(db, numpy_2d_array_as_text(self.embedding), processor, text_type, article_id)

    def load_by_ids(db, processor, text_type, ids):
        return TextEmbedding(np.array([text_to_numpy_2d(get_embeddings(db, processor, text_type, id.item())) for id in ids]))

    
    def load_by_objs(objs):
        return TextEmbedding(
            np.array(
                [text_to_numpy_2d(obj) for obj in objs]
            )
        )


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

    def load(db, embedding_type):

        similarities, index = get_similarities(db, embedding_type)
        return SimilarityMatrix(text_to_numpy_2d(similarities), text_to_numpy_2d(index))

    def save(self, db, type):
        save_similarities(db, numpy_2d_array_as_text(self.similarities), numpy_2d_array_as_text(self.index), type)






class SimilarityOutput:
    def __init__(self, indices, scores):
        self.indices = indices
        self.scores = scores

    def __len__(self):
        return len(self.indices)

