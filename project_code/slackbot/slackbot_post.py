import requests
import sqlalchemy
import pandas as pd
import time

# wait for 20 second for slackbot post
time.sleep(20)

WEBHOOK_URL = 'https://hooks.slack.com/services/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'


def get_emoji_sentiment(score):
    if score >= 0.05:
        emoji = ':grin:'
    elif score <= -0.05:
        emoji = ':face_with_rolling_eyes:'
    else:
        emoji = ':neutral_face:'
    return emoji

# 1) connecting to postgres
pg = sqlalchemy.create_engine(
    'postgresql://postgres:postgres@postgresdb:5432/posts',
    echo=True
    )
connection = pg.connect()

# 2) querying data from postgres
query = '''
    SELECT * FROM post_sentiment
    LIMIT 5
'''
df_posts = pd.read_sql(query,connection)

# 3) posting the data on slack

for i in range(5):
    row = df_posts.iloc[i]
    text = str(row['post_text'])
    sentiment_score = row['sentiment_score']
    emoji = get_emoji_sentiment(sentiment_score)
    sentiment = f"*Score: {str(sentiment_score)}  {emoji} *"
    data={
        "blocks": [
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "plain_text",
                    "text": text
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": sentiment
                }
            }
        ]
    }
    requests.post(url=WEBHOOK_URL, json=data)
    time.sleep(20)
