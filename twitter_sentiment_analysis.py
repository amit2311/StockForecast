import re
import tweepy
from tweepy import OAuthHandler
from textblob import TextBlob

class TwitterClient(object):
    # keys and tokens from the Twitter Dev Console
    consumer_key = ''
    consumer_secret = ''
    access_token = ''
    access_token_secret = ''
    positive_tweets = []
    negative_tweets = []
    neutral_tweets = []
    all_tweets = []

    def __init__(self):

        # attempt authentication
        try:
            # create OAuthHandler object
            self.auth = OAuthHandler(self.consumer_key, self.consumer_secret)
            # set access token and secret
            self.auth.set_access_token(self.access_token, self.access_token_secret)
            # create tweepy API object to fetch tweets
            self.api = tweepy.API(self.auth)
        except:
            print("Error: Authentication Failed")

    def _main(self, query, count):
        try:
            # call twitter api to fetch tweets
            tweet_list = self.api.search(q=query, count=count)
            for tweet in tweet_list:
                # ignore retweets
                if (not tweet.retweeted) and ('RT @' not in tweet.text):
                    # print(tweet.text)
                    self.all_tweets.append(tweet.text)
                    # clean tweet text before try to predict sentiment
                    # by remove user mentions urls and other special symbolic chars
                    tweet_text = ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet.text,
                                                 flags=re.MULTILINE).split())

                    # saving sentiment of tweet
                    analysis = TextBlob(tweet_text)

                    if analysis.sentiment.polarity > 0:
                        self.positive_tweets.append(tweet_text)
                    elif analysis.sentiment.polarity == 0:
                        self.neutral_tweets.append(tweet_text)
                    else:
                        self.negative_tweets.append(tweet_text)
        except tweepy.TweepError as e:
            # print error (if any)
            print("Error : " + str(e))

    def predict_stock_sentiment(self, query, count=100):
        # add re-tweet filter
        self._main(query + '-filter:retweets', count)
        # % of +ve tweets
        print("+ve : {} %".format(100 * len(self.positive_tweets) / len(self.all_tweets)))
        # % of -ve tweets
        print("-ve: {} %".format(100 * (len(self.negative_tweets) / len(self.all_tweets))))
        # % of neutral tweets
        print("Neutral: {} %".format(100 * len(self.neutral_tweets) / len(self.all_tweets)))

        print("\n\nNegative tweets:")
        for tweet in self.negative_tweets[:10]:
            print('-ve Tweet- ' + tweet)

        print("\n\nPositive tweets:")
        for tweet in self.positive_tweets[:10]:
            print('+ve Tweet- ' + tweet)

        print("\n\nNeutral tweets:")
        for tweet in self.neutral_tweets[:10]:
            print('= Tweet- ' + tweet)


def main():
    client = TwitterClient()
    client.predict_stock_sentiment(query='Apple Stocks', count=900)


if __name__ == "__main__":
    # calling main function
    main()
