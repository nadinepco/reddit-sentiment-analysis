##########################################################################
##########################################################################
                      # EXTRACT TRANSFORM LOAD #
##########################################################################
##########################################################################

# extract stack
from pymongo import MongoClient

# transform stack
import re
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# load stack
#from sqlalchemy import text as dbtext
from sqlalchemy import create_engine, text

# miscellaneous
import logging
import time

logging.warning('\n-----start etl job-----\n')

##########################################################################
                               # EXTRACT #
##########################################################################


def mongodb_connection():
    logging.warning('\n-----start mongodb_connection-----\n')
    """
    conencts to mongodb reddit database
    """
    # establish connection to mongodb container
    client = MongoClient(
        host="mongodb",   # host: name of the container
        port=27017        # port: port inside the container
        )

    # connect to reddit database
    db = client.reddit

    return db


def extract(db, number_of_posts):
    logging.warning('\n-----start extract-----\n')
    """
    extracts posts from the mongodb reddit database
    """
    # connect to the posts collection
    posts = db.posts
    
    # pull out tweets with filter
    extracted_posts = posts.find(limit=number_of_posts)

    return extracted_posts


##########################################################################
                             # TRANSFORM #
##########################################################################


# useful regular expressions
regex_list = [
    '@[A-Za-z0-9]+',  # to find @mentions
    '#',              # to find hashtag symbol
    'RT\s',           # to find retweet announcement
    'https?:\/\/\S+'  # to find most URLs
    ]


def clean_post(post):
    logging.warning('\n-----start clean_post-----\n')
    """
    gets the text of a post and cleans it up 
    """
    # get reddit text
    text = post['text'] 
    logging.debug(f'\ntext: {text}\n')
    # remove all regex patterns
    for regex in regex_list:
        text = re.sub(regex, '', text)  
    
    return text


# instantiate sentiment analyzer
analyzer = SentimentIntensityAnalyzer()


def sentiment_score(text):
    logging.warning('\n-----start sentiment_score-----\n')
    """
    spits out sentiment score of a text
    """
    # calculate polarity scores 
    sentiment = analyzer.polarity_scores(text)
    
    # choose compund polarity score
    score = sentiment['compound'] 

    return score


def transform(post):
    logging.warning('\n-----start transform-----\n')
    """
    transforms extracted tweet: text cleaning and sentiment analysis
    """
    text = clean_post(post)
    score = sentiment_score(text)

    return text, score


##########################################################################
                              # LOAD #
##########################################################################


def postgres_connection():
    logging.warning('\n-----start postgres_connection-----\n')
    """
    establishes connection to postgres database
    """
    # create sql query engine
    pg_engine = create_engine(
        'postgresql://postgres:postgres@postgresdb:5432/posts',
        echo=True
        )

    return pg_engine



def load(pg_engine, transformed_data):
    """
    Loads post text and score into PostgreSQL database.
    """
    # Create a database connection from the engine
    with pg_engine.connect() as connection:
        # Create table of post text and sentiment if necessary
        query = """
        CREATE TABLE IF NOT EXISTS post_sentiment (
            post_text VARCHAR(500),
            sentiment_score NUMERIC
        );
        """
        connection.execute(text(query))
        connection.commit()
        
        # SQL query for inserting text and score data
        insert_query = "INSERT INTO post_sentiment VALUES (:text, :score);"
        
        # Prepare the data as a list of tuples
        data = [{"text": text_data, "score": score} for text_data, score in transformed_data]

        logging.warning(f'\ndata-----\n {data}')
        # Insert new records in the table
        connection.execute(text(insert_query), data)
        connection.commit()


##########################################################################
                           # ETL STEPS #
##########################################################################

# mongodb connection; give mongodb some seconds to start
mongo_db = mongodb_connection()
time.sleep(20)

# extract posts from mongodb
extracted_posts = extract(mongo_db, number_of_posts=10)
logging.warning('\n-----Posts already extracted from MongoDB-----\n')
logging.warning(f'\n-----extracted posts:{extracted_posts}-----\n')

# transform data
transformed_data = [transform(post) for post in extracted_posts]
logging.warning('\n-----Transformed data already generated-----\n')
logging.warning(f'\n-----transformed_data:{transformed_data}-----\n')

# postgres connection
pg_engine = postgres_connection()

# load data into postgres
load(pg_engine, transformed_data)
logging.warning('\n-----Data already loaded into Postgres-----\n')