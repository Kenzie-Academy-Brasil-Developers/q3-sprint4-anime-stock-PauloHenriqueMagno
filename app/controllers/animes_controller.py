from flask import jsonify, request
from app.models.animes_model import Anime
from psycopg2.errors import UniqueViolation, NotNullViolation, InvalidParameterValue, NoDataFound

anime_keys = ["anime", "released_date", "seasons"]

def get_animes():
    anime = Anime()
    return jsonify({"data": anime.get_animes()}), 200

def create_anime():
    data = request.json

    try:

        anime = Anime(**data)

        check_anime = anime.check_anime_data()

        if not check_anime["is_ok"]:
            raise NotNullViolation(check_anime["response"])

        check_anime = anime.check_anime_data(True)

        if not check_anime["is_ok"]:
            raise TypeError(check_anime["response"], check_anime["correct_values"])

        check_anime = anime.check_anime_keys(data)

        if not check_anime["is_ok"]:
            raise InvalidParameterValue(check_anime["response"])

        response = anime.save_anime()
        
        return jsonify(response), 201

    except UniqueViolation:
        return jsonify({"error": "anime is already exists"}), 409

    except NotNullViolation as err:
        error_message = err.args[0]

        return jsonify({"error": f"{error_message} are empty"}), 400

    except TypeError as err:
        error_message = err.args[0]
        correct_value = err.args[1]

        return jsonify({"wrong_values": error_message, "correct_values": correct_value}), 400

    except InvalidParameterValue as err:
        wrong_keys = err.args[0]

        return jsonify({
            "avaliable_keys": anime_keys,
            "worng_keys_sended": wrong_keys
        })

def delete_anime(id: int):
    id = int(id)

    try:

        anime = Anime()

        sql_response: list = anime.delete_anime_by_id(id)

        if len(sql_response) == 0:
            raise NoDataFound

        return jsonify(), 204

    except NoDataFound:
        return jsonify({"error": "Not Found"}), 404

def modify_anime(id: int):
    data = dict(request.json)
    id = int(id)

    try:
        anime = Anime(**data)

        check_anime = anime.check_anime_keys(data)

        if not check_anime["is_ok"]:
            raise InvalidParameterValue(check_anime["response"])

        sql_response = anime.modify_anime_data(data, id)
        
        if not sql_response["changed"]:
            raise NoDataFound

        return jsonify(sql_response["response"]), 200

    except NoDataFound:
        return jsonify({"error": "Not Found"}), 404

    except InvalidParameterValue as err:
        wrong_keys = err.args[0]

        return jsonify({
            "avaliable_keys": anime_keys,
            "worng_keys_sended": wrong_keys
        }), 422
        
    except UniqueViolation:
        return jsonify({"error": "anime is already exists"}), 409

def get_anime_by_id(id: int):
    id = int(id)

    try:
        anime = Anime()

        sql_response: list = anime.get_anime_by_id(id)

        if not sql_response["found"]:
            raise NoDataFound

        return jsonify(sql_response["response"]), 200

    except NoDataFound:
        return jsonify({"error": "Not Found"}), 404