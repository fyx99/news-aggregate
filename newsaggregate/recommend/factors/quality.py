import numpy as np
from recommend.factors.general import FactorSetupInput, FactorProcessInput, normalize_array, BaseFactor

from logger import get_logger, timeit
logger = get_logger()

class QualityFactor(BaseFactor):

    @timeit
    def setup(setup_input: FactorSetupInput):


        texts = [article.text for article in setup_input.articles]
        text_lengths = np.array([max(len(text), 7000) for text in texts])

        QualityFactor.text_quality = normalize_array(text_lengths)


        QualityFactor.ready = True

    @timeit
    def process(process_input: FactorProcessInput):
        return QualityFactor.text_quality