import psycopg2
from sql_queries import create_table_queries, drop_table_queries
from create_db_conn_str import create_db_conn_str


def drop_tables(cur, conn):
    """
    Function deletes tables if they exist
    by running queries from drop_table_queries list
    """
    for query in drop_table_queries:
        cur.execute(query)
        conn.commit()


def create_tables(cur, conn):
    """
    Function creates all needed tables
    by running queries from create_table_queries list
    """
    for query in create_table_queries:
        cur.execute(query)
        conn.commit()


def main():
    
    conn_str = create_db_conn_str()
   
    conn = psycopg2.connect(conn_str)
    cur = conn.cursor()

    drop_tables(cur, conn)
    create_tables(cur, conn)

    conn.close()


if __name__ == "__main__":
    main()