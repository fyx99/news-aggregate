from fastapi import APIRouter

recommendations_router = APIRouter()


@recommendations_router.get("/")
async def home():
    return "here recommendations"
