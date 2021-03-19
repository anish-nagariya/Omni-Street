from polygon import RESTClient


API_KEY = 'vqeohd8x5k1x6PKiisJQS8RgS3A1iRQC'

def get_ticker_detail(ticker, api_key):
    information = {}
    with RESTClient(api_key) as client:
        resp = client.stocks_equities_snapshot_single_ticker(ticker)
        information['lastUpdate'] = resp.updated
        information['todaysChange'] = resp.todaysChange
        information['openPrice'] = resp.day['o']
        information['closePrice'] = resp.day['c']
        information['tradingVolume'] = resp.day['v']
        information['lastQuoteBidPrice'] = resp.lastQuote['p']
        information['lastQuoteBidSize'] = resp.lastQuote['s']
    return information

