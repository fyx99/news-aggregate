import numpy as np
from db.databaseinstance import DatabaseInterface
from db.crud.interactions import get_read_counts
from recommend.factors.general import FactorSetupInput, FactorProcessInput, normalize_array

from logger import get_logger, timeit
logger = get_logger()

class ViralFactor:

    @timeit
    def setup(db: DatabaseInterface, setup_input: FactorSetupInput):

        read_count_raw = get_read_counts(db)
        read_count_array = np.zeros(len(setup_input.article_index.keys()))
        for article_id, read_count in read_count_raw:
            if article_id in setup_input.article_index:
                read_count_array[setup_input.article_index[article_id]] = read_count

        # TODO better normalization extremes?
        ViralFactor.read_counts = normalize_array(read_count_array)

    @timeit
    def process(process_input: FactorProcessInput):
        return ViralFactor.read_counts