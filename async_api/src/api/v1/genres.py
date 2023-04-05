from uuid import UUID

from api.v1.utils import raise_exception_if_not_found, to_response_model
from core.config import Config
from fastapi import APIRouter, Depends, Query
from models.schemas import GenreDetail
from services.genres import GenreService, get_service

router = APIRouter(prefix='/genres', tags=['Genres'])


@router.get(
    path='',
    name='Genres List',
    description='Get a list of all movie genres with pagination',
    response_model=list[GenreDetail],
    response_model_exclude_unset=True,
)
async def get_genres_list(
    page_number: int = Query(default=0, ge=0),
    page_size: int = Query(default=Config.PROJECT_GLOBAL_PAGE_SIZE, gt=0),
    genre_service: GenreService = Depends(get_service),
) -> list[GenreDetail]:
    """
    Get a list of all movie genres with pagination.
    """
    genres_list = await genre_service.get_genres_list(
        page_number=page_number, page_size=page_size
    )
    raise_exception_if_not_found(genres_list, 'No genres found')
    return to_response_model(genres_list, GenreDetail)


@router.get(
    path='/search',
    name='Search Genres',
    description='Search for movie genres by their name',
    response_model=list[GenreDetail],
    response_model_exclude_unset=True,
)
async def get_persons_by_search(
    query: str,
    page_number: int = Query(default=0, ge=0),
    page_size: int = Query(default=Config.PROJECT_GLOBAL_PAGE_SIZE, gt=0),
    person_service: GenreService = Depends(get_service),
) -> list[GenreDetail]:
    """
    Search for movie genres by their name.
    """
    genres_list = await person_service.get_genres_by_search(
        query, page_number, page_size
    )
    raise_exception_if_not_found(genres_list, 'No genres found')
    return to_response_model(genres_list, GenreDetail)


@router.get(
    path='/{genre_id}',
    name='Genre Details',
    description='Get detailed information about a specific genre by its ID',
    response_model=GenreDetail,
    response_model_exclude_unset=True,
)
async def get_genre_detail(
    genre_id: UUID, genre_service: GenreService = Depends(get_service)
) -> GenreDetail:
    """
    Get detailed information about a specific genre by its ID.
    """
    genre = await genre_service.get_genre_by_id(genre_id)
    raise_exception_if_not_found(genre, 'Genre not found')
    return GenreDetail(id=genre.id, name=genre.name, description=genre.description)
