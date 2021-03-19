import keras
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import finnhub
import nltk
import os
import math
import time as t
from os import path
from datetime import datetime, timezone
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Dense, LSTM, Dropout, Activation
from keras.callbacks import EarlyStopping


API_KEY = os.environ['API_KEY']
models = {}

def get_result(ticker, multiplier, horizon):
    multiplier = 5
    horizon = 'minute'

    if not path.exists('Models/' + ticker):
        start = int(datetime(2021, 1, 19).replace(tzinfo=timezone.utc).timestamp())
        date = int(datetime(2021, 2, 26).replace(tzinfo=timezone.utc).timestamp())

        data = get_historic_data(ticker, multiplier, start, date)
        data['timestamp'] = data['timestamp'].apply(lambda x: datetime.fromtimestamp(x))
        x_train, y_train, xv, yv, x_test, y_test, scaler = preprocess_training_data(data)  # splits data for training
        # save_scaler(ticker, horizon, scaler)

        model = keras.models.load_model('Models/AlphaModel')
        compile_model(model, x_train, y_train, xv, yv)
        model.save('Models/' + ticker)
    try:
        model = models[ticker]
    except Exception:
        model = keras.models.load_model('Models/' + ticker)
        models[ticker] = model
        print("LOADING MODEL...")

    recent_df = call_recent_data(ticker, multiplier)
    x_train, y_train, xv, yv, x_test, y_test, scaler = preprocess_training_data(recent_df)

    predictions = model.predict(x_test) * 1 / scaler[0]
    answers = y_test * 1 / scaler[0]
    average = get_average(predictions[-10:], answers[-10:])

    recent_df = call_recent_data(ticker, multiplier)

    time = recent_df['timestamp'].iloc[-1]
    entry_price = recent_df['open'].iloc[-1]

    training_df = normalize_recent_data(recent_df, scaler)
    result = round(model.predict(training_df)[0][0] * 1 / scaler[0], 5) + average
    prob = probablity(predictions, y_test, -1)
    result = get_prediction_details(ticker, multiplier, horizon, result, entry_price, prob, time)
    print(len(models))
    return result


def get_historic_data(ticker, time_horizon, start, end):
    client = finnhub.Client(API_KEY)
    resp = client.stock_candles(ticker, time_horizon, start, end)
    df0 = pd.DataFrame(resp)
    resp = client.stock_candles(ticker, time_horizon, 1609000000, 1612184400)
    df1 = pd.DataFrame(resp)
    df = pd.concat([df1, df0])
    df = df.drop(['s'], axis=1)
    df = df.rename(columns={'c': 'close', 'h': 'high', 'l': 'low',
                            'o': 'open', 't': 'timestamp', 'v': 'volume'})
    df = df[['timestamp', 'open', 'low', 'high', 'volume', 'close']]
    df = df.reset_index()
    df = df.drop(['index'], axis=1)
    return df


def get_recent_data(ticker, time_horizon, start, end):  # gets recent data for predictions
    if time_horizon == 'hour' or time_horizon == 1:
        time_horizon = 60
    client = finnhub.Client(API_KEY)
    resp = client.stock_candles(ticker, time_horizon, start, end)
    df = pd.DataFrame(resp)
    df = df.drop(['s'], axis=1)
    df = df.rename(columns={'c': 'close', 'h': 'high', 'l': 'low',
                            'o': 'open', 't': 'timestamp', 'v': 'volume'})
    df = df[['timestamp', 'open', 'low', 'high', 'volume', 'close']]
    return df


def preprocess_training_data(training_df):
    training_df = training_df.drop(['timestamp'], axis=1)
    scaler = MinMaxScaler()
    scaler_df = training_df.copy()
    scaler.fit_transform(scaler_df)
    scaler = scaler.scale_
    training_df['open'] *= scaler[0]
    training_df['low'] *= scaler[1]
    training_df['high'] *= scaler[2]
    training_df['volume'] *= scaler[3]
    training_df['close'] *= scaler[4]

    x_train, y_train = [], []
    training_df = np.asarray(training_df)
    for i in range(12, training_df.shape[0]):
        x_train.append(training_df[i - 12: i])
        y_train.append(training_df[i, 0])
    x_train, y_train, xv, yv, x_test, y_test = np.asarray(x_train[:-200]), np.asarray(y_train[:-200]), np.array(
        x_train[-200:-100]), np.array(y_train[-200:-100]), np.asarray(x_train[-100:]), np.asarray(y_train[-100:])
    return x_train, y_train, xv, yv, x_test, y_test, scaler


def normalize_recent_data(recent_df, scaler):
    training_df = recent_df[-12:]
    training_df = training_df.drop(['timestamp'], axis=1)
    training_df['open'] *= scaler[0]
    training_df['low'] *= scaler[1]
    training_df['high'] *= scaler[2]
    training_df['volume'] *= scaler[3]
    training_df['close'] *= scaler[4]
    training_df = [training_df]
    training_df = np.asarray(training_df)
    return training_df


