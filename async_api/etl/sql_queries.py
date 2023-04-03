MOVIE_SQL_QUERY = """
    SELECT
        film_work.id,
        film_work.title,
        film_work.description,
        film_work.rating,
        film_work.type,
        film_work.created_at,
        film_work.updated_at,
        film_work.creation_date,
        film_work.file_path,
        COALESCE (json_agg(
        DISTINCT jsonb_build_object(
           'role', person_film_work.role,
           'id', person.id,
           'full_name', person.full_name
       )
    ) FILTER (WHERE person.id is not null), '[]') as all_persons,
        COALESCE (json_agg(
        DISTINCT jsonb_build_object(
            'id', genre.id,
            'name', genre.name,
            'description', genre.description
        )
    ) FILTER (WHERE genre.id is not null), '[]') as all_genres
    FROM content.film_work
    LEFT JOIN content.person_film_work ON person_film_work.film_work_id = film_work.id
    LEFT JOIN content.person ON person.id = person_film_work.person_id
    LEFT JOIN content.genre_film_work ON genre_film_work.film_work_id = film_work.id
    LEFT JOIN content.genre ON genre.id = genre_film_work.genre_id
    WHERE film_work.updated_at > %s
    GROUP BY film_work.id
"""

GENRE_SQL_QUERY = """
    SELECT
        genre.id,
        genre.name,
        genre.description,
        genre.updated_at
    FROM content.genre
    WHERE genre.updated_at > %s;
"""

PERSON_SQL_QUERY = """
    SELECT
        person.id,
        person.full_name,
        person.updated_at,
        COALESCE (json_agg(
        DISTINCT jsonb_build_object(
           'id', film_work.id,
           'title', film_work.title,
           'rating', film_work.rating,
           'type', film_work.type
       )
   ) FILTER (WHERE film_work.id is not null), '[]') as all_movies,
    array_agg(DISTINCT person_film_work.role) as roles
    FROM content.person
    LEFT JOIN content.person_film_work ON person_film_work.person_id = person.id
    LEFT JOIN content.film_work ON film_work.id = person_film_work.film_work_id
    WHERE person.updated_at > %s
    GROUP BY person.id
"""

ALL_SQL_QUERIES = {
    'movies': MOVIE_SQL_QUERY,
    'genres': GENRE_SQL_QUERY,
    'persons': PERSON_SQL_QUERY,
}
