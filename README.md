# Project: Data Warehouse with AWS

A music streaming startup, **Sparkify**, has grown their user base and song database even more and want to move their data warehouse to a data lake. Their data resides in S3, in a directory of JSON logs on user activity on the app, as well as a directory with JSON metadata on the songs in their app.

Goal of the project - build an ETL pipeline that extracts their data from *AWS S3*, stages them in *AWS Redshift* and executes SQL statements that will create the analytics dimensional tables from the staging tables and save them on *AWS Redshift*. Analytics team will use these dimensional tables for finding insights in what songs their users are listening to

### Project Datasets

* Song data: `s3://udacity-dend/song_data`
* Log data: `s3://udacity-dend/log_data`

#### 1. Song Dataset
The first dataset is a subset of real data from the Million Song Dataset. Each file is in JSON format and contains metadata about a song and the artist of that song. 

The files are partitioned by the first three letters of each song's track ID. For example, here are file paths to two files in this dataset.

```
song_data/A/B/C/TRABCEI128F424C983.json
song_data/A/A/B/TRAABJL12903CDCF1A.json
```
###### *Example of file (TRAABJL12903CDCF1A.json):*
```
{"num_songs": 1, "artist_id": "ARJIE2Y1187B994AB7", "artist_latitude": null, 
"artist_longitude": null, "artist_location": "", "artist_name": "Line Renaud", 
"song_id": "SOUPIRU12A6D4FA1E1", "title": "Der Kleine Dompfaff", 
"duration": 152.92036, "year": 0}
```

#### 2. Log Dataset
The second dataset is log files in JSON format generated an event simulator based on the songs in the dataset above. These simulate app activity logs from an imaginary music streaming app based on configuration settings.

The log files in the dataset are partitioned by year and month. For example, here are file paths to two files in this dataset.

```
     log_data/2018/11/2018-11-12-events.json
     log_data/2018/11/2018-11-13-events.json
```
###### *Example of file (2018-11-12-events.json):*

```
{"artist":"Slipknot", "auth":"LoggedIn", "firstName":"Aiden", "gender":"M",
"itemInSession":0,"lastName":"Ramirez", "length":192.57424,"level":"paid",
"location":"New York-Newark-Jersey City, NY-NJ-PA", "method":"PUT", 
"page":"NextSong", "registration":1540283578796.0,"sessionId":19,
"song":"Opium Of The People (Album Version)", "status":200, 
"userAgent":"\"Mozilla\/5.0 (Windows NT 6.1) AppleWebKit\/537.36 (KHTML, like Gecko) Chrome\/36.0.1985.143 Safari\/537.36\"",
"ts":1541639510796,"userId":"20"}
```


## Project structure

* `dwh.cfg` - Config file with credentials and paths

```
        [CLUSTER]
        HOST=<end point to AWS redshift Cluster>
        DB_NAME=<name of database>
        DB_USER=<username in database DB_NAME>
        DB_PASSWORD=<password for username in database DB_NAME>
        DB_PORT=5439
        REGION=us-west-2

        [IAM_ROLE]
        IAM_ROLE_ARN=<arn IAM Role>

        [S3]
        SONG_DATA=s3a://udacity-dend/song-data
        LOG_DATA=s3a://udacity-dend/log-data
        LOG_JSONPATH=s3a://udacity-dend/log_json_path.json
```

* `create_db_conn_str.py` - Python script creates connection string to DB using dwh.cfg['CLUSTER']

* `create_tables.py` - Python script for creating all needed tables

* `sql_queries.py` - Python script for defining all SQL queries that will be used in sripts create_tables.py and etl.py

* `etl.py` - Python script that extracts songs data and log data from AWS S3, copies data from them to staging tables on Redshift Cluster, 
    and then creates fact table and dimensional tables on Redshift Cluster.

* `README.md` - Current file, contains detailed information about the project.

## Data Schema

### Staging Tables

#### staging_songs

column name | type
------------- | -------------
num_songs | INTEGER
artist_id | VARCHAR 
artist_latitude | FLOAT 
artist_longitude | FLOAT 
artist_location | VARCHAR 
artist_name | VARCHAR 
song_id | VARCHAR 
title | VARCHAR 
duration | FLOAT
year | SMALLINT

#### staging_events

column name | type
------------- | -------------
artist | VARCHAR
auth | VARCHAR
firstName | VARCHAR
gender | CHAR(1)
itemInSession | INTEGER
lastName | VARCHAR
length | FLOAT
level | VARCHAR
location | VARCHAR
method | VARCHAR
page | VARCHAR
registration | FLOAT
sessionId | INTEGER
song | VARCHAR
status | INTEGER
ts | BIGINT
userAgent | VARCHAR
userId | INTEGER

### Fact Table

#### songplay - records in log data associated with song plays (records with page = "NextSong")

*sorted by start_time* \
*distributed by start_time*

column name | type
------------- | -------------
songplay_id | INTEGER
start_time | TIMESTAMP 
user_id | INTEGER 
level | VARCHAR 
song_id | VARCHAR 
artist_id | VARCHAR 
session_id | INTEGER 
location | VARCHAR 
user_agent | VARCHAR


### Dimension Tables

#### songs - songs in music database

*sorted by song_id* 

column name | type
------------- | -------------
song_id | VARCHAR
title | VARCHAR
artist_id | VARCHAR
year | SMALLINT
duration | FLOAT


#### artists - artists in music database

*sorted by artist_id* 

column name | type
------------- | -------------
artist_id | VARCHAR
artist_name | VARCHAR
artist_location | VARCHAR
artist_latitude | FLOAT
artist_longitude | FLOAT


#### time - records from songplays with specific time units

*sorted by start_time* \
*distributed by start_time*

column name | type
------------- | -------------
start_time | TIMESTAMP
hour | SMALLINT
day | SMALLINT
week | SMALLINT
month | SMALLINT
year | SMALLINT
weekday | SMALLINT

#### users - users in the app

*sorted by user_id*

column name | type
------------- | -------------
user_id | INTEGER
first_name | VARCHAR
last_name | VARCHAR
gender | CHAR(1)
level | VARCHAR
