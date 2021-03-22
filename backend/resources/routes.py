from .account import ForgotApi, LoginApi, RefreshTokenApi, RegisterApi, ResetPasswordApi, RevokeTokenApi, ValidateResetTokenApi
from .ticker import StartTickerAiAsyncApi, TickerAiApi, TickerAiAsyncResultApi, TickersApi


def initialize_routes(api):
    api.add_resource(TickersApi, '/tickers')
    api.add_resource(RegisterApi, '/accounts/register')
    api.add_resource(LoginApi, '/accounts/authenticate')
    api.add_resource(RefreshTokenApi, '/accounts/refresh-token')
    api.add_resource(RevokeTokenApi, '/accounts/revoke-token')
    api.add_resource(ForgotApi, '/accounts/forgot')
    api.add_resource(ResetPasswordApi, '/accounts/reset-password')
    api.add_resource(ValidateResetTokenApi, '/accounts/validate-reset-token')
    api.add_resource(TickerAiApi, '/tickers/<ticker>/<multiplier>/<horizon>')
    api.add_resource(StartTickerAiAsyncApi, '/tickers/task')
    api.add_resource(TickerAiAsyncResultApi, '/tickers/task/<taskId>')
