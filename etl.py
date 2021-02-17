import psycopg2
from sql_queries import copy_table_queries, insert_table_queries
from create_db_conn_str import create_db_conn_str


def load_staging_tables(cur, conn):
    """
    Function copies data from song_data and log_data 
    which are located on AWS S3, to Redshift Cluster
    into staging tables running two quieries
    from copy_table_queries list
    """
    for query in copy_table_queries:
        cur.execute(query)
        conn.commit()


def insert_tables(cur, conn):
    """
    Function inserts data from staging tables into 
    Fact and Dimension tables running quieries
    from insert_table_queries list
    """
    for query in insert_table_queries:
        cur.execute(query)
        conn.commit()


def main():
    
    conn_str = create_db_conn_str()
    
    conn = psycopg2.connect(conn_str)
    cur = conn.cursor()
    
    load_staging_tables(cur, conn)
    insert_tables(cur, conn)

    conn.close()

if __name__ == "__main__":
    main()