"tweeting.py - interface to twitter for mps_edits"

import twitter # pip install python-twitter

# Get credentials by creating an app at https://apps.twitter.com/
api = twitter.Api(
    consumer_key=consumer_key,
    consumer_secret=consumer_secret,
    access_token_key=access_token_key,
    access_token_secret=access_token_secret)

print api.VerifyCredentials()
status = api.PostUpdate('Test post')
print status.text
