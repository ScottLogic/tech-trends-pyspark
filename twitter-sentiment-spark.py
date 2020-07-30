import sparknlp
from sparknlp.pretrained import PretrainedPipeline
from pyspark.sql import SparkSession
from pyspark.sql.types import *
from pyspark.sql.functions import from_json

# Load from Kinesis Stream
rawData = spark\
    .readStream\
    .format("kinesis")\
    .option("streamName", "tech-trends-stream")\
    .option("endpointUrl", "https://kinesis.eu-west-2.amazonaws.com")\
    .load()

tweetSchema = StructType() \
    .add("text", StringType()) \
    .add("hashtags", ArrayType(StringType())) \

# Extract JSON data from Kinesis message
tweets = rawData \
    .selectExpr("cast (data as STRING) jsonData") \
    .select(from_json("jsonData", tweetSchema).alias("tweets")) \
    .select('tweets.text')

# Load Pipeline and Transform for Sentiment
pipeline = PretrainedPipeline("analyze_sentiment", lang="en")
sentiments = pipeline.transform(tweets)

result = sentiments.select('text','sentiment')

# Write to JSON in S3
query = sentiments.writeStream\
    .format("json")\
    .option("path", "s3a://tech-trends-output/sentiments")\
    .option("checkpointLocation", "s3a://tech-trends-output/sentiments/checkpoint")\
    .start()
