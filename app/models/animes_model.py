from flask import request
from app.models import DatabaseConnector
from psycopg2 import sql

ANIME_KEYS = ["anime", "released_date", "seasons"]
ANIME_VALUES = {"anime": str, "released_date": str, "seasons": int}

class Anime(DatabaseConnector):
    @classmethod
    def __init__(self, *args, **kwargs):
        anime: str = kwargs.get("anime")

        self.anime         = anime if not anime else anime.title()
        self.seasons       = kwargs.get("seasons")
        self.released_date = kwargs.get("released_date")

    @classmethod
    def get_animes(cls):
        keys = ["id", "anime", "seasons", "released_date"]

        cls.create_table()
        cls.get_conn_cur()

        query = """
            SELECT
                id, anime, seasons, to_char(released_date, 'DD/MM/YYYY') as released_date
            FROM
                animes
            ORDER BY
                id
        """

        cls.cur.execute(query)

        animes = cls.cur.fetchall()
        response = []

        for row in animes:
            response.append(dict(zip(keys, row)))

        cls.commit_and_close()

        return response
    
    @classmethod
    def save_anime(self):
        self.create_table()
        self.get_conn_cur()

        anime = dict(self.__dict__)

        keys = ANIME_KEYS.copy()

        values = [anime.get(key) for key in keys]
        
        keys.append("id")

        query = """
            INSERT INTO
                animes (anime, released_date, seasons)
            VALUES
                (%s, %s, %s)
            RETURNING
                anime, to_char(released_date, 'DD/MM/YYYY') as released_date, seasons, id
        """

        self.cur.execute(query, values)

        sql_response = self.cur.fetchone()
        formatted = dict(zip(keys, sql_response))

        self.commit_and_close()

        return formatted

    @classmethod
    def check_anime_data(self, check_values = False):
        data = self.__dict__

        if check_values:
            response = {"response": {}, "correct_values": {}, "is_ok": True}

            for key in ANIME_KEYS:
                value_type = str(type(data[key]))[8:-2]
                correct_value_type = str(ANIME_VALUES[key])[8:-2]

                if value_type != correct_value_type:
                    response["response"][key] = value_type
                    response["correct_values"][key] = correct_value_type
                    response["is_ok"] = False

        else:
            response = {"response": [], "is_ok": True}

            for key in ANIME_KEYS:
                if not data.get(key):
                    response["response"].append(key)
                    response["is_ok"] = False
     
        return response

    @staticmethod
    def check_anime_keys(data):
        invalid_keys = []

        print(data)
        for key in data.keys():
            if not ANIME_VALUES.get(key):
                invalid_keys.append(key)

        if len(invalid_keys) > 0:
            return {"response": invalid_keys, "is_ok": False}

        return {"response": invalid_keys, "is_ok": True}

    @classmethod
    def delete_anime_by_id(cls, id: int):
        cls.create_table()
        cls.get_conn_cur()

        query = """
            DELETE FROM
                animes
            WHERE
                id = %s
            RETURNING
                *
        """

        cls.cur.execute(query, [id])

        response = cls.cur.fetchall()

        cls.commit_and_close()

        return response

    @classmethod
    def modify_anime_data(self, data, id: int):
        # data = self.__dict__
        
        if data.get("anime"):
            data["anime"] = data["anime"].title()

        self.create_table()
        self.get_conn_cur()    

        anime_keys = ANIME_KEYS.copy()
        anime_keys.append("id")

        data_keys = [sql.Identifier(key) for key in data.keys()]
        data_values = [sql.Literal(value) for value in data.values()]

        query = sql.SQL("""
            UPDATE
                animes
            SET
                ({keys}) = ROW({values})
            WHERE
                id = {user_id}
            RETURNING
                anime, to_char(released_date, 'DD/MM/YYYY') as released_date, seasons, id
        """).format(
            keys = sql.SQL(", ").join(data_keys),
            values = sql.SQL(", ").join(data_values),
            user_id = sql.Literal(id)
        )   

        self.cur.execute(query)

        response = self.cur.fetchone()
        
        if not response:
            return {"changed": False}

        formatted = dict(zip(anime_keys, response))

        self.commit_and_close()

        return {"response": formatted, "changed": True}
    
    @classmethod
    def get_anime_by_id(cls, id: int):

        cls.create_table()
        cls.get_conn_cur()

        anime_keys = ANIME_KEYS.copy()
        anime_keys.append("id")

        query = """
            SELECT
                anime, to_char(released_date, 'DD/MM/YYYY') as released_date, seasons, id
            FROM 
                animes
            WHERE
                id = %s
        """

        cls.cur.execute(query, [id])

        response = cls.cur.fetchone()

        cls.commit_and_close()

        if not response:
            return {"found": False}

        formatted = dict(zip(anime_keys, response))

        return {"response": formatted, "found": True}