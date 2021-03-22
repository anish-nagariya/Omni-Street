import json
import pprint
from flask import Response, request, jsonify
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from mongoengine.errors import FieldDoesNotExist, DoesNotExist, ValidationError
from celery.result import AsyncResult
from database.models.account import Account
from resources.errors import InvalidApiKeyError, SchemaValidationError, InternalServerError, TickerNotFoundError, UnauthorizedError, UserNotExistsError
from tasks import start_ticker_ai
from .util import *

ApiKey = os.environ['API_KEY']


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
        except Exception as e:
            pprint.pprint(e)
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
            pprint.pprint(e)
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
        except Exception as e:
            pprint.pprint(e)
            raise InternalServerError


class TickerAiApi(Resource):
    def get(self, ticker, multiplier, horizon):
        try:
            body = request.get_json()
            if ApiKey != body['key']:
                raise InvalidApiKeyError

            result = get_result(ticker, multiplier, horizon)

            pprint.pprint(result)
            return jsonify(result)
        except (IndexError, ValueError) as e:
            pprint.pprint(e)
            raise TickerNotFoundError
        except InvalidApiKeyError as e:
            pprint.pprint(e)
            raise InvalidApiKeyError
        except Exception as e:
            pprint.pprint(e)
            raise InternalServerError


class StartTickerAiAsyncApi(Resource):
    @jwt_required()
    def post(self):
        try:
            body = request.get_json()
            task = start_ticker_ai.delay(
                body['ticker'], body['multiplier'], body['horizon'])
            return jsonify({'ticker': body['ticker'], 'taskId': task.id})
        except DoesNotExist:
            raise UserNotExistsError
        except Exception as e:
            pprint.pprint(e)
            raise InternalServerError


class TickerAiAsyncResultApi(Resource):
    @jwt_required()
    def get(self, taskId):
        try:
            task_result = AsyncResult(taskId)
            if task_result.status == 'SUCCESS':
                return jsonify(task_result.result)
            elif task_result.status == 'FAILURE':
                pprint.pprint(task_result.args)
                return jsonify(task_result.args[0])
            else:
                return jsonify(task_result.status)
        except DoesNotExist:
            raise UserNotExistsError
        except Exception as e:
            pprint.pprint(e)
            raise InternalServerError
