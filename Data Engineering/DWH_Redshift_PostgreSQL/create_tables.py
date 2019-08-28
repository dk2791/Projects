import configparser
import psycopg2
from sql_queries import create_table_queries, drop_table_queries


def drop_tables(cur, conn):
    """
        This query will be responsible for deleting pre-existing tables to ensure that our database 
        does not throw any error if we try creating a table that already exists.
    """
    for query in drop_table_queries:
        cur.execute(query)
        conn.commit()


def create_tables(cur, conn):
    """
        This query creates tables with pre-specified data types and schema
    """
    for query in create_table_queries:
        cur.execute(query)
        conn.commit()


def main():
    """
        It connects to AWS Redshift Cluster created for this project and utilizes drop_table and create_table functions
    """
    config = configparser.ConfigParser()
    config.read('dwh.cfg')

    conn = psycopg2.connect("postgresql://{}:{}@{}:{}/{}".format(*config['CLUSTER'].values()))
    cur = conn.cursor()
    

    drop_tables(cur, conn)
    create_tables(cur, conn)

    conn.close()


if __name__ == "__main__":
    main()