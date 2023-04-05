from uuid import UUID

from api.v1.utils import raise_exception_if_not_found, to_response_model
from core.config import Config
from fastapi import APIRouter, Depends, Query
from models.schemas import MovieDetail, MovieList, SortField
from services.movies import MovieService, get_service

router = APIRouter(prefix='/movies', tags=['Movies'])


@router.get(
    path='',
    name='Movies List',
    description='Get a list of all movies with optional filtering by genre and sorting by IMDb rating',
    response_model=list[MovieList],
    response_model_exclude_unset=True,
)
async def get_movies_list(
    sort: SortField = Query(default=SortField.imdb_rating_desc),
    genre_id: UUID = None,
    page_number: int = Query(default=0, ge=0),
    page_size: int = Query(default=Config.PROJECT_GLOBAL_PAGE_SIZE, gt=0),
    movie_service: MovieService = Depends(get_service),
) -> list[MovieList]:
    """
    Get a list of all movies with optional filtering by genre and sorting by IMDb rating.
    """
    sort_field = sort.value
    sort_type = 'desc' if sort_field.startswith('-') else 'asc'
    if sort_type == 'desc':
        sort_field = sort_field[1:]
    movies_list = await movie_service.get_sorted_movies(
        page_number=page_number,
        page_size=page_size,
        sort_field=sort_field,
        sort_type=sort_type,
        genre_id=genre_id,
    )
    raise_exception_if_not_found(movies_list, 'No movies found')
    return to_response_model(movies_list, MovieList)


@router.get(
    path='/search',
    name='Search Movies',
    description='Search for movies by title and paginate the results',
    response_model=list[MovieList],
    response_model_exclude_unset=True,
)
async def get_movies_by_search(
    query: str,
    page_number: int = Query(default=0, ge=0),
    page_size: int = Query(default=Config.PROJECT_GLOBAL_PAGE_SIZE, gt=0),
    movie_service: MovieService = Depends(get_service),
) -> list[MovieList]:
    """
    Search for movies by title and paginate the results.
    """
    movies_list = await movie_service.get_movies_by_search(
        query, page_number, page_size
    )
    raise_exception_if_not_found(movies_list, 'No movies found')
    return to_response_model(movies_list, MovieList)


@router.get(
    path='/{movie_id}',
    name='Movie Details',
    description='Get detailed information about a specific movie by its ID',
    response_model=MovieDetail,
    response_model_exclude_unset=True,
)
async def get_movie_details(
    movie_id: UUID, movie_service: MovieService = Depends(get_service)
) -> MovieDetail:
    """
    Get detailed information about a specific movie by its ID.
    """
    movie = await movie_service.get_movie_by_id(movie_id)
    raise_exception_if_not_found(movie, 'Movie not found')
    return movie


@router.get(
    path='/{movie_id}/similar',
    name='Similar Movies',
    description='Get a list of movies similar to the specified movie, based on genre',
    response_model=list[MovieList],
    response_model_exclude_unset=True,
)
async def get_similar_movies(
    movie_id: UUID, movie_service: MovieService = Depends(get_service)
) -> list[MovieList]:
    """
    Get a list of movies similar to the specified movie, based on genre.
    """
    movies_list = await movie_service.get_similar_movies(movie_id)
    raise_exception_if_not_found(movies_list, 'No similar movies found')
    return to_response_model(movies_list, MovieList)


@router.get(
    path='/genres/{genre_id}',
    name='Popular Movies in Genre',
    description='Get a list of the most popular movies in a specific genre',
    response_model=list[MovieList],
    response_model_exclude_unset=True,
)
async def get_popular_in_genre(
    genre_id: UUID, movie_service: MovieService = Depends(get_service)
) -> list[MovieList]:
    """
    Get a list of the most popular movies in a specific genre.
    """
    movies_list = await movie_service.get_popular_movies_by_genre(genre_id)
    raise_exception_if_not_found(movies_list, 'No movies found in the specified genre')
    return to_response_model(movies_list, MovieList)
