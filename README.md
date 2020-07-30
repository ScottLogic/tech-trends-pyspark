# tech-trends-pyspark

## Twitter Streamer

This script uses the *Tweepy* library to access the twitter stream API, you then implement a custom `StreamListener` class to add your own behaviour to handle new tweets. Ours calls the *boto3* library which is the AWS Python SDK and uses this to dispatch the tweet to a kinesis stream.   

Requirements:
- Install Python from website
- Install dependencies in a command window - `pip install boto3 tweepy`
- Register for a dev account on Twitter to get API keys, there are 2 sets consumer key/secret and auth key/secret.
- Store API Keys in ENV properties (Env names can be seen near the top of the script)
- Run the script `python ./twitter-streamer.py`
- Check the kineses console/dashboard to see if things are written to the stream

I've been running this on my local PC, though it could be ran on EC2 once things are stable.

## EMR and PySpark

One part of PySpark I've found confusing is that you are running both Python code and Scala code. The cluster is executing the Spark job in Scala and the master node is executing your Spark script in Python.

In order to add a dependency such as `Spark-NLP` you'll need to include both the Python version and the Scala version, and they both have different mechanisms. From the error messages it's not always clear to me which dependency is missing.

### Spark (Scala) Config

EMR provides a cluster configuration ('Software Settings') option from which you can setup Spark config, in particular `spark.jars.packages` can be used to include dependencies (this is also where the kinesis adapter is included). A JSON file for this config is stored in `tech-trends-emr-config` S3 bucket, which can be used when setting up the cluster. These values can be edited while the cluster is running from the 'Configuration' panel

### Python

Python dependencies are installed using pip/conda, which is most easily done using a bootstrap script which is run on all nodes. This is stored in the S3 bucker `tech-trends-emr-config`. Otherwise you can install packages in a notebook using `sc.install_package_pypi("spark-nlp")`

### Spark Cluster Settings

EMR offers a few options to automatically set cluster config based on the instance type but recommends manually setting them based off this [blog](https://aws.amazon.com/blogs/big-data/best-practices-for-successfully-managing-memory-for-apache-spark-applications-on-amazon-emr/) to ensure resources are maximised. 

In particular for us, Spark will auto-set the executor memory + numbers, but doesn't change any settings for the Driver. The Twitter sentiment model is ~950mb and this is loaded when executing on the driver, so the memory allocation has to be increased above the 1GB default.

## Running Spark Jobs
Two options for running jobs, either add an EMR Spark Step which calls `spark-submit` or open a Jupyter Lab notebook, which automatically opens a SparkContext.

I've been favouring the notebook because it's easier for trial and error, but submitting a step would probably be a better long term solution.

**Note:** I've been having problems loading the `analyze_sentimentdl_use_twitter` pipeline, it works in local mode for analysis a single string, but won't work across a cluster due to a TensorFlow problem. This could be a memory issue or could be a versioning issue, I haven't had a chance to solve it. Instead I've been using the simpler `analyze_sentiment` model, which is not trained on tweets.

