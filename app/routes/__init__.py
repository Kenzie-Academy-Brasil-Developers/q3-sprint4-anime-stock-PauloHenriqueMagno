from flask import Flask
from app.routes.anime_route import bp as bp_animes

def init_app(app: Flask):
  
    app.register_blueprint(bp_animes)