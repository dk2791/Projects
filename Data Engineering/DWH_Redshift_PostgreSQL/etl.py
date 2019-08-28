import configparser
import psycopg2
from sql_queries import copy_table_queries, insert_table_queries


def load_staging_tables(cur, conn):
    """
        It loads raw data from S3
    """
    for query in copy_table_queries:
        cur.execute(query)
        conn.commit()


def insert_tables(cur, conn):
    """
        It inserts values to tables created.
    """
    for query in insert_table_queries:
        cur.execute(query)
        conn.commit()


def main():
    """
        It utilizes AWS credentials stored in dwh.cfg, loads raw data and feeds relevant data
        to tables.
    """
    config = configparser.ConfigParser()
    config.read('dwh.cfg')
    
    conn = psycopg2.connect("postgresql://{}:{}@{}:{}/{}".format(*config['CLUSTER'].values()))
    cur = conn.cursor()
    
    load_staging_tables(cur, conn)
    insert_tables(cur, conn)

    conn.close()


if __name__ == "__main__":
    main()