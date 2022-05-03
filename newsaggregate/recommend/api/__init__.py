from fastapi import APIRouter

from recommend.api.routes.hello import hello_router
from recommend.api.routes.recommendations import recommendations_router


router = APIRouter()

router.include_router(hello_router, prefix="/hello")
router.include_router(recommendations_router, prefix="/recommendations")