# adds label and features to words from corpus
def generate_features(documents, words, label):
    features = []
    for document in documents:
        features.append(({
            word: (word in document)
            for word in words
        }, label))
    return features


def extract_words(document):  # tokenizes words using nltk
    return set(
        word.lower() for word in nltk.word_tokenize(document)
        if any(c.isalpha() for c in word)
    )


def classify(classifier, document, words):  # returns polarity of news text
    document_words = extract_words(document)
    features = {
        word: (word in document_words)
        for word in words
    }
    return classifier.prob_classify(features)


def get_polarity(headline):
    result = []
    for file in ["corpus/positives.txt", "corpus/negatives.txt"]:  # loads files from corpus
        with open(file, 'r') as f:
            result.append([extract_words(line)
                           for line in f.read().splitlines()])
    positives, negatives = result  # splits into positive and negative groups

    words = set()
    for document in positives:
        words.update(document)
    for document in negatives:
        words.update(document)

    training = []
    # trains model on words from corpus
    training.extend(generate_features(positives, words, "Positive"))
    training.extend(generate_features(negatives, words, "Negative"))

    classifier = nltk.NaiveBayesClassifier.train(
        training)  # gets NaiveBayesClassifier
    result = (classify(classifier, headline, words))  # gets polarity
    return result.prob("Positive")


def call_news_api(client, ticker, start, end):
    resp = client.company_news(ticker, start, end)
    df = pd.DataFrame(resp)
    return df


def process_news(df):
    df['datetime'] = df['datetime'].apply(
        lambda x: datetime.fromtimestamp(x))  # converts unix msec to datetime
    df = df.drop(['url'], axis=1)
    df = df.drop(['id'], axis=1)
    df = df.drop(['image'], axis=1)
    df = df.drop(['source'], axis=1)
    df = df.drop(['related'], axis=1)
    df = df.drop(['category'], axis=1)
    df = df.reset_index()
    df = df.drop(['index'], axis=1)
    df = df.iloc[::-1]
    df = df.reset_index()
    # only stores news date, headline and summary
    df = df.drop(['index'], axis=1)
    return df


def get_news(ticker):
    # gets historical news data from 2020-09-27 to 2021-02-19
    client = finnhub.Client(API_KEY)
    resp = client.company_news(ticker, '2021-01-04', '2021-02-19')
    df = pd.DataFrame(resp)
    df = process_news(df)
    return df


def get_recent_news(ticker, date):
    client = finnhub.Client(API_KEY)
    # gets recent news for predictions
    resp = client.company_news(ticker, '2021-02-18', date)
    df = pd.DataFrame(resp)
    df['datetime'] = df['datetime'].apply(lambda x: datetime.fromtimestamp(x))
    df = df.drop(['url'], axis=1)
    df = df.drop(['id'], axis=1)
    df = df.drop(['image'], axis=1)
    df = df.drop(['source'], axis=1)
    df = df.drop(['related'], axis=1)
    df = df.drop(['category'], axis=1)
    df = df.reset_index()
    df = df.drop(['index'], axis=1)
    df = df.iloc[::-1]
    df = df.reset_index()
    df = df.drop(['index'], axis=1)
    return df


def combine_news_data(news_df, df):
    # combines news and stock data if news is not available for timeframe takes previous news into account
    x = []
    j = 0
    n = len(df)
    f = 0
    p = 0
    for i in range(len(news_df)):
        while news_df['datetime'].iloc[i] >= df['timestamp'].iloc[j]:
            x.append(p)
            j = j + 1
            if j == n:
                f = 1
                break
        if f == n:
            break
        p = news_df['polarity'].iloc[i]
        while i == len(news_df) - 1 and j < n:
            x.append(p)
            j = j + 1
    df = pd.DataFrame(np.array(x), columns=['polarity'])
    return df


def save_scaler(ticker, time_horizon, scaler):  # saves scaler values for future usage
    f = open('Data/Scale/' + ticker + time_horizon + '.csv', 'w')
    f.write(str(scaler[0]) + '\n')  # scaler value for open
    f.write(str(scaler[1]) + '\n')
    f.write(str(scaler[2]) + '\n')
    f.write(str(scaler[3]) + '\n')
    f.write(str(scaler[4]) + '\n')


def create_rnn():  # creates neural network
    model = Sequential()

    model.add(LSTM(units=50,  # 4 LSTM layers using SeLU activation function
                   activation='selu',
                   input_shape=(12, 5),
                   return_sequences=True))
    model.add(Dropout(0.2))  # dropout to prevent overfitting

    model.add(LSTM(units=60,
                   activation='selu',
                   return_sequences=True))

    model.add(Dropout(0.2))
    model.add(LSTM(units=80,
                   activation='selu',
                   return_sequences=True))
    model.add(Dropout(0.2))

    model.add(LSTM(units=100,
                   activation='selu',
                   return_sequences=False
                   ))
    model.add(Dropout(0.2))

    model.add(Dense(25))
    model.add(Dense(1))  # dense layer for output
    model.add(Activation('linear'))

    return model


