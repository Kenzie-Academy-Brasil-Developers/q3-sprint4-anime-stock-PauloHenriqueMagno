from os import getenv
import psycopg2

config = {
    "host": getenv("DB_HOST"),
    "database": getenv("DB_NAME"),
    "user": getenv("DB_USER"),
    "password": getenv("DB_PASSWORD")
}

class DatabaseConnector:
    @classmethod
    def get_conn_cur(cls):
        cls.conn = psycopg2.connect(**config)
        cls.cur = cls.conn.cursor()

    @classmethod
    def commit_and_close(cls):
        cls.conn.commit()
        cls.cur.close()
        cls.conn.close()

    @classmethod
    def create_table(cls):
        cls.get_conn_cur()
    
        query = """
            CREATE TABLE IF NOT EXISTS animes (
                id            BIGSERIAL     PRIMARY KEY,
                anime         VARCHAR(100)  NOT NULL UNIQUE,
                released_date DATE          NOT NULL,
                seasons       INTEGER       NOT NULL
            );
        """

        cls.cur.execute(query)

        cls.commit_and_close()