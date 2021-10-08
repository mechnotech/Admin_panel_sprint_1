from dataclasses import dataclass, asdict


@dataclass
class CommonTable:
    @property
    def get_fields(self):
        return ', '.join(asdict(self).keys())

    @property
    def get_values(self):
        return asdict(self).values()

    @property
    def get_len(self):
        return len(asdict(self))


@dataclass
class Movie(CommonTable):
    __slots__ = (
        'id', 'title', 'description', 'creation_date', 'certificate', 'file_path', 'rating', 'type',
        'created_at', 'updated_at'
    )
    id: str
    title: str
    description: str
    creation_date: str
    certificate: str
    file_path: str
    rating: float
    type: str
    created_at: str
    updated_at: str


@dataclass
class Genre(CommonTable):
    __slots__ = (
        'id', 'name', 'description', 'created_at', 'updated_at'
    )
    id: str
    name: str
    description: str
    created_at: str
    updated_at: str


@dataclass
class Person(CommonTable):
    __slots__ = (
        'id', 'full_name', 'birth_date', 'created_at', 'updated_at'
    )
    id: str
    full_name: str
    birth_date: str
    created_at: str
    updated_at: str


@dataclass
class GenreFilmWork(CommonTable):
    __slots__ = (
        'id', 'film_work_id', 'genre_id', 'created_at'
    )
    id: str
    film_work_id: str
    genre_id: str
    created_at: str


@dataclass
class PersonFilmWork(CommonTable):
    __slots__ = (
        'id', 'film_work_id', 'person_id', 'role', 'created_at'
    )
    id: str
    film_work_id: str
    person_id: str
    role: str
    created_at: str
