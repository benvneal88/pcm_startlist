-- STARTLIST STAGING --

CREATE TABLE IF NOT EXISTS stg_startlist_files(
    data_source text,
    year integer,
    race_name text,
    url text,
    blob_content blob,
    downloaded_at text
);

CREATE TABLE IF NOT EXISTS stg_startlist_cyclists(
    year integer,
    race_name text,
    team_name text,
    cyclist_name text,
    cyclist_first_name text,
    cyclist_last_name text
);


-- PCM DB STAGING --
--
--CREATE TABLE IF NOT EXISTS pcm_stg_races(
--    race_id integer,
--    race_name text,
--    race_abbrreviation text,
--    race_filename text,
--);
--
--
--CREATE TABLE IF NOT EXISTS pcm_stg_teams(
--    team_id integer,
--    team_name text,
--    team_shortname text,
--);
--
--
--CREATE TABLE IF NOT EXISTS pcm_stg_cyclists(
--    cyclist_id integer,
--    cyclist_name text,
--    cyclist_last_name text,
--    cyclist_first_name text,
--    team_id integer
--);
--
--
---- MODEL --
--
--CREATE TABLE IF NOT EXISTS tbl_editions(
--    id integer PRIMARY KEY,
--    name text,
--);
--
--
--CREATE TABLE IF NOT EXISTS tbl_teams(
--    id integer PRIMARY KEY,
--    edition_id integer,
--    pcm_team_id integer,
--    team_name text,
--    team_shortname text,
--    FOREIGN KEY (edition_id) REFERENCES tbl_editions (id)
--         ON DELETE CASCADE
--         ON UPDATE NO ACTION,
--);
--
--
--CREATE TABLE IF NOT EXISTS tbl_races(
--    id integer PRIMARY KEY,
--    edition_id integer,
--    pcm_race_id integer,
--    race_name text,
--    race_abbrreviation text,
--    race_filename text,
--    FOREIGN KEY (edition_id) REFERENCES tbl_editions (id)
--         ON DELETE CASCADE
--         ON UPDATE NO ACTION,
--);
--
--
--CREATE TABLE IF NOT EXISTS tbl_cyclists(
--    id integer PRIMARY KEY,
--    team_id integer,
--    pcm_cyclist_id integer,
--    cyclist_name text,
--    cyclist_last_name text,
--    cyclist_first_name text,
--    FOREIGN KEY (team_id) REFERENCES tbl_teams (id)
--         ON DELETE CASCADE
--         ON UPDATE NO ACTION,
--);
--
--
--CREATE TABLE IF NOT EXISTS tbl_cyclists_races_mtm(
--    id integer PRIMARY KEY,
--    race_id integer,
--    cyclist_id integer,
--    FOREIGN KEY (race_id) REFERENCES tbl_races (id)
--         ON DELETE CASCADE
--         ON UPDATE NO ACTION,
--    FOREIGN KEY (cyclist_id) REFERENCES tbl_cyclists (id)
--         ON DELETE CASCADE
--         ON UPDATE NO ACTION,
--);
