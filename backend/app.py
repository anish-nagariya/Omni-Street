import os
import datetime
from flask import Flask, Response
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from database.db import initialize_db
from database.models.token import TokenBlockList
from resources.routes import initialize_routes
from resources.errors import errors

app = Flask(__name__)
app.config["MONGODB_SETTINGS"] = {
    'host': os.environ['MONGODB_HOSTNAME'],
    'username': os.environ['MONGODB_USERNAME'],
    'password': os.environ['MONGODB_PASSWORD'],
    'db': os.environ['MONGODB_DATABASE'],
}
app.config['model_folder_path'] = os.environ['MODEL_PATH']
app.config["ENV"] = os.environ['FLASK_ENV']
app.config['DEBUG'] = os.environ.get('ENV') == 'development'
app.config["JWT_SECRET_KEY"] = os.environ['JWT_SECRET_KEY']
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = datetime.timedelta(hours=1)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = datetime.timedelta(hours=8)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['PROPAGATE_EXCEPTIONS'] = True
api = Api(app, prefix="/api/v1", errors=errors)
jwt = JWTManager(app)
cors = CORS(app, supports_credentials=True)

initialize_db(app)
initialize_routes(api)


@app.route("/api")
def hello():
    return Response("Hello World!", status=200)


@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    tokenCount = TokenBlockList.objects(jti=jti).count()
    return tokenCount > 0


@app.after_request
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = 'http://localhost:3000'
    header['Access-Control-Allow-Credentials'] = 'true'
    header['Access-Control-Allow-Methods'] = 'DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT'
    header['Access-Control-Allow-Headers'] = 'Access-Control-Allow-Headers, Origin,Accept, X-Requested-With, Content-Type, Access-Control-Request-Method, Access-Control-Request-Headers,Authorization'
    return response


if __name__ == "__main__":
    app.run(port=5000, threaded=True)
