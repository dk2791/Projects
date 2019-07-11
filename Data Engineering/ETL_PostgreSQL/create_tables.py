import psycopg2
from sql_queries import create_table_queries, drop_table_queries


def create_database():
    """
    connect to default database, create project specific database called sparkify,
    close connection to default database, connect to the project specific database
    """
    conn = psycopg2.connect("host=127.0.0.1 dbname=studentdb user=student password=student")
    conn.set_session(autocommit=True)
    cur = conn.cursor()
    
    # Following line should be adjusted if we make use of an old database
    cur.execute("DROP DATABASE IF EXISTS sparkifydb")
    cur.execute("CREATE DATABASE sparkifydb WITH ENCODING 'utf8' TEMPLATE template0")

    conn.close()    
    
    conn = psycopg2.connect("host=127.0.0.1 dbname=sparkifydb user=student password=student")
    cur = conn.cursor()
    
    return cur, conn


def drop_tables(cur, conn):
    """
    drop following set of tables.
    [songplay_table_drop, user_table_drop, song_table_drop, artist_table_drop, time_table_drop]
    """
    for query in drop_table_queries:
        cur.execute(query)
        conn.commit()


def create_tables(cur, conn):
    """
    create following set of tables.
    [songplay_table_create, user_table_create, song_table_create, artist_table_create, time_table_create]
    """
    for query in create_table_queries:
        cur.execute(query)
        conn.commit()


def main():
    cur, conn = create_database()
    
    drop_tables(cur, conn)
    create_tables(cur, conn)

    conn.close()


if __name__ == "__main__":
    main()