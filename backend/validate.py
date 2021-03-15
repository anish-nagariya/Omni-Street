from polygon import RESTClient

API_KEY = 'vqeohd8x5k1x6PKiisJQS8RgS3A1iRQC'

def validate_ticker(ticker, api_key):
    """
    :param ticker: Ticker user has requested for
    :param api_key: API_KEY to use Polygon.io API
    :return: True if ticker exists, False if ticker does not exist
    """
    with RESTClient(api_key) as client:
        resp = client.stocks_equities_aggregates(ticker=ticker, multiplier=1, timespan='day',
                                                 from_='1999-07-12', to='2021-01-12', sort='asc',
                                                 limit=50000)
        if resp.queryCount == 0:
            return False
        return True

