import re
import math
import tweepy
import feedparser
from tweepy import OAuthHandler
from textblob import TextBlob


class TwitterClient(object):
    # keys and tokens from the Twitter Dev Console
    consumer_key = ''
    consumer_secret = ''
    access_token = ''
    access_token_secret = ''
    positive_news = []
    negative_news = []
    neutral_news = []
    all_news = []

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

    def read_tweets(self, query, count):
        try:
            # call twitter api to fetch tweets
            tweet_list = self.api.search(q=query, count=count)
            for tweet in tweet_list:
                # ignore retweets
                if (not tweet.retweeted) and ('RT @' not in tweet.text):
                    # print(tweet.text)
                    self.all_tweets.append(self.clean_text(tweet.text))
        except Exception as e:
            # print error (if any)
            print("Error : " + str(e))

    def read_google_news_feed(self, quote, news_count=100):
        try:
            parsed_news = feedparser.parse(
                "https://finance.google.com/finance/company_news?q={}&output=rss&num={}".format(quote, news_count))
            for index in range(len(parsed_news['entries'])):
                self.all_news.append(self.clean_text(parsed_news['entries'][index]['title']))
        except Exception as e:
            print("<p>Error: %s</p>" % e)

    # by remove user mentions urls and other special symbolic chars
    def clean_text(self, text):
        return ' '.join(
            re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", text, flags=re.MULTILINE).split())

    def predict_stock_sentiment(self, quote, count=100):
        result = {}
        news_sentiment = {}
        tweet_sentiment = {}

        # read twitter feed, use keywords with company quotes + " Stocks " etc.
        tokens = quote.split(":")
        if len(tokens) > 1:
            tweet_search = tokens[1] + " Stocks "
        else:
            tweet_search = quote + " Stocks "
        self.read_tweets(tweet_search + '-filter:retweets', count)

        self.read_google_news_feed(quote, count)

        for news in self.all_news:
            # saving sentiment of tweet
            # print('News- '+news)
            analysis = TextBlob(news)
            if analysis.sentiment.polarity > 0:
                self.positive_news.append(news)
            elif analysis.sentiment.polarity == 0:
                self.neutral_news.append(news)
            else:
                self.negative_news.append(news)

        total_news_count = len(self.all_news)
        positive_news_count = len(self.positive_news)
        negative_news_count = len(self.negative_news)
        neutral_news_count = len(self.neutral_news)

        news_sentiment['positive_per'] = round(100 * (positive_news_count / total_news_count), 2)
        news_sentiment["negative_per"] = round(100 * (negative_news_count / total_news_count), 2)
        news_sentiment["neutral_per"] = round(100 * (neutral_news_count / total_news_count), 2)

        news_sentiment["positive_count"] = positive_news_count
        news_sentiment["negative_count"] = negative_news_count
        news_sentiment["neutral_count"] = neutral_news_count
                      
        print("\n\nNegative news:")
        for news in self.negative_news[:10]:
            print('-ve news- ' + news)

        print("\n\nPositive news:")
        for news in self.positive_news[:10]:
            print('+ve news- ' + news)

        print("\n\nNeutral news:")
        for news in self.neutral_news[:10]:
            print('= news- ' + news)

        for tweet in self.all_tweets:
            # saving sentiment of tweet
            # print('News- '+news)
            analysis = TextBlob(tweet)
            if analysis.sentiment.polarity > 0:
                self.positive_tweets.append(tweet)
            elif analysis.sentiment.polarity == 0:
                self.neutral_tweets.append(tweet)
            else:
                self.negative_tweets.append(tweet)

        total_tweet_count = len(self.all_tweets)
        positive_tweet_count = len(self.positive_tweets)
        negative_tweet_count = len(self.negative_tweets)
        neutral_tweet_count = len(self.neutral_tweets)

        tweet_sentiment["positive_per"] = round(100 * (positive_tweet_count / total_tweet_count), 2)
        tweet_sentiment["negative_per"] = round (100 * (negative_tweet_count / total_tweet_count), 2)
        tweet_sentiment["neutral_per"] =  round(100 * (neutral_tweet_count / total_tweet_count), 2)

        tweet_sentiment["positive_count"] = positive_tweet_count
        tweet_sentiment["negative_count"] = negative_tweet_count
        tweet_sentiment["neutral_count"] = neutral_tweet_count

        print("\n\nNegative tweets:")
        for tweet in self.negative_tweets[:10]:
            print('-ve tweet- ' + tweet)

        print("\n\nPositive tweet:")
        for tweet in self.positive_tweets[:10]:
            print('+ve tweet- ' + tweet)

        print("\n\nNeutral tweet:")
        for tweet in self.neutral_tweets[:10]:
            print('= tweet- ' + tweet)

        result["tweet_sentiment"] = tweet_sentiment
        result["news_sentiment"] = news_sentiment

        return result


def main():
    client = TwitterClient()
    # client.get_google_finance_news_feed('NASDAQ:FB',100)
    result = client.predict_stock_sentiment(quote='NSE:TCS', count=500)
    print(result)


if __name__ == "__main__":
    # calling main function
    main()
