from flask import Blueprint
from app.controllers import animes_controller

bp = Blueprint("animes", __name__, url_prefix = "/animes")

bp.get("")(animes_controller.get_animes)

bp.get("/<id>")(animes_controller.get_anime_by_id)

bp.post("")(animes_controller.create_anime)

bp.delete("/<id>")(animes_controller.delete_anime)

bp.patch("/<id>")(animes_controller.modify_anime)