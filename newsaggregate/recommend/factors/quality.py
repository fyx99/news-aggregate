import numpy as np
from recommend.factors.general import FactorSetupInput, FactorProcessInput, normalize_array

from logger import get_logger, timeit
logger = get_logger()

class QualityFactor:

    @timeit
    def setup(setup_input: FactorSetupInput):


        texts = [article.text for article in setup_input.articles]
        text_lengths = np.array([max(len(text), 7000) for text in texts])

        QualityFactor.text_quality = normalize_array(text_lengths)

    @timeit
    def process(process_input: FactorProcessInput):
        return QualityFactor.text_quality