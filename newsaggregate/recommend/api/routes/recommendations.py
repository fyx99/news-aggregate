from fastapi import APIRouter, Request
from starlette.responses import JSONResponse

recommendations_router = APIRouter()


@recommendations_router.post("/{user_id}")
async def recommend(request: Request, user_id: str):

    #body = await request.json()
    

    return JSONResponse()
