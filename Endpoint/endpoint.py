from flask import Flask
from flask_restful import Api, Resource, reqparse


app = Flask(__name__)
api = Api(app)


class Quote(Resource):
    def get(self, id):
        print(id)
