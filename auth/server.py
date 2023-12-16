import datetime, os
import jwt
from flask import Flask, request
from flask_mysqldb import MySQL


# Creating a server

server = Flask(__name__)
mysql = MySQL(server)


# Configuring the DB
server.config["MYSQL_HOST"] = os.environ.get("MYSQL_HOST", "localhost")
server.config["MYSQL_USER"] = os.environ.get("MYSQL_USER", "auth_user")
server.config["MYSQL_PASSWORD"] = os.environ.get("MYSQL_PASSWORD", "Abhishek98")
server.config["MYSQL_DB"] = os.environ.get("MYSQL_DB", "auth")
server.config["MYSQL_PORT"] = os.environ.get("MYSQL_PORT", "1337")


def create_jwt(username, jwt_secret, authz):
    return jwt.decode(
        {
            "username": username,
            "exp": datetime.datetime.now(tz=datetime.datetime.utc)
            + datetime.timedelta(days=1),
            "iat": datetime.datetime.utcnow(),
            "admin": authz,
        },
        jwt_secret,
        algorithm="HS256",
    )


@server.route("/login", methods=["POST"])
def login():
    # Works with basic Authorization header when making a POST request
    auth = request.authorization
    if not auth:
        return "Missing / Invalid credentials", 401

    # Check DB for username and password
    cur = mysql.connection.cursor()
    res = cur.execute(
        "SELECT email, password FROM user WHERE email=%s", (auth.username)
    )

    if res > 0:
        user_row = cur.fetchone()
        email = user_row[0]
        password = user_row[1]

        if auth.username != email or auth.password != password:
            # Wrong credentials
            return "Missing / Invalid credentials", 401
        # Create JWT token for successful authentication
        return create_jwt(
            auth.username, os.environ.get("JWT_SECRET", "somethingsomething"), True
        )
    else:
        # User does not exits
        return "Missing / Invalid credentials", 401


@server.route("/validate", methods=["POST", "GET"])
def validate():
    encoded_jwt = request.headers.get("Authorization")
    if not encoded_jwt:
        return "Missing / Invalid credentials", 401
    encoded_jwt = encoded_jwt.split(
        " "
    )  # Removing Bearer type from Authorization header
    decoded = None
    try:
        decoded = jwt.decode(
            encoded_jwt, os.environ.get("JWT_SECRET", "somethingsomething"), "HS256"
        )

    except Exception as e:
        print(e)
        return "Unauthorized", 403

    return decoded, 200


if __name__ == "__main__":
    # Listen to all Public IPs instead of the deafult localhost for external availability.
    server.run(host="0.0.0.0", port=5000)
