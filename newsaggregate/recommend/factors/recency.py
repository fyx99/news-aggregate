import numpy as np
from recommend.factors.general import FactorSetupInput, FactorProcessInput, normalize_array, BaseFactor

from logger import get_logger, timeit
logger = get_logger()

class RecencyFactor(BaseFactor):

    @timeit
    def setup(setup_input: FactorSetupInput):


        publish_dates = [article.publish_date for article in setup_input.articles]
        publish_timestamps = np.array([datetime.timestamp() for datetime in publish_dates])

        RecencyFactor.publish_dates = normalize_array(publish_timestamps)

        RecencyFactor.ready = True

    @timeit
    def process(process_input: FactorProcessInput):
        return RecencyFactor.publish_dates