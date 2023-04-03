from enum import Enum


class MovieSortingType(str, Enum):
    imdb_rating = 'imdb_rating'
    imdb_rating_desc = '-imdb_rating'
