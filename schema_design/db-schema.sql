CREATE SCHEMA IF NOT EXISTS content;
SET search_path TO content,public;

CREATE TABLE IF NOT EXISTS content.film_work (
    id uuid PRIMARY KEY,
    title text NOT NULL,
    description text,
    creation_date date,
    certificate text,
    file_path text,
    rating float,
    type text,
    created_at timestamptz,
    updated_at timestamptz
);

CREATE TABLE IF NOT EXISTS content.genre (
    id uuid PRIMARY KEY,
    name text NOT NULL,
    description text,
    created_at timestamptz,
    updated_at timestamptz
);

CREATE TABLE IF NOT EXISTS content.person (
    id uuid PRIMARY KEY,
    full_name text NOT NULL,
    birth_date date,
    created_at timestamptz,
    updated_at timestamptz
);


CREATE TABLE IF NOT EXISTS content.genre_film_work (
    id uuid PRIMARY KEY,
    film_work_id uuid NOT NULL,
    genre_id uuid NOT NULL,
    created_at timestamptz
);

CREATE TABLE IF NOT EXISTS content.person_film_work (
    id uuid PRIMARY KEY,
    film_work_id uuid NOT NULL,
    person_id uuid NOT NULL,
    role text,
    created_at timestamptz
);

CREATE UNIQUE INDEX IF NOT EXISTS film_work_genre ON genre_film_work (film_work_id, genre_id);

CREATE UNIQUE INDEX IF NOT EXISTS film_work_person_role ON person_film_work (film_work_id, person_id, role);
