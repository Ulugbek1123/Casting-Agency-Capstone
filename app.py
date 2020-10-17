import os
import json
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate

from models import setup_db, Movies, Actors, db
#from auth import AuthError, requires_auth

DEFAULT_OFFSET = 1
DEFAULT_LIMIT = 30

def paginate_response(request, selection):
  offset = request.args.get('offset', DEFAULT_OFFSET, type=int)
  limit = request.args.get('limit', DEFAULT_LIMIT, type=int)
  start =  (offset - 1) * limit
  end = start + limit

  formatted_selection = [item.format() for item in selection]
  paginated_selection = formatted_selection[start:end]

  return paginated_selection

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  #migrate = Migrate(app, db)
  db.init_app(app)
  setup_db(app)
  CORS(app)

  class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code
  #___________________________________________________
  # GET reuqests
  #___________________________________________________
  '''get movies'''

  @app.route('/movies', method=['GET'])
  @requires_auth('get:movies')
  def get_movies(jwt):
      try:
          return jsonify({
          'success': True,
          'movies': paginate_response(request, Movies.query.order_by(Movies.id).all())
          })
      except:
          abort(422)


  '''get Actors'''
  @app.route('/actors', method=['GET'])
  @requires_auth('get:actors')
  def get_actors(jwt):
      try:
          return jsonify({
          'success': True,
          'actors': paginated_response(request, Actors.query.order_by(Actors.id).all())
          })
      except:
          abort(422)

  #___________________________________________________
  # POST requests
  #___________________________________________________


  '''post movies'''

  @app.route('/movies', method=['POST'])
  @requires_auth('post:movies')
  def add_movie(jwt):
      body = request.json
      title = body.get('title', None)
      release_date = body.get('release_date', None)

      #IF FIELDS ARE EMPTY ABORT(400)
      if any(arg is None for arg in[title, release_date]) or '' in[title, release_date]:
          abort(400, 'All fields are required. Please check again!!!')

      #IF THE MOVIE ALREADY ADDED ABORT(400)
      if title in list(map(Movies.get_title, Movies.query.all())):
          abort(400, 'That title is already added. Please, add a new ones')

      #INSERT Movie
      added_movie = Movies(title=title, release_date=release_date)
      added_movie.insert()

      return jsonify({
      'success': True,
      'movies': [Movies.query.get(added_movie.id).format()]
      })




  '''post actors'''

  @app.route('/actors', method=['POST'])
  @reuires_auth('post:actors')
  def add_actor(jwt):
      body = reuqest.json
      name = body.get('name', None)
      age = body.get('age', None)
      gender = body.get('gender', None)

      #IF FIELDS ARE EMPTY ABORT(400)
      if any(arg is None for arg in[name, age, gender]) or '' in[name, age, gender]:
          abort(400, 'All fields are required. Please check again!!!')

      #IF THE MOVIE ALREADY ADDED ABORT(400)
      if title in list(map(Actors.get_title, Actors.query.all())):
          abort(400, 'That title is already added. Please, add a new ones')

      #INSERT Movie
      added_actor = Actors(title=title, release_date=release_date)
      added_actor.insert()

      return jsonify({
      'success': True,
      'actors': [Actors.query.get(added_actor.id).format()]
      })


  #___________________________________________________
  # PATCH requests
  #___________________________________________________


  '''patch movies'''

  @app.route('/movies/<movies_id>', methods=['PATCH'])
  @requires_auth('patch:movies')
  def patch_movies(jwt, movies_id):
      movies = Movies.query.get(movies_id)

      if movies is None:
          abort(404)

      body = request.json
      title = body.get('title', None)
      release_date = body.get('release_date', None)

      #IF ANY FLIED EMPTY ABORT(400)
      if any(arg is None for arg in[title, release_date]) or '' in[title, release_date]:
          abort(400, 'All fields are required. Please check again!!!')

      #UPDATE
      movies.title = title
      movies.release_date = release_date
      movies.update()

      return jsonify({
      'success': True,
      'movies': [Movies.query.get(movies_id).format()]
      })



  '''patch actors'''
  @app.route('/actors/<actors_id>', method=['PATCH'])
  @requires_auth('patch:actors')
  def patch_actors(jwt, actors_id):
      actors = Actors.query.get(actors_id)

      if actors is None:
          abort(404)

      body = request.json
      name = body.get('name', None)
      age = body.get('age', None)
      gender = body.get('gender', None)

      #IF ANY FLIED EMPTY ABORT(400)
      if any(arg is None for arg in[name, age, gender]) or '' in[name, age, gender]:
          abort(400, 'All fields are required. Please check again!!!')

      #UPDATE

      actors.name = name
      actors.age = age
      actors.gender = gender
      actors.update()

      return jsonify({
      'success': True,
      'actors': [Actors.query.get(actors_id).format()]
      })


  #___________________________________________________
  #DELETE request
  #___________________________________________________

  '''delete movies'''

  @app.route('/movies/<movies_id>', method=['DELETE'])
  @requires_auth('delete:movies')
  def remove_movie(jwt, movies_id):
      movies = Movies.query.get(movies_id)

      if movies is None:
          abort(404)
      movies.delete()

      return jsonify({
      'success': True,
      'delete': movies_id
      })



  '''delete actors'''
  @app.route('/actors/<actors_id>', method=['DELETE'])
  @requires_auth('delete:actors')
  def remove_actors(jwt, actors_id):
      actors = Actors.query.get(actors_id)

      if actors is None:
          abort(404)
      actors.delete()

      return jsonify({
      'success': True,
      'delete': actors_id
      })



  @app.errorhandler(Exception)
  def handle_auth_error(ex):
      response = jsonify(message=str(ex))
      response.status_code = (ex.code if isinstance(ex, HTTPException) else 500)
      return response


  return app

APP = create_app()

if __name__ == '__main__':
    APP.run(host='0.0.0.0', port=8080, debug=True)
