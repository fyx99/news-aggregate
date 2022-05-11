import asyncio
from logger import timeit
from fastapi import FastAPI
from db.async_postgresql import AsyncDatabase




async def compute_intensive_work(n):
    # j = 0
    # for i in range(n):
    #     j += i % 100000

    

    await db.query("SELECT pg_sleep(0.2);")



async def io_intensive_work():
    j = 0
    for i in range(100000000):
        j += i % 100000
    
    print("seelct")
    await db_back.query("SELECT pg_sleep(30);")

    

async def background_task():
    print("execute task")
    #compute_intensive_work(90000000)
    print("finish task")
    await io_intensive_work()
    print("finish task io")
    

app = FastAPI()
db = AsyncDatabase() 
db_back = AsyncDatabase() 

async def background_function(param):
    loop = asyncio.get_running_loop()
    while True:
        await background_task()
        # await loop.run_in_executor(
        #     executor=None, func=background_task
        # )
        await asyncio.sleep(20)

task = None
@app.on_event("startup")
async def load_mem_loader():
    await db.connect()
    await db_back.connect(1,1)

    task = asyncio.create_task(
        background_function("hey")
    )


@app.on_event("shutdown")
async def cancel_mem_loader():
    task.cancel() if task else 0
    print("CHECK TASK CANCELED")



@app.get("/content")
async def get_content():
    return await compute_intensive_work(1000000)

import uvicorn


if __name__ == "__main__":
    uvicorn.run(app, log_level="debug")