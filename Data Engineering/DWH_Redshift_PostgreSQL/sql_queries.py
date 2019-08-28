import configparser


# CONFIG
config = configparser.ConfigParser()
config.read_file(open('dwh.cfg'))

ROLE_ARN     = config.get('IAM_ROLE','ARN')
LOG_DATA     = config.get("S3","LOG_DATA")
SONG_DATA    = config.get("S3","SONG_DATA")
LOG_JSONPATH = config.get("S3","LOG_JSONPATH")


# DROP TABLES

staging_events_table_drop = "DROP TABLE IF EXISTS staging_events"
staging_songs_table_drop  = "DROP TABLE IF EXISTS staging_songs"
songplay_table_drop       = "DROP TABLE IF EXISTS songplay"
user_table_drop           = "DROP TABLE IF EXISTS users"
song_table_drop           = "DROP TABLE IF EXISTS songs"
artist_table_drop         = "DROP TABLE IF EXISTS artists"
time_table_drop           = "DROP TABLE IF EXISTS time"

# CREATE TABLES

staging_events_table_create= ("""
    CREATE TABLE staging_events
    (
        staging_events_id INT IDENTITY(0,1),
        artist VARCHAR,
        auth VARCHAR,
        firstname VARCHAR,
        gender VARCHAR,
        iteminsession INTEGER,
        lastname VARCHAR,
        length DOUBLE PRECISION,
        level VARCHAR,
        location VARCHAR,
        method VARCHAR,
        page VARCHAR,
        registration BIGINT,
        sessionid INTEGER,
        song VARCHAR,
        status INTEGER,
        ts BIGINT,
        useragent VARCHAR,
        userid INTEGER
    );
""")


staging_songs_table_create = ("""
    CREATE TABLE staging_songs 
    (
        staging_songs_id INT IDENTITY(0,1),
        num_songs INTEGER,
        artist_id VARCHAR,
        artist_latitude DOUBLE PRECISION,
        artist_longitude DOUBLE PRECISION,
        artist_location VARCHAR,
        artist_name VARCHAR,
        song_id VARCHAR,
        title VARCHAR,
        duration DOUBLE PRECISION,
        year INTEGER
    );
""")

songplay_table_create = ("""
    CREATE TABLE songplay 
    (
        songplay_id INT IDENTITY(0,1), 
        start_time DATETIME, 
        userid VARCHAR,
        level VARCHAR, 
        session_id INTEGER, 
        location VARCHAR, 
        useragent VARCHAR, 
        song_id VARCHAR, 
        artist_id VARCHAR
    );
""")

user_table_create = ("""
    CREATE TABLE users 
    (
        userid INTEGER, 
        firstname VARCHAR, 
        lastname VARCHAR,
        gender VARCHAR, 
        level VARCHAR
    )
""")


song_table_create = ("""
    CREATE TABLE songs 
    (
        song_id varchar PRIMARY KEY, 
        title varchar, 
        artist_id varchar, 
        year varchar,
        duration float
    )
""")

artist_table_create = ("""
    CREATE TABLE artists 
    (
        artist_id varchar PRIMARY KEY, 
        name varchar, 
        location varchar, 
        latitude DOUBLE PRECISION, 
        longitude DOUBLE PRECISION
    )
""")

time_table_create = ("""
    CREATE TABLE time 
    (
        start_time DATETIME PRIMARY KEY, 
        hour INTEGER, 
        day INTEGER, 
        week INTEGER,
        month VARCHAR, 
        year INTEGER, 
        weekday VARCHAR
    )
""")

# STAGING TABLES

staging_events_copy = ("""
                        copy {} from {}
                        credentials 'aws_iam_role={}' 
                        region 'us-west-2' 
                        json {}
                        ;
                        """).format("staging_events", LOG_DATA, ROLE_ARN , LOG_JSONPATH)

staging_songs_copy = ("""
                        copy {} from {}
                        credentials 'aws_iam_role={}' 
                        region 'us-west-2' 
                        json 'auto'
                        ;
                        """).format("staging_songs", SONG_DATA, ROLE_ARN)
# FINAL TABLES


songplay_table_insert = ("""
    INSERT INTO songplay 
    (start_time, userid, level, session_id, location, useragent, song_id, artist_id)
    SELECT DISTINCT
    TIMESTAMP 'epoch' + ts/1000 *INTERVAL '1 second' AS start_time, 
    e.userid, 
    e.level, 
    e.sessionid,
    e.location,
    e.useragent,
    s.song_id, 
    s.artist_id
    FROM staging_events AS e
    JOIN staging_songs AS s
    ON (e.song = s.title
    AND e.artist = s.artist_name
    AND e.length = s.duration)
    WHERE page = 'NextSong'

""")

user_table_insert = ("""
    INSERT INTO users 
    (userid, firstname, lastname, gender, level)
    SELECT DISTINCT userid, firstname, lastname, gender, level
    FROM staging_events
""")

song_table_insert = song_table_insert = ("""
    INSERT INTO songs 
    (song_id, title, artist_id, year, duration) 
    SELECT DISTINCT song_id, title, artist_id, year, duration
    FROM staging_songs
""")

artist_table_insert = ("""
    INSERT INTO artists (artist_id, name, location, latitude, longitude)
    SELECT DISTINCT artist_id, artist_name AS name, location, artist_latitude AS latitude, artist_longitude AS longitude
    FROM staging_events
    JOIN staging_songs 
    ON artist = artist_name
""")

time_table_insert = ("""
    INSERT INTO time (start_time, hour, day, week, month, year, weekday) 
    SELECT DISTINCT start_time, 
    EXTRACT(hour FROM start_time) as hour, 
    EXTRACT(day FROM start_time) AS day, 
    EXTRACT(week FROM start_time) as week, 
    EXTRACT(month FROM start_time) as month, 
    EXTRACT(year FROM start_time) as year,
    EXTRACT(weekday FROM start_time) as weekday
    FROM songplay
""")

# QUERY LISTS

create_table_queries = [staging_events_table_create, staging_songs_table_create, songplay_table_create, user_table_create, song_table_create, artist_table_create, time_table_create]
drop_table_queries = [staging_events_table_drop, staging_songs_table_drop, songplay_table_drop, user_table_drop, song_table_drop, artist_table_drop, time_table_drop]
copy_table_queries = [staging_events_copy, staging_songs_copy]
insert_table_queries = [songplay_table_insert, user_table_insert, song_table_insert, artist_table_insert, time_table_insert]
