import configparser


def create_db_conn_str():
    config = configparser.ConfigParser()
    config.read('dwh.cfg')

    host = config["CLUSTER"]["HOST"]
    dbname = config["CLUSTER"]["DB_NAME"]
    user = config["CLUSTER"]["DB_USER"]
    password = config["CLUSTER"]["DB_PASSWORD"]
    port = config["CLUSTER"]["DB_PORT"]

    conn_str = f"host={host} dbname={dbname} user={user} password={password} port={port}"
    
    return conn_str