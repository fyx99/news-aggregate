import asyncio
from typing import List, Dict

import numpy as np

from db.crud.article import Article
from db.crud.interactions import Read
from feature.preprocessing.general import SimilarityMatrix
from db.crud.interactions import Preference
from db.async_crud.article import get_articles_clean
from db.async_crud.interactions import get_read_counts, get_preferences_for_user, get_reads_for_user

from logger import get_logger
logger = get_logger()

class FactorOutput:
    pass

import time



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
		self.similarities = [FactorSetupInput.similarity_matrix_to_article_order(similaritiy, self.article_ids, self.article_index) for similaritiy in similarity_matrixes if similaritiy]	# to check if not was an error 
		self.read_counts = read_counts

	async def load(db, dl):
		setup_coros = []
		setup_coros.append(get_articles_clean(db))
		setup_coros.append(get_read_counts(db))
		setup_coros.extend([SimilarityMatrix.load(db, dl, type) for type in ["BertProcessorDistDESimilarity", "TfidfProcessorSimilarity"]])
		
		articles_clean, read_counts, *matrices,  = await asyncio.gather(*setup_coros)
		if not articles_clean:
			raise IndexError("DATABASE RETURNED NOT ENOUGH ENTRIES")
		return FactorSetupInput(articles_clean, matrices, read_counts)


	def similarity_matrix_to_article_order(similarities, article_ids, article_index):
		start = time.time()
		similarities_reverse_index = dict(zip(similarities.index, range(len(similarities.index))))
		existing_elements = np.intersect1d(article_ids, similarities.index)
		insert_indices = np.array([article_index[e] for e in existing_elements])
		similarity_matrix = np.zeros((len(article_ids), len(article_ids)))
		for article_id in existing_elements:
			a = similarity_matrix[article_index[article_id]]
			v = insert_indices
			z = [similarities_reverse_index[e] for e in existing_elements]
			ind = similarities.similarities[similarities_reverse_index[article_id]][z]
			np.put(a, v, ind)

		# index_combinations = np.array(np.meshgrid(similarities.index, similarities.index)).T.reshape(-1, 2)
		# flat_indices = np.array([article_index[y] + article_index[x] * len(article_ids) for x, y in index_combinations if x in article_index and y in article_index])
		# flat_indices_to_delete = np.setdiff1d(similarities.index, article_ids)
		# similarity_matrix_flat = np.zeros(len(article_ids) * len(article_ids))
		# source_similarity_matrix_flat = similarities.similarities.flatten()
		# np.put(similarity_matrix_flat, flat_indices, source_similarity_matrix_flat)
		# similarity_matrix3 = similarity_matrix_flat.reshape(len(article_ids), len(article_ids))

		# print("1")
		# similarity_matrix2 = np.zeros((len(article_ids), len(article_ids)))
		# for article_id in article_ids:
		# 	for other_article_id in article_ids:
		# 			if article_id in similarities_reverse_index and other_article_id in similarities_reverse_index:
		# 				similarity_matrix2[article_index[article_id], article_index[other_article_id]] = similarities.similarities[similarities_reverse_index[article_id], similarities_reverse_index[other_article_id]]
		# a = 1
		logger.debug(f"Done similarity_matrix_to_article_order {time.time() - start}")
		return similarity_matrix


class FactorProcessInput:

	user_id: str
	user_transactions: List[Read]

	def __init__(self, user_id: str, user_transactions: List[Read], user_preferences: List[Preference]) -> None:
		self.user_id = user_id
		self.user_transactions = user_transactions
		self.user_preferences = user_preferences


	async def load(db, user_id):
		setup_coros = []
		setup_coros.append(get_reads_for_user(db, user_id))
		setup_coros.append(get_preferences_for_user(db, user_id))
		user_reads, user_prefs = await asyncio.gather(*setup_coros)
		return FactorProcessInput(user_id, user_reads, user_prefs)


def normalize_array(array):
	if array.size == 0:
		logger.error("ARRAY IS EMPTY")
		return array
	min_value = np.min(array)
	max_value = np.max(array)
	divisor = (max_value - min_value) if (max_value - min_value) != 0 else 1
	array_normalized = (array - min_value) / divisor
	return array_normalized


    


class BaseFactor():

	ready = False
	is_mask = False

	def setup():
		pass

	def process():
		pass