import configparser


#  ----------------- CONFIG  -----------------
config = configparser.ConfigParser()
config.read('dwh.cfg')

# -------------- DROP TABLES  -----------------

staging_events_table_drop = "DROP TABLE IF EXISTS staging_events;"
staging_songs_table_drop = "DROP TABLE IF EXISTS staging_songs;"
songplay_table_drop = "DROP TABLE IF EXISTS songplay;"
users_table_drop = "DROP TABLE IF EXISTS users;"
songs_table_drop = "DROP TABLE IF EXISTS songs;"
artists_table_drop = "DROP TABLE IF EXISTS artists;"
time_table_drop = "DROP TABLE IF EXISTS time;"

# ------------- CREATE TABLES  -----------------

staging_songs_table_create = ("""
    CREATE TABLE IF NOT EXISTS staging_songs(
        num_songs INTEGER,
        artist_id VARCHAR,
        artist_latitude FLOAT,
        artist_longitude FLOAT,
        artist_location VARCHAR(MAX),
        artist_name VARCHAR(MAX),
        song_id VARCHAR,
        title VARCHAR(MAX),
        duration FLOAT,
        year SMALLINT
     );
    """)

staging_events_table_create = ("""
    CREATE TABLE IF NOT EXISTS staging_events (
        artist VARCHAR(MAX),
        auth VARCHAR,
        firstName VARCHAR(MAX),
        gender CHAR(1),
        itemInSession INTEGER,
        lastName VARCHAR(MAX),
        length FLOAT,
        level VARCHAR,
        location VARCHAR(MAX),
        method VARCHAR,
        page VARCHAR,
        registration FLOAT,
        sessionId INTEGER,
        song VARCHAR(MAX),
        status INTEGER,
        ts BIGINT,
        userAgent VARCHAR,
        userId INTEGER
    );
""")

songplay_table_create = ("""
    CREATE TABLE IF NOT EXISTS songplay(
        songplay_id INTEGER IDENTITY(0,1) PRIMARY KEY,
        start_time TIMESTAMP NOT NULL SORTKEY DISTKEY,
        user_id INTEGER NOT NULL,
        level VARCHAR,
        song_id VARCHAR NOT NULL,
        artist_id VARCHAR NOT NULL,
        session_id INTEGER,
        location VARCHAR(MAX), 
        user_agent VARCHAR
    );
""")

songs_table_create = ("""
    CREATE TABLE IF NOT EXISTS songs(
        song_id VARCHAR PRIMARY KEY SORTKEY, 
        title VARCHAR(MAX) NOT NULL, 
        artist_id VARCHAR NOT NULL, 
        year SMALLINT NOT NULL,
        duration FLOAT
    );
""")

artists_table_create = ("""
    CREATE TABLE IF NOT EXISTS artists(
        artist_id VARCHAR PRIMARY KEY SORTKEY, 
        name VARCHAR(MAX) NOT NULL,
        location VARCHAR(MAX), 
        latitude FLOAT, 
        longitude FLOAT
    );
""")

users_table_create = ("""
    CREATE TABLE IF NOT EXISTS users(
        user_id INTEGER PRIMARY KEY SORTKEY, 
        first_name VARCHAR NOT NULL, 
        last_name VARCHAR NOT NULL, 
        gender CHAR(1), 
        level VARCHAR NOT NULL
    );
""")

time_table_create = ("""
    CREATE TABLE IF NOT EXISTS time(
        start_time TIMESTAMP PRIMARY KEY SORTKEY DISTKEY ,
        hour SMALLINT NOT NULL,
        day SMALLINT NOT NULL,
        week SMALLINT NOT NULL,
        month SMALLINT NOT NULL,
        year SMALLINT NOT NULL,
        weekday SMALLINT NOT NULL
    );
""")
 
# ----------------- COPY TO STAGING TABLES  -----------------

staging_songs_copy = ("""
    COPY staging_songs 
    FROM '{}'
    CREDENTIALS 'aws_iam_role={}'
    REGION '{}' 
    FORMAT AS JSON 'auto';
    """).format(config['S3']['SONG_DATA'], config['IAM_ROLE']['IAM_ROLE_ARN'], config['CLUSTER']['REGION'])

staging_events_copy = ("""
    COPY staging_events
    FROM '{}'
    CREDENTIALS 'aws_iam_role={}'
    REGION '{}'
    FORMAT AS JSON '{}';
    """).format(config['S3']['LOG_DATA'], config['IAM_ROLE']['IAM_ROLE_ARN'], config['CLUSTER']['REGION'], config['S3']['LOG_JSONPATH'])


#  ----------------- FINAL TABLES  -----------------
                
#  ----------------- FACT table  -----------------
                
songplay_table_insert = ("""
    INSERT INTO songplay (start_time, user_id, level, song_id, artist_id, session_id, location, user_agent)
    SELECT  DISTINCT TIMESTAMP 'epoch' + ev.ts/1000 * INTERVAL '1 second' AS start_time,
            ev.userId,
            ev.level,
            s.song_id,
            s.artist_id,
            ev.sessionId,
            ev.location,
            ev.userAgent
    FROM staging_events ev
    JOIN staging_songs s ON (ev.song = s.title AND ev.artist = s.artist_name)
    WHERE ev.page = 'NextSong' AND ev.userId IS NOT NULL;
""")             
                
# DIMENSION tables                
songs_table_insert = ("""
    INSERT INTO songs (song_id, title, artist_id, year, duration) 
        SELECT DISTINCT 
                    song_id, 
                    title, 
                    artist_id, 
                    year, 
                    duration
        FROM staging_songs
        WHERE song_id IS NOT NULL;
""")

artists_table_insert = ("""
    INSERT INTO artists (artist_id, name, location, latitude, longitude)
    SELECT DISTINCT artist_id,
           artist_name,
           artist_location,
           artist_latitude,
           artist_longitude
    FROM staging_songs
    WHERE artist_id IS NOT NULL;
""")

users_table_insert = ("""
    INSERT INTO users (user_id, first_name, last_name, gender, level)
    SELECT DISTINCT userId,
            firstName, 
            lastName, 
            gender, 
            level
    FROM staging_events
    WHERE userId IS NOT NULL AND page = 'NextSong';
""")
                
time_table_insert = ("""
    INSERT INTO time (start_time, hour, day, week, month, year, weekday)
    SELECT DISTINCT (TIMESTAMP 'epoch' + (ts / 1000) * INTERVAL '1 Second ') as tstamp,
           EXTRACT(HOUR FROM tstamp),
           EXTRACT(DAY FROM tstamp),
           EXTRACT(WEEK FROM tstamp),
           EXTRACT(MONTH FROM tstamp),
           EXTRACT(YEAR FROM tstamp),
           EXTRACT(DOW FROM tstamp)
    FROM staging_events
    WHERE ts IS NOT NULL AND page = 'NextSong';
""")
                
# Creating QUERY LISTS
create_table_queries = [staging_songs_table_create, staging_events_table_create, songplay_table_create, songs_table_create, artists_table_create, users_table_create, time_table_create]
drop_table_queries = [staging_songs_table_drop, staging_events_table_drop, songplay_table_drop, songs_table_drop, artists_table_drop, users_table_drop, time_table_drop]
copy_table_queries = [staging_songs_copy, staging_events_copy]
insert_table_queries = [songplay_table_insert, songs_table_insert, artists_table_insert, users_table_insert, time_table_insert]
