import os
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import boto3
import json

# consumer key, consumer secret, access token, access secret.
ckey = os.environ.get('TWITTER_CONSUMER_KEY')
csecret = os.environ.get('TWITTER_CONSUMER_SECRET')
atoken = os.environ.get('TWITTER_AUTH_KEY')
asecret = os.environ.get('TWITTER_SECRET_KEY')

kinesis = boto3.client('kinesis')

class SparkListener(StreamListener):

    def on_status(self, status):
        hashtag_entities = status.entities['hashtags']
        hashtags = list(map(lambda e: e['text'], hashtag_entities))

        output = {'text': status.text, 'hashtags': hashtags}
        try:
            kinesis.put_record(StreamName='tech-trends-stream',
                               Data=json.dumps(output),
                               PartitionKey=output['text'])
            print("Put word into stream")
        except Exception as e:
            print("Error writing to Kinesis" + str(e))

    def on_error(self, status_code):
        print(status_code)


auth = OAuthHandler(ckey, csecret)
auth.set_access_token(atoken, asecret)

twitterStream = Stream(auth, SparkListener())
twitterStream.filter(track=["python"])