def call_recent_data(ticker,  multiplier):
    recent_df = get_recent_data(ticker, multiplier, math.floor(t.time()) - 864000, math.floor(t.time()))
    recent_df['timestamp'] = recent_df['timestamp'].apply(lambda x: datetime.fromtimestamp(x))
    return recent_df


def compile_model(model, training_input, training_output, xv, yv):
    # compiles model on adam optimizer and mse loss function
    model.compile(optimizer='adam', loss='mean_squared_error')
    es = EarlyStopping(monitor='val_loss', mode='min', patience=5,
                       verbose=1)  # early stopping to stop training model if results are not improving

    model.fit(  # trains model for a maximum of 100 epochs
        training_input, training_output, validation_data=(xv, yv),
        epochs=20, batch_size=24, verbose=1, callbacks=[es]
    )


def visualize_model(predictions, answers, ticker):
    plt.figure(figsize=(15, 5))
    plt.plot(answers, c='r', label='Real' + ' ' + ticker + ' ' + 'Stock Price')
    plt.plot(predictions, c='c', label='Prediction' +
             ' ' + ticker + ' ' + 'Stock Price')
    plt.xlabel('time')
    plt.ylabel(ticker + ' ' + 'Stock Price')
    plt.legend()
    plt.show()


def get_prediction(model, scaler, last_data):
    # gets future prediction of model from recent data
    prediction = model.predict(last_data)
    # converts back to actual number from 0 - 1 value by multiplication of inverse scaler
    prediction *= 1 / scaler[0]
    return prediction


def get_prediction_details(ticker, time_horizon, time_span, prediction, entry_price, prob, time):
    result = {
        'ticker': ticker,
        'enterPrice': str(entry_price),
        'targetPrice': str(prediction[0]),
        'profitTarget': str((prediction / entry_price * 100 - 100)[0]),
        'multiplier': str(time_horizon),
        'profitProbability': str(prob),
        'timeHorizon': str(time_horizon) + ' ' + time_span + 's',
        'dayVolume': 100000000,
        'bid': 10,
        'ask': 11,
        'float': 10,
        'Time': time
    }
    return result  # returns all prediction details


def r(x, y):
    if y / x > 1.5:
        return 1.5
    elif y / x < -1.4:
        return -1.4
    else:
        return y / x


# function to get probability of target price through last news
def probablity(pred, y_test, recent_news_polarity):
    # headline and previous predictions
    n = len(pred)
    prob = []
    i = 0
    for j in range(5, n):
        p = 50
        for i in range(j - 5, j):
            pp = (pred[i] - pred[i - 1]) / pred[i - 1]
            tp = (y_test[i] - y_test[i - 1]) / y_test[i - 1]
            if r(pp, tp) < 0:
                p = p + p * (r(pp, tp) / 10)
            else:
                p = p + (100 - p) * (r(pp, tp) / 10)
            prob.append(p)

    if pred[i] > pred[i - 1] and recent_news_polarity > 0:
        news_p = 15 * recent_news_polarity
    elif pred[i] < pred[i - 1] and recent_news_polarity < 0:
        news_p = -1 * 10 * recent_news_polarity
    else:
        news_p = -1 * 10 * recent_news_polarity
    try:
        return (prob[-1] + news_p)[0]
    except TypeError:
        return prob[-1] + news_p


# gets average difference between predictions and actual answers
def get_average(predictions, answers):
    difference = 0
    tests = 0
    for i in range(1, len(answers)):
        tests += 1
        difference += answers[i] - predictions[i]
    average = difference / tests
    return average


def call_td_api(**kwargs):
    key = 'GWNM8JLTS4S13H3TFPDVINLSKBMLKQJE'
    symbol = kwargs.get('symbol')
    url = 'https://api.tdameritrade.com/v1/marketdata/{}/pricehistory'.format(kwargs.get('symbol'))
    params = {}
    params.update({'apikey': key})

    for arg in kwargs:
        parameter = {arg: kwargs.get(arg)}
        params.update(parameter)

    result =  requests.get(url, params=params).json()

    file = open(symbol + '.csv', 'w')
    file.write('datetime,open,high,low,volume,close\n')
    for resp in result['candles']:
        file.write(str(resp['datetime']) + ',' + str(resp['open']) + "," + str(resp['low']) + ',' + str(resp['high']) + ',' + str(resp['volume'])
        + ',' + str(resp['close']) + '\n')
    file.close()

    file = open(symbol + '.csv', 'r')
    df = pd.read_csv(file)
    df['datetime'] = df['datetime'].apply(lambda x: datetime.fromtimestamp(x/1000))
    return df
    