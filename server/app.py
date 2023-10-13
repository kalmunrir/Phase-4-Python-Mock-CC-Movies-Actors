#!/usr/bin/env python3

from models import db, Movie, Actor, Credit
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)
api = Api(app)

class Actor_Route(Resource):
    def get(self):
        actors = [actor.to_dict(only=('id', 'name', 'age')) for actor in Actor.query.all()]
        return make_response(actors, 200)
    def post(self):
        try:
            new_actor = Actor(
                name=request.get_json()['name'],
                age=request.get_json()['age']
            )
        except ValueError as e:
            return make_response({"errors": str(e)}, 400)
            

        db.session.add(new_actor)
        db.session.commit()

        return make_response(new_actor.to_dict(only=('id', 'name', 'age')), 200)
api.add_resource(Actor_Route, '/actors')

class ActorById_Route(Resource):
    def get(self, id):
        actor = Actor.query.filter_by(id=id).first()
        if actor:
            return make_response(actor.to_dict(), 200)
        return make_response({"error": "Name not found"}, 404)
    def patch(self, id):
        actor = Actor.query.filter_by(id=id).first()

        if actor:
            dtp = request.get_json()
            try:
                for attr in dtp:
                    setattr(actor, attr, dtp[attr])
            except ValueError as e:
                return make_response({"errors": str(e)}, 400)
            errors = []
            for attr in dtp:
                try:
                    setattr(actor, attr, dtp[attr])
                except ValueError as e:
                    errors.append(e.__repr__())
            if len(errors) != 0:
                return make_response({"errors": errors}, 400)
            else:
                db.session.add(actor)
                db.session.commit()
                return make_response(actor.to_dict(), 202)
        
        return make_response({"error": "Actor not found"}, 404)
    
    def delete(self, id):
        actor = Actor.query.filter_by(id=id).first()
        if actor:
            try:
                db.session.delete(actor)
                db.session.commit()
                return make_response('', 204)
            except Exception:
                return make_response('', 400)
        else:
            return make_response({"error": "Actor not found"}, 404)
api.add_resource(ActorById_Route, '/actors/<int:id>')

class Movie_Route(Resource):
    def get(self):
        movies = [movie.to_dict() for movie in Movie.query.all()]
        return make_response(movies, 200)
    def post(self):
        try:
            new_movie = Movie(
                image=request.get_json()['image'],
                title=request.get_json()['title'],
                genre=request.get_json()['genre'],
                rating=request.get_json()['rating'],
                description=request.get_json()['description']
            )
        except ValueError as e:
            return make_response({"errors": str(e)}, 400)
            

        db.session.add(new_movie)
        db.session.commit()

        return make_response(new_movie.to_dict(), 200)
api.add_resource(Movie_Route, '/movies')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
