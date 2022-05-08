from fastapi import APIRouter, Request
from starlette.responses import JSONResponse

recommendations_router = APIRouter()


@recommendations_router.post("/")
async def recommend(request: Request):

    body = await request.json()
    

    return JSONResponse()
