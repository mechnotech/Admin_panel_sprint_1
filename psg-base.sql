-- CREATE SCHEMA content;

DROP TABLE content.film_work;
DROP TABLE content.genre;
DROP TABLE content.person;
DROP TABLE content.genre_film_work;
DROP TABLE content.person_film_work;
DROP EXTENSION citext;


SET search_path TO content,public;
CREATE EXTENSION citext;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS content.film_work (
    id uuid PRIMARY KEY default gen_random_uuid(),
    title citext NOT NULL UNIQUE CHECK (textlen(title) BETWEEN 3 and 250),
    description VARCHAR(10000),
    creation_date DATE CHECK (creation_date BETWEEN '1900-01-01' and now()),
    certificate VARCHAR(1000),
    file_path VARCHAR(4096),
    rating FLOAT CHECK (rating BETWEEN 0.0 and 9.9),
    type VARCHAR(30) NOT NULL DEFAULT 'movie',
    created_at timestamptz default now(),
    updated_at timestamptz
);

CREATE TABLE IF NOT EXISTS content.genre (
    id uuid PRIMARY KEY default gen_random_uuid(),
    name citext NOT NULL UNIQUE CHECK (textlen(name) between 3 and 30),
    description VARCHAR(1000),
    created_at timestamptz default now(),
    updated_at timestamptz
);

CREATE TABLE IF NOT EXISTS content.person (
    id uuid PRIMARY KEY,
    full_name citext NOT NULL UNIQUE CHECK (textlen(full_name) between 3 and 200),
    birth_date DATE CHECK (birth_date BETWEEN '1900-01-01' and now()),
    created_at timestamptz default now(),
    updated_at timestamptz
);

CREATE FUNCTION content.new_uuid() RETURNS trigger AS $new_uuid$
    BEGIN
        NEW.id := uuid_generate_v5(uuid_ns_x500(), NEW.full_name);
        RETURN NEW;
    END;
$new_uuid$ LANGUAGE plpgsql;

CREATE TRIGGER new_person_uuid BEFORE INSERT ON content.person
    FOR EACH ROW EXECUTE FUNCTION new_uuid();

CREATE TABLE IF NOT EXISTS content.genre_film_work (
    id uuid PRIMARY KEY default gen_random_uuid(),
    film_work_id TEXT NOT NULL,
    genre_id TEXT NOT NULL,
    created_at timestamptz default now()
);

CREATE TABLE IF NOT EXISTS content.person_film_work (
    id uuid PRIMARY KEY default gen_random_uuid(),
    film_work_id TEXT NOT NULL,
    person_id TEXT NOT NULL,
    role citext NOT NULL CHECK (textlen(role) between 3 and 30),
    created_at timestamptz default now()
);

CREATE UNIQUE INDEX IF NOT EXISTS film_work_genre ON genre_film_work (film_work_id, genre_id);

CREATE UNIQUE INDEX IF NOT EXISTS film_work_person_role ON person_film_work (film_work_id, person_id, role);

CREATE FUNCTION content.upd_stamp() RETURNS trigger AS $upd_stamp$
    BEGIN
        NEW.updated_at := current_timestamp;
        RETURN NEW;
    END;
$upd_stamp$ LANGUAGE plpgsql;

CREATE TRIGGER upd_film_stamp BEFORE INSERT OR UPDATE ON content.film_work
    FOR EACH ROW EXECUTE FUNCTION upd_stamp();
CREATE TRIGGER upd_genre_stamp BEFORE INSERT OR UPDATE ON content.genre
    FOR EACH ROW EXECUTE FUNCTION upd_stamp();
CREATE TRIGGER upd_person_stamp BEFORE INSERT OR UPDATE ON content.person
    FOR EACH ROW EXECUTE FUNCTION upd_stamp();




INSERT INTO person (full_name, birth_date)
VALUES ('Ли Кан', '1978-05-31');
--4af6c9c9-0be0-4864-b1e9-7f87dd59ee1f
SELECT uuid_generate_v5(uuid_ns_oid(), 'Star Trek');