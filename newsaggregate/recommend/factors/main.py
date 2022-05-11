

from typing import List, Dict
from db.crud.article import get_articles_clean
from db.crud.interactions import get_reads_for_user
from feature.preprocessing.general import SimilarityMatrix
from db.async_postgresql import AsyncDatabase
from db.crud.interactions import get_read_counts
from recommend.factors.similarity import SimilarityFactor
from recommend.factors.outletrelated import OutletRelatedFactor
from recommend.factors.recency import RecencyFactor
from recommend.factors.viral import ViralFactor
from recommend.factors.general import FactorSetupInput, FactorProcessInput
from db.databaseinstance import DatabaseInterface

from db.postgresql import Database
from db.s3 import Datalake


from logger import get_logger, timeit
logger = get_logger()

factors = [
    SimilarityFactor,
    OutletRelatedFactor,
    RecencyFactor,
    ViralFactor
]

@timeit
async def setup(db: DatabaseInterface):
    setup_input = FactorSetupInput(
        await get_articles_clean(db), 
        [await SimilarityMatrix.load(db, type) for type in ["BertProcessorDistDESimilarity", "TfidfProcessorSimilarity"]],
        get_read_counts(db)
    )
    for factor in factors:
        factor.setup(setup_input)


@timeit
def main(db: DatabaseInterface, user_id):
    
    setup_input = FactorSetupInput(get_articles_clean(db), [SimilarityMatrix.load(db, type) for type in ["BertProcessorDistDESimilarity", "TfidfProcessorSimilarity"]])
    
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

if __name__ == "__main__":
	    
    
	with Database() as db, Datalake() as dl :
		di = DatabaseInterface(db, dl, 'None')
		debug(di)
		
