

import traceback
from typing import List, Dict
from db.async_crud.article import get_articles_clean
from db.async_crud.interactions import get_reads_for_user
from feature.preprocessing.general import SimilarityMatrix
from db.async_postgresql import AsyncDatabase
from recommend.factors.similarity import SimilarityFactor
from recommend.factors.outletrelated import OutletRelatedFactor
from recommend.factors.recency import RecencyFactor
from recommend.factors.viral import ViralFactor
from recommend.factors.rank import RankFactors
from recommend.factors.general import FactorSetupInput, FactorProcessInput, BaseFactor
from db.databaseinstance import DatabaseInterface
import asyncio
from db.s3 import Datalake
import time
import numpy as np

from logger import get_logger, timeit
logger = get_logger()

factors: List[BaseFactor] = [
    SimilarityFactor,
    OutletRelatedFactor,
    RecencyFactor,
    ViralFactor
]

@timeit
async def setup(db, dl):
    try:
        start = time.time()
        logger.debug("start setup")

        setup_input = await FactorSetupInput.load(db, dl)
        RankFactors.setup(setup_input)
        for factor in factors:
            factor.setup(setup_input)

        logger.debug(f"Done {time.time() - start}")
    except Exception as e:
        logger.error("SETUP FAILED")
        logger.error(traceback.format_exc())

async def process(db, user_id):
    try:
        start = time.time()
        process_input = await FactorProcessInput.load(db, user_id)
        ranks = [factor.process(process_input) for factor in factors if factor.ready]

    
        top_n_articles = RankFactors.process(factors, ranks)

        logger.debug(f"process {time.time() - start}")
        return top_n_articles
    except:
        logger.error("ERROR IN RECOMMEND SERVICE")
        logger.error(traceback.format_exc())
    return False


@timeit
def main(db, dl, user_id):
    
    setup_input = FactorSetupInput(get_articles_clean(db), [SimilarityMatrix.load(db, dl, type) for type in ["BertProcessorDistDESimilarity", "TfidfProcessorSimilarity"]])
    
    process_input = FactorProcessInput(user_id, get_reads_for_user(db, user_id))
    
    ViralFactor.setup(db, setup_input)
    
    res = ViralFactor.process(process_input)
    
    logger.debug(res)
    
    RecencyFactor.setup(db, setup_input)
    
    res = RecencyFactor.process(process_input)
    
    logger.debug(res)

    OutletRelatedFactor.setup(db, setup_input)
    
    res = OutletRelatedFactor.process(process_input)
    
    logger.debug(res)

    SimilarityFactor.setup(db, setup_input)
    
    res = SimilarityFactor.process(process_input)
    
    logger.debug(res)
    
    return








@timeit
def debug(db: DatabaseInterface):
    
    setup_input = FactorSetupInput(get_articles_clean(db), [SimilarityMatrix.load(db, type) for type in ["BertProcessorDistDESimilarity", "TfidfProcessorSimilarity"]])
    
    tesT_article_ids = [305739, 1573, 1574]
    user_id = "74d06a24-ae32-4cf3-be20-a8d98be251b4"
    process_input = FactorProcessInput(user_id, get_reads_for_user(db, user_id))
    
    ViralFactor.setup(db, setup_input)
    
    res = ViralFactor.process(process_input)
    
    logger.debug(res)
    
    RecencyFactor.setup(db, setup_input)
    
    res = RecencyFactor.process(process_input)
    
    logger.debug(res)

    OutletRelatedFactor.setup(db, setup_input)
    
    res = OutletRelatedFactor.process(process_input)
    
    logger.debug(res)

    SimilarityFactor.setup(db, setup_input)
    
    res = SimilarityFactor.process(process_input)
    
    logger.debug(res)
    
    return


async def wrap():
    db = AsyncDatabase()
    dl = Datalake()
    await db.connect()
    await setup(db, dl)
    await db.close()

if __name__ == "__main__":

	asyncio.run(wrap())
