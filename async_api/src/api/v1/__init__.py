from fastapi import APIRouter

from api.v1.genres import router as genres_router
from api.v1.movies import router as movies_router
from api.v1.persons import router as persons_router

router = APIRouter(prefix='/v1')

router.include_router(movies_router)
router.include_router(genres_router)
router.include_router(persons_router)
