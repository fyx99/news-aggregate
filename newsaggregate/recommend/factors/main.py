import traceback
from typing import List

from db.async_postgresql import AsyncDatabase
from recommend.factors.similarity import SimilarityFactor
from recommend.factors.outletrelated import OutletRelatedFactor
from recommend.factors.recency import RecencyFactor
from recommend.factors.viral import ViralFactor
from recommend.factors.rank import RankFactors
from recommend.factors.general import FactorSetupInput, FactorProcessInput, BaseFactor
import asyncio
from db.async_s3 import AsyncDatalake
import time

from logger import get_logger

logger = get_logger()


class RecommendManager:

    factors: List[BaseFactor] = []

    rank_factor = None

    async def factor_status():

        return [f.json_status() for f in RecommendManager.factors]

    async def setup(db, dl):
        target_factors: List[BaseFactor] = [
            SimilarityFactor(),
            OutletRelatedFactor(),
            RecencyFactor(),
            ViralFactor(),
        ]
        try:
            start = time.time()
            logger.debug("start setup")

            setup_input = await FactorSetupInput.load(db, dl)
            rank_factor = RankFactors()
            rank_factor.setup(setup_input)
            for factor in target_factors:
                factor.setup(setup_input)

            RecommendManager.factors = target_factors
            RecommendManager.rank_factor = rank_factor

            logger.debug(f"Done {time.time() - start}")
        except Exception as e:
            logger.error("SETUP FAILED")
            logger.error(traceback.format_exc())

    async def process(db, user_id):
        try:
            start = time.time()
            if not RecommendManager.rank_factor:
                raise Exception("Not ready")
            process_input = await FactorProcessInput.load(db, user_id)
            ranks = [
                factor.process(process_input)
                for factor in RecommendManager.factors
                if factor.ready
            ]

            top_n_articles = RecommendManager.rank_factor.process(RecommendManager.factors, ranks)

            logger.debug(f"process {time.time() - start}")
            return top_n_articles
        except:
            logger.error("ERROR IN RECOMMEND SERVICE")
            logger.error(traceback.format_exc())
        return False


async def wrap():
    db = AsyncDatabase()
    dl = AsyncDatalake()
    await db.connect()
    await dl.connect()
    await RecommendManager.setup(db, dl)
    await db.close()
    await dl.close()


if __name__ == "__main__":

    asyncio.run(wrap())
