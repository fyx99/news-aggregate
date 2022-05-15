import numpy as np
from recommend.factors.general import FactorSetupInput, FactorProcessInput, normalize_array, BaseFactor

from logger import get_logger, timeit
logger = get_logger()

class ViralFactor(BaseFactor):

    @timeit
    def setup(setup_input: FactorSetupInput):
        read_count_raw = setup_input.read_counts
        read_count_array = np.zeros(len(setup_input.article_index.keys()))
        for article_id, read_count in read_count_raw:
            if article_id in setup_input.article_index:
                read_count_array[setup_input.article_index[article_id]] = read_count

        # TODO better normalization extremes?
        ViralFactor.read_counts = normalize_array(read_count_array)

        ViralFactor.ready = True

    @timeit
    def process(process_input: FactorProcessInput):
        return ViralFactor.read_counts