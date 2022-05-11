import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from starlette.middleware.gzip import GZipMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse

import uvicorn
from recommend.factors.main import setup

from recommend.api import router as endpoint_router
from db.async_postgresql import AsyncDatabase


db = AsyncDatabase()
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


@app.on_event("startup")
async def on_app_start():
    """Anything that needs to be done while app starts
    """
    await db.connect()
    await db_back.connect(1,1)

    task = asyncio.create_task(setup(db_back))
    


@app.on_event("shutdown")
async def on_app_shutdown():
    """Anything that needs to be done while app shutdown
    """
    db.close()
    db_back.close()
    task.cancel() if task else 0


@app.get("/ping")
async def ping():
    """
    """
    return Response("Pong")


@app.get("/json")
async def json():
    """json
    """
    return JSONResponse({"hello":"world"})


if __name__ == "__main__":
    uvicorn.run(app, log_level="debug", reload=True)








