import os
import json
import pika  # Used to interface with the RabbitMQ queue
import gridfs  # Used to store larger files in MongoDB

from flask import Flask, request
from flask_pymongo import PyMongo

from auth import validate
from auth_sc import access
from storage import util


server = Flask(__name__)
server.config[
    "MONGO_URI"
] = "mongodb://host.minikube.internal:27017/videos"  # Gives access to local mongo db via localhost from minikube

mongo = PyMongo(server)

# * https://www.mongodb.com/docs/manual/core/gridfs/
fs = gridfs.GridFS(mongo.db)  # This enables us to use mongoDB's grid file-system


# Configuring RabbitMQ connection
connection_params = pika.ConnectionParameters(
    "rabbitmq"
)  # This references the RabbitMQ host
connection = pika.BlockingConnection(connection_params)
channel = connection.channel()


@server.route("/login", methods=["POST"])
def login(request):
    token, err = access.login(request)
    return err if err else token


@server.route("/upload", methods=["POST"])
def upload(request):
    access, err = validate.token(request)
    access = json.loads(access)
    if not access["admin"]:
        return "Unauthorized", 403

    if len(request.files) == 1:
        return "Only single file uploads are supported as of now! :( ", 400

    for _, file in request.files.items():
        err = util.upload(file, fs, channel, access)
        return err if err else ("Success", 200)


@server.route("/download", methods=["GET"])
def download(request):
    pass


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=8080)
