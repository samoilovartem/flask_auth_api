from typing import Union

from backoff import expo, on_exception
from configs import loguru_config, settings_config
from loguru import logger
from pydantic import ValidationError
from schemas import FullPersonData, GenreData, MovieData

logger.add(**loguru_config)


class DataTransformer:
    """A class to validate and transform postgres data with pydantic model."""

    def get_persons_by_role(
        self, persons: list[dict], roles: list[str]
    ) -> dict[str, tuple[list[dict], list[str]]]:
        persons_data_by_role = {}
        for role in roles:
            persons_with_role = [
                {'id': person.get('id'), 'full_name': person.get('full_name')}
                for person in persons
                if person.get('role') == role
            ]
            names_of_persons_with_role = [
                person.get('full_name') for person in persons_with_role
            ]
            persons_data_by_role[role] = (persons_with_role, names_of_persons_with_role)
        return persons_data_by_role

    @on_exception(
        expo, ValidationError, max_tries=settings_config.MAX_TRIES, logger=logger
    )
    def transform_movies_data(
        self,
        movies_data: list[dict],
        index_name: str,
    ) -> list[Union[MovieData, GenreData, FullPersonData]]:
        es_data = []
        if index_name == 'movies':
            for movie in movies_data:
                persons = self.get_persons_by_role(
                    persons=movie.get('all_persons'),
                    roles=['director', 'actor', 'writer'],
                )
                genres = [
                    GenreData(
                        id=genre.get('id'),
                        name=genre.get('name'),
                        description=genre.get('description'),
                    )
                    for genre in movie.get('all_genres')
                ]
                movie_data = MovieData(
                    id=movie.get('id'),
                    imdb_rating=movie.get('rating'),
                    type=movie.get('type'),
                    creation_date=movie.get("creation_date"),
                    genres=genres,
                    title=movie.get('title'),
                    file_path=movie.get("file_path"),
                    description=movie.get('description'),
                    directors_names=persons.get('director')[1],
                    actors_names=persons.get('actor')[1],
                    writers_names=persons.get('writer')[1],
                    directors=persons.get('director')[0],
                    actors=persons.get('actor')[0],
                    writers=persons.get('writer')[0],
                )
                es_data.append(movie_data)
            return es_data
        elif index_name == 'genres':
            for genre in movies_data:
                genre_data = GenreData(
                    id=genre.get('id'),
                    name=genre.get('name'),
                    description=genre.get('description'),
                )
                es_data.append(genre_data)
            return es_data
        else:
            for person in movies_data:
                person_data = FullPersonData(
                    id=person.get('id'),
                    full_name=person.get('full_name'),
                    roles=person.get('roles'),
                    movies_ids=[movie.get('id') for movie in person.get('all_movies')],
                )
                es_data.append(person_data)
            return es_data
