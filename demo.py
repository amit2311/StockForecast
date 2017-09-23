import sys
import requests
import numpy as np

from keras.models import Sequential
from keras.layers import Dense


# Where the csv file will live
FILE_NAME = 'data/historical.csv'


def get_historical_India(quote):
    # Download our file from google finance
    url = 'https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY&symbol='+quote+'&apikey=3FGHYHL0CV6P6P04&datatype=csv'
    r = requests.get(url, stream=True)

    if r.status_code != 400:
        with open(FILE_NAME, 'wb') as f:
            for chunk in r:
                f.write(chunk)

        return True

#Not using anymore
# def get_historical(quote):
#     # Download our file from google finance
#     url = 'http://www.google.com/finance/historical?q=NASDAQ%3A' + quote + '&output=csv'
#     r = requests.get(url, stream=True)
#
#     if r.status_code != 400:
#         with open(FILE_NAME, 'wb') as f:
#             for chunk in r:
#                 f.write(chunk)
#
#         return True


def stock_prediction():
    # Collect data points from csv
    dataset = []

    with open(FILE_NAME) as f:
        for n, line in enumerate(f):
            if n != 0:
                dataset.append(float(line.split(',')[1]))

    dataset = np.array(dataset)
    print(dataset)
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


# Check if we got te historical data
if not get_historical_India('NSE:INFY'):
    print('Google returned a 404, please re-run the script and')
    print('enter a valid stock quote from NASDAQ')
    sys.exit()


# We have our file so we create the neural net and get the prediction
print(stock_prediction())
print('Stock prediction done.')
