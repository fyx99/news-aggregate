import numpy as np
from recommend.factors.general import FactorSetupInput, FactorProcessInput, normalize_array, normalize_array_exp, BaseFactor

from logger import get_logger, timeit
logger = get_logger()

class RecencyFactor(BaseFactor):


    @timeit
    def setup(self, setup_input: FactorSetupInput):
        super().setup()

        publish_dates = [article.publish_date for article in setup_input.articles]
        publish_timestamps = np.array([datetime.timestamp() for datetime in publish_dates])

        self.publish_dates = normalize_array(normalize_array_exp(publish_timestamps))

        if self.publish_dates.size == 0:
            return logger.debug("VIRAL FACTOR 0 ELEMENTS")

        self.ready = True

    @timeit
    def process(self, process_input: FactorProcessInput):
        return self.publish_dates