

import numpy as np
from db.crud.blob import get_similarities
from db.databaseinstance import DatabaseInterface
from db.postgresql import Database
from feature.numpy_utils import text_to_numpy_2d

from feature.preprocessing.general import SimilarityMatrix
from logger import get_logger
from db.s3 import Datalake
logger = get_logger()


class SimilarityInference:

    def setup(self, db):
        similarities, index = get_similarities(db, "BertProcessorDistDESimilarity")
        self.similarities = SimilarityMatrix(text_to_numpy_2d(similarities), text_to_numpy_2d(index))



    def top_n(self):
        output = self.similarities.top_n(10)
        logger.info(output.indices)
        logger.info(output.scores)
        

if __name__ == "__main__":
    
    with Database() as db, Datalake() as dl:
        di = DatabaseInterface(db, dl)

        sim = SimilarityInference()
        sim.setup(di)
        sim.top_n()