import os
import feedparser
from textblob import TextBlob
import sys
import tweepy
import requests
import numpy as np

from keras.models import Sequential
from keras.layers import Dense

# First we login into twitter
# First we login into twitter
consumer_key = 'z0SNNqKbCMGVpuBKArQSyIA6b'
consumer_secret = '47LfjkYR73JYzpX6Qtw4i0b6zhK1V1HkJoAoRjinYYEHEbtR5N'
access_token = '231076651-BE3pwuSeBq0PNIhJuF5G3QwNMfmupojyoDZi6qSK'
access_token_secret = 'Ku5j7k6C7YBfV6Ux0Pl3coZH88LoSeM6pM1MaPMHk9DEP'
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
user = tweepy.API(auth)

# Where the csv file will live
FILE_NAME = 'data/historical.csv'


def stock_sentiment(quote, num_tweets):
    # Checks if the sentiment for our quote is

    # positive or negative, returns True if
    # majority of valid tweets have positive sentiment
    list_of_tweets = user.search(quote, count=num_tweets)
    positive, null = 0, 0

    for tweet in list_of_tweets:
        print("---------------" + tweet.text)
        blob = TextBlob(tweet.text).sentiment
        if blob.subjectivity == 0:
            null += 1
            next
        if blob.polarity > 0:
            positive += 1

    if positive > ((num_tweets - null) / 2):
        return True


def get_historical(quote):
    # Download our file from google finance
    url = 'http://www.google.com/finance/historical?q=NASDAQ%3A' + quote + '&output=csv'
    r = requests.get(url, stream=True)

    if r.status_code != 400:
        with open(FILE_NAME, 'wb') as f:
            for chunk in r:
                f.write(chunk)

        return True


def stock_prediction():
    # Collect data points from csv
    dataset = []

    with open(FILE_NAME) as f:
        for n, line in enumerate(f):
            if n != 0:
                dataset.append(float(line.split(',')[1]))

    dataset = np.array(dataset)

    # Create dataset matrix (X=t and Y=t+1)
    def create_dataset(dataset):
        dataX = [dataset[n + 1] for n in range(len(dataset) - 2)]
        return np.array(dataX), dataset[2:]

    trainX, trainY = create_dataset(dataset)

    # Create and fit Multilinear Perceptron model
    model = Sequential()
    model.add(Dense(8, input_dim=1, activation='relu'))
    model.add(Dense(1))
    model.compile(loss='mean_squared_error', optimizer='adam')
    model.fit(trainX, trainY, nb_epoch=200, batch_size=2, verbose=2)

    # Our prediction for tomorrow
    prediction = model.predict(np.array([dataset[0]]))
    result = 'The price will move from %s to %s' % (dataset[0], prediction[0][0])

    return result


# Ask user for a stock quote
# stock_quote = raw_input('Enter a stock quote from NASDAQ (e.j: AAPL, FB, GOOGL): ').upper()

# Check if the stock sentiment is positve
if not stock_sentiment('FB', num_tweets=100):
    print('This stock has bad sentiment, please re-run the script')
    sys.exit()

# Check if we got te historical data
if not get_historical('FB'):
    print('Google returned a 404, please re-run the script and')
    print('enter a valid stock quote from NASDAQ')
    sys.exit()

# We have our file so we create the neural net and get the prediction
print(stock_prediction())

# We are done so we delete the csv file
# os.remove(FILE_NAME)

parsedNews = feedparser.parse('http://feeds.finance.yahoo.com/rss/2.0/headline?s=FB&region=US&lang=en-US')
num_of_news = len(parsedNews['entries'])
positive, null = 0, 0

for index in range(num_of_news):
    news = parsedNews['entries'][index]['title'];
    print("News : " + news)
    blob = TextBlob(news).sentiment
    if blob.subjectivity == 0:
        null += 1
        next
    if blob.polarity > 0:
        positive += 1

if positive > ((num_of_news - null) / 2):
    print('Sentiment is positive')
    # return True
else:
    print('Sentiment is negative')

