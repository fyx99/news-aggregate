

import traceback
from typing import List, Dict
from db.async_crud.article import get_articles_clean
from db.async_crud.interactions import get_reads_for_user
from feature.preprocessing.general import SimilarityMatrix
from db.async_postgresql import AsyncDatabase
from db.async_crud.interactions import get_read_counts, get_preferences_for_user
from recommend.factors.similarity import SimilarityFactor
from recommend.factors.outletrelated import OutletRelatedFactor
from recommend.factors.recency import RecencyFactor
from recommend.factors.viral import ViralFactor
from recommend.factors.rank import RankFactors
from recommend.factors.general import FactorSetupInput, FactorProcessInput
from db.databaseinstance import DatabaseInterface
import asyncio
from db.s3 import Datalake
import time
import numpy as np

from logger import get_logger, timeit
logger = get_logger()

factors = [
    SimilarityFactor,
    OutletRelatedFactor,
    RecencyFactor,
    ViralFactor
]

@timeit
async def setup(db, dl):
    try:
        start = time.time()
        print("start setup")
        articles_clean = await get_articles_clean(db)
        print(f"Done Articles Clean {time.time() - start}")
        start = time.time()
        matrix = [await SimilarityMatrix.load(db, dl, type) for type in ["BertProcessorDistDESimilarity", "TfidfProcessorSimilarity"]]
        print(f"Done Matrix {time.time() - start}")
        setup_input = FactorSetupInput(
            articles_clean, 
            matrix,
            await get_read_counts(db)
        )
        for factor in factors:
            factor.setup(setup_input)

        RankFactors.setup(setup_input)
        print(f"Done {time.time() - start}")
    except Exception as e:
        logger.error(traceback.format_exc())

async def process(db, user_id):
    start = time.time()
    process_input = FactorProcessInput(
        user_id, 
        await get_reads_for_user(db, user_id),
        await get_preferences_for_user(db, user_id)
    )
    #potential speed up on awaiting all together

    ranks = [factor.process(process_input) for factor in factors ]

  
    top_n_articles = RankFactors.process(factors, ranks)

    print(f"process {time.time() - start}")
    return top_n_articles

@timeit
def main(db, dl, user_id):
    
    setup_input = FactorSetupInput(get_articles_clean(db), [SimilarityMatrix.load(db, dl, type) for type in ["BertProcessorDistDESimilarity", "TfidfProcessorSimilarity"]])
    
    process_input = FactorProcessInput(user_id, get_reads_for_user(db, user_id))
    
    ViralFactor.setup(db, setup_input)
    
    res = ViralFactor.process(process_input)
    
    print(res)
    
    RecencyFactor.setup(db, setup_input)
    
    res = RecencyFactor.process(process_input)
    
    print(res)

    OutletRelatedFactor.setup(db, setup_input)
    
    res = OutletRelatedFactor.process(process_input)
    
    print(res)

    SimilarityFactor.setup(db, setup_input)
    
    res = SimilarityFactor.process(process_input)
    
    print(res)
    
    return








@timeit
def debug(db: DatabaseInterface):
    
    setup_input = FactorSetupInput(get_articles_clean(db), [SimilarityMatrix.load(db, type) for type in ["BertProcessorDistDESimilarity", "TfidfProcessorSimilarity"]])
    
    tesT_article_ids = [305739, 1573, 1574]
    user_id = "74d06a24-ae32-4cf3-be20-a8d98be251b4"
    process_input = FactorProcessInput(user_id, get_reads_for_user(db, user_id))
    
    ViralFactor.setup(db, setup_input)
    
    res = ViralFactor.process(process_input)
    
    print(res)
    
    RecencyFactor.setup(db, setup_input)
    
    res = RecencyFactor.process(process_input)
    
    print(res)

    OutletRelatedFactor.setup(db, setup_input)
    
    res = OutletRelatedFactor.process(process_input)
    
    print(res)

    SimilarityFactor.setup(db, setup_input)
    
    res = SimilarityFactor.process(process_input)
    
    print(res)
    
    return


async def wrap():
    db = AsyncDatabase()
    dl = Datalake()
    await db.connect()
    await setup(db, dl)
    await db.close()

if __name__ == "__main__":

	asyncio.run(wrap())
