import numpy as np
from recommend.factors.general import FactorSetupInput, FactorProcessInput, normalize_array, BaseFactor

from logger import get_logger, timeit
logger = get_logger()

class QualityFactor(BaseFactor):

    @timeit
    def setup(self, setup_input: FactorSetupInput):
        super().setup()

        texts = [article.text for article in setup_input.articles]
        text_lengths = np.array([max(len(text), 7000) for text in texts])

        self.text_quality = normalize_array(text_lengths)


        self.ready = True

    @timeit
    def process(self, process_input: FactorProcessInput):
        return self.text_quality