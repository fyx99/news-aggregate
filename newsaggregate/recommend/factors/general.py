from typing import List, Dict

import numpy as np

from db.crud.article import Article
from db.crud.interactions import Read
from feature.preprocessing.general import SimilarityMatrix


class FactorOutput:
    pass





class FactorSetupInput:

	article_ids: List
	article_index: Dict
	articles: List[Article]
	similarities: List[SimilarityMatrix]
	read_counts: np.ndarray

	def __init__(self, articles: List[Article], similarity_matrixes: List[SimilarityMatrix], read_counts: np.ndarray) -> None:
		self.articles = articles
		self.article_ids = [article.id for article in self.articles]
		self.article_index = {article_id: index for index, article_id in enumerate(self.article_ids)}
		self.similarities = [FactorSetupInput.similarity_matrix_to_article_order(similaritiy, self.article_ids, self.article_index) for similaritiy in similarity_matrixes]
		self.read_counts = read_counts

	def similarity_matrix_to_article_order(similarities, article_ids, article_index):
		similarities_reverse_index = dict(zip(similarities.index, range(len(similarities.index))))
		similarity_matrix = np.zeros((len(article_ids), len(article_ids)))
		for article_id in article_ids:
			for other_article_id in article_ids:
					if article_id in similarities_reverse_index and other_article_id in similarities_reverse_index:
						similarity_matrix[article_index[article_id], article_index[other_article_id]] = similarities.similarities[similarities_reverse_index[article_id], similarities_reverse_index[other_article_id]]
			
		return similarity_matrix


class FactorProcessInput:

	user_id: str
	user_transactions: List[Read]

	def __init__(self, user_id: str, user_transactions: List[Read]) -> None:
		self.user_id = user_id
		self.user_transactions = user_transactions


def normalize_array(array):
	min_value = np.min(array)
	max_value = np.max(array)
	divisor = (max_value - min_value) if (max_value - min_value) != 0 else 1
	array_normalized = (array - min_value) / divisor
	return array_normalized


    