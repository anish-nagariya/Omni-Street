import json
import pprint
import os
from flask import Response, request, jsonify
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from mongoengine.errors import FieldDoesNotExist, DoesNotExist, ValidationError
from database.models.account import Account
from resources.errors import SchemaValidationError, InternalServerError, TickerNotFoundError, UnauthorizedError, UserNotExistsError
from .util import *


class TickersApi(Resource):
    @jwt_required()
    def get(self):
        try:
            username = get_jwt_identity()
            tickers = json.dumps(
                Account.objects.get(username=username).symbols)
            return Response(tickers, mimetype="application/json", status=200)
        except DoesNotExist:
            raise UserNotExistsError
        except Exception:
            raise InternalServerError

    @jwt_required()
    def put(self):
        try:
            username = get_jwt_identity()
            body = request.get_json()

            result = get_result(body['symbol'], 5, 'minute')
            result['username'] = username

            Account.objects(username=username).update(
                upsert=True, add_to_set__symbols=body['symbol'])
            pprint.pprint(result)
            return jsonify(result)
        except (IndexError, ValueError):
            raise TickerNotFoundError
        except (FieldDoesNotExist, ValidationError):
            raise SchemaValidationError
        except Exception as e:
            raise InternalServerError

    @jwt_required()
    def delete(self):
        try:
            username = get_jwt_identity()
            body = request.get_json()
            Account.objects(username=username).update(
                pull__symbols=body['symbol'])
            return 'None', 200
        except DoesNotExist:
            raise UserNotExistsError
        except Exception:
            raise InternalServerError


class TickerAiApi(Resource):
    def get(self, ticker, multiplier, horizon):
        try:
            result = get_result(ticker, multiplier, horizon)

            pprint.pprint(result)
            return jsonify(result)
        except (IndexError, ValueError):
            raise TickerNotFoundError
        except Exception as e:
            raise InternalServerError
