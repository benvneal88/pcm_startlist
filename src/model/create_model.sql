-- start_list STAGING --

CREATE TABLE IF NOT EXISTS stg_start_list_files(
    data_source text,
    race_year integer,
    race_name text,
    url text,
    blob_content text,
    downloaded_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS stg_start_list_races_files(
    data_source text,
    race_year integer,
    url text,
    blob_content text,
    downloaded_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS stg_start_list_races(
    race_year integer,
    race_name text,
    start_list_url text
);

CREATE TABLE IF NOT EXISTS stg_start_list_cyclists(
    race_year integer,
    race_name text,
    team_name text,
    cyclist_name text,
    cyclist_first_name text,
    cyclist_last_name text
);


-- PCM DB STAGING --

CREATE TABLE IF NOT EXISTS pcm_stg_races(
    database_name text,
    race_id integer,
    race_name text,
    race_abbrreviation text,
    filename text
);


CREATE TABLE IF NOT EXISTS pcm_stg_teams(
    database_name text,
    team_id integer,
    team_name text,
    team_short_name text
);


CREATE TABLE IF NOT EXISTS pcm_stg_cyclists(
    database_name text,
    cyclist_id integer,
    team_id integer,
    cyclist_name text,
    cyclist_last_name text,
    cyclist_first_name text
);


-- MODEL --

CREATE TABLE IF NOT EXISTS tbl_databases(
    id integer PRIMARY KEY,
    name text
);


CREATE TABLE IF NOT EXISTS tbl_teams(
    id integer PRIMARY KEY,
    database_id integer,
    pcm_team_id integer,
    team_name text,
    team_shortname text,
    FOREIGN KEY (database_id) REFERENCES tbl_databases (id)
         ON DELETE CASCADE
         ON UPDATE NO ACTION
);


CREATE TABLE IF NOT EXISTS tbl_races(
    id integer PRIMARY KEY,
    database_id integer,
    pcm_race_id integer,
    race_name text,
    race_abbrreviation text,
    filename text,
    FOREIGN KEY (database_id) REFERENCES tbl_databases (id)
         ON DELETE CASCADE
         ON UPDATE NO ACTION
);


CREATE TABLE IF NOT EXISTS tbl_cyclists(
    id integer PRIMARY KEY,
    team_id integer,
    pcm_cyclist_id integer,
    cyclist_name text,
    cyclist_last_name text,
    cyclist_first_name text,
    FOREIGN KEY (team_id) REFERENCES tbl_teams (id)
         ON DELETE CASCADE
         ON UPDATE NO ACTION
);


CREATE TABLE IF NOT EXISTS tbl_cyclists_races_mtm(
    id integer PRIMARY KEY,
    race_id integer,
    cyclist_id integer,
    FOREIGN KEY (race_id) REFERENCES tbl_races (id)
         ON DELETE CASCADE
         ON UPDATE NO ACTION,
    FOREIGN KEY (cyclist_id) REFERENCES tbl_cyclists (id)
         ON DELETE CASCADE
         ON UPDATE NO ACTION
);
