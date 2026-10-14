from fastapi import APIRouter
from api.v1.price import router as price_router
router = APIRouter(prefix="/api/v1")

router.include_router(price_router)
