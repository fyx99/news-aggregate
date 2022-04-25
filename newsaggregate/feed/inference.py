

import numpy as np
from newsaggregate.db.crud.blob import get_similarities
from newsaggregate.db.databaseinstance import DatabaseInterface
from newsaggregate.db.postgresql import Database
from newsaggregate.feed.numpy_utils import text_to_numpy_2d

from newsaggregate.feed.preprocessing.general import SimilarityMatrix
from newsaggregate.logging import get_logger
from newsaggregate.storage.s3 import Datalake
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