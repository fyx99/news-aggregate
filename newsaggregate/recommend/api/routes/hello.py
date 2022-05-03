from fastapi import APIRouter

hello_router = APIRouter()


@hello_router.get("/")
async def home():
    return "Hello World"

    
@hello_router.get("/hello")
async def hello():
    return "Hello Helloo World"