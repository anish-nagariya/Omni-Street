import random
import os
import pprint
from flask import request
from flask_restful import Resource
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt, create_refresh_token
from mongoengine.errors import FieldDoesNotExist, NotUniqueError, DoesNotExist
from database.models.account import Account
from database.models.token import TokenBlockList
from .errors import InvalidApiKeyError, SchemaValidationError, UserNotExistsError, UsernameAlreadyExistsError, UnauthorizedError, InternalServerError

ApiKey = os.environ['API_KEY']


class RegisterApi(Resource):
    def post(self):
        try:
            body = request.get_json()
            account = Account(**body).save()
            id = account.id
            return {'id': str(id), 'username': account.username}, 200
        except FieldDoesNotExist:
            raise SchemaValidationError
        except NotUniqueError:
            raise UsernameAlreadyExistsError
        except Exception as e:
            pprint.pprint(e)
            raise InternalServerError


class LoginApi(Resource):
    def post(self):
        try:
            body = request.get_json()
            account = Account.objects.get(username=body['username'])
            if body['password'] != account.password:
                return {'message': 'Username or password is invalid'}, 401

            jwt_token = create_access_token(identity=str(account.username))
            refresh_token = create_refresh_token(
                identity=str(account.username))
            resp = account.generateDict()
            resp['jwtToken'] = jwt_token
            resp['refreshToken'] = refresh_token
            return resp, 200
        except (UnauthorizedError, DoesNotExist):
            raise UnauthorizedError
        except Exception as e:
            pprint.pprint(e)
            raise InternalServerError


class RefreshTokenApi(Resource):
    @jwt_required(refresh=True)
    def post(self):
        try:
            username = get_jwt_identity()
            account = Account.objects.get(username=username)
            jwt_token = create_access_token(identity=str(account.username))
            refresh_token = create_refresh_token(
                identity=str(account.username))
            resp = account.generateDict()
            resp['jwtToken'] = jwt_token
            resp['refreshToken'] = refresh_token
            return resp, 200
        except (UnauthorizedError, DoesNotExist):
            raise UnauthorizedError
        except Exception as e:
            pprint.pprint(e)
            raise InternalServerError


class RevokeTokenApi(Resource):
    @jwt_required()
    def post(self):
        try:
            jti = get_jwt()["jti"]
            TokenBlockList(jti=jti).save()
            return "Logout completed", 200
        except (UnauthorizedError, DoesNotExist):
            raise UnauthorizedError
        except Exception as e:
            pprint.pprint(e)
            raise InternalServerError


class ForgotApi(Resource):
    def post(self):
        try:
            body = request.get_json()
            if ApiKey != body['key']:
                raise InvalidApiKeyError
            Account.objects().get(username=body['username'])

            while True:
                resetToken = str(random.random())[2:18]
                if Account.objects(resetToken=str(resetToken)).count() == 0:
                    break

            Account.objects(username=body['username']).update(
                set__resetToken=resetToken)
            return {'resetToken': resetToken}, 200
        except InvalidApiKeyError:
            raise InvalidApiKeyError
        except DoesNotExist:
            raise UserNotExistsError
        except Exception as e:
            pprint.pprint(e)
            raise InternalServerError


class ResetPasswordApi(Resource):
    def post(self):
        try:
            body = request.get_json()
            if Account.objects(username=body['username']).count() != 1:
                raise DoesNotExist

            Account.objects(username=body['username']).update(
                password=body['password'])

            return 'Password reset', 200
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
            Account.objects(username=username).update(
                password=body['password'])
            return {'message': 'Password reset'}, 200
        except (UnauthorizedError, DoesNotExist):
            raise UnauthorizedError
        except Exception as e:
            pprint.pprint(e)
            raise InternalServerError


class ValidateResetTokenApi(Resource):
    def post(self):
        try:
            body = request.get_json()
            # if Account.objects(resetToken=str(body['resetToken'])).count() != 1:
            if body['resetToken'] != os.environ['RESET_TOKEN']:
                return {'message': 'Invalid reset token provided'}, 401

            return 'Valid reset token', 200
        except Exception as e:
            pprint.pprint(e)
            raise InternalServerError
