CREATE ROLE dataset WITH UNENCRYPTED PASSWORD 'dataset';
ALTER ROLE dataset WITH LOGIN;
CREATE DATABASE dataset OWNER 'test';
-- REVOKE ALL PRIVILEGES ON DATABASE dataset FROM public;

-- GRANT ALL PRIVILEGES ON DATABASE dataset TO dataset;

ALTER DATABASE dataset SET search_path = public, postgis;
\c dataset

CREATE EXTENSION IF NOT EXISTS postgis ;

CREATE TYPE levl AS ENUM ('country', 'NUTS1', 'NUTS2', 'NUTS3', 'LAU', 'geometry');

CREATE TABLE public.datasets
(
    ds_id int PRIMARY KEY,
    metadata jsonb
);

CREATE TABLE public.spatial
(
    fid varchar(200) PRIMARY KEY,
    name varchar(200),
    name_engl varchar(200),
    cntr_code char(2),
    levl_code levl,
    ds_id int,
    geometry geometry(Geometry,3035)
);

CREATE TABLE public.data
(
    index SERIAL PRIMARY KEY,
    start_at timestamp without time zone,
    fields jsonb,
    variable varchar(200),
    unit varchar(200),
    value double precision,
    ds_id int,
    fid varchar(200),
    dt double precision,
    z double precision,
    isRaster boolean
);


ALTER TABLE spatial
    ADD CONSTRAINT fk_ds_id
    FOREIGN KEY(ds_id) 
    REFERENCES datasets(ds_id)
    ON DELETE CASCADE
;

ALTER TABLE data
    ADD CONSTRAINT fk_ds_id
    FOREIGN KEY(ds_id) 
    REFERENCES datasets(ds_id)
    ON DELETE CASCADE
;


-- POSTGREST
CREATE ROLE api_anon nologin;
grant usage on schema public to api_anon;
grant api_anon to test;

create role api_user nologin;
grant api_user to test;

grant usage on schema public to api_user;
grant SELECT on public.spatial to api_user;
grant SELECT on public.data to api_user;
grant SELECT on public.datasets to api_user;
-- grant usage, select on sequence api.todos_id_seq to todo_user;