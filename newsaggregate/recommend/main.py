import asyncio

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from starlette.middleware.gzip import GZipMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse

import uvicorn
from db.async_s3 import AsyncDatalake
from recommend.factors.main import setup, process

from recommend.api import router as endpoint_router
from db.async_postgresql import AsyncDatabase
import logging
from logger import get_logger
logger = get_logger()


db = AsyncDatabase()
dl = AsyncDatalake()
db_back = AsyncDatabase()
task = None

app = FastAPI(title="data-backend", version="0")
app.add_middleware(GZipMiddleware, minimum_size=1000)

origins = [
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(endpoint_router, prefix="/api")



async def background_function():
    while True:
        await setup(db_back, dl)
        await asyncio.sleep(600)    # refresh every 10min


@app.on_event("startup")
async def on_app_start():
    """Anything that needs to be done while app starts
    """
    logging.getLogger("uvicorn").removeHandler(logging.getLogger("uvicorn").handlers[0])
    await db.connect()
    await db_back.connect(1,1)
    await dl.connect()

    task = asyncio.create_task(background_function())
    


@app.on_event("shutdown")
async def on_app_shutdown():
    """Anything that needs to be done while app shutdown
    """
    db.close()
    db_back.close()
    await dl.close()
    task.cancel() if task else 0


@app.get("/content/{userId}")
async def ping(userId):
    """
    """
    top_articles = await process(db_back, userId)
    if not top_articles:
        raise HTTPException(status_code=500, detail="NO RECOMMENDATIONS FOUND")
    return JSONResponse(top_articles)
    

@app.get("/json")
async def json():
    """json
    """
    return JSONResponse({"hello":"world"})


if __name__ == "__main__":
    
    
    uvicorn.run(app, log_level="debug", host="0.0.0.0", port=8000)#, log_config=uvicorn_log_config)






