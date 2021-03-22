from flask_restful import HTTPException


class InternalServerError(HTTPException):
    pass


class SchemaValidationError(HTTPException):
    pass


class UsernameAlreadyExistsError(HTTPException):
    pass


class UnauthorizedError(HTTPException):
    pass


class UserNotExistsError(HTTPException):
    pass


class TickerNotFoundError(HTTPException):
    pass


class InvalidApiKeyError(HTTPException):
    pass


errors = {
    "InternalServerError": {
        "message": "Something went wrong",
        "status": 500
    },
    "SchemaValidationError": {
        "message": "Request is missing required fields",
        "status": 400
    },
    "UsernameAlreadyExistsError": {
        "message": "User with given username already exists",
        "status": 400
    },
    "UnauthorizedError": {
        "message": "Invalid username or password",
        "status": 401
    },
    "UserNotExistsError": {
        "message": "Username does not exist",
        "status": 401
    },
    "ExpiredSessionError": {
        "message": "Session has expired",
        "status": 401
    },
    "TickerNotFoundError": {
        "message": "Invalid ticker provided",
        "status": 404
    },
    "InvalidApiKeyError": {
        "message": "Invalid Api Key provided",
        "status": 401
    }

}
