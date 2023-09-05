# reddit-sentiment-analysis
Build a Dockerized Data Pipeline that analyzes the sentiment of reddits.

In this project, a data pipeline is created that collects reddits and stores them in MongoDB. 
The sentiment of reddits is then analyzed and the annotated text is stored in a PostgresDB. This post is then published to slack using a slackbot.

### Process:
1. Build a data pipeline with docker-compose
2. Collect data from reddit
3. Store data in Mongo DB
4. Create an ETL job transporting data from MongoDB to PostgreSQL
5. Run sentiment analysis on the text
6. Build a Slack bot that publishes selected reddits
