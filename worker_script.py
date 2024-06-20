from os import environ
import gspread
import tweepy 
from dotenv import load_dotenv
import time
import logging
from datetime import datetime
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


API_KEY=environ['API_KEY']
API_KEY_SECRET=environ['API_KEY_SECRET']
ACCESS_TOKEN=environ['ACCESS_TOKEN']
ACCESS_TOKEN_SECRET=environ['ACCESS_TOKEN_SECRET']
BEARER_TOKEN=environ['BEARER_TOKEN']
INTERVAL=int(environ['INTERVAL'])
DEBUG=environ['DEBUG'] == '1'


client = tweepy.Client(bearer_token=BEARER_TOKEN, access_token=ACCESS_TOKEN, access_token_secret=ACCESS_TOKEN_SECRET, consumer_key=API_KEY, consumer_secret=API_KEY_SECRET)
auth = tweepy.OAuth1UserHandler(API_KEY, API_KEY_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
old_api = tweepy.API(auth)


gc = gspread.service_account(filename='gsheet_credentials.json')
sh = gc.open_by_key('1BW-qsvVEo54Xyv_8L1HK3FHx6e04Da97lwnhu02PgqI')
worksheet = sh.sheet1

def main():
    while True:
        tweet_records = worksheet.get_all_records()
        now_time = datetime.now()
        logger.info(f'{len(tweet_records)} tweets found at {now_time.time()}')

        for index, tweet in enumerate(tweet_records, start=2):
            message = tweet['message']
            time_str = tweet['time']
            done = tweet['done']
            date_time_obj = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
            if not done:
                if date_time_obj < now_time:
                    logger.info('This should be tweeted')
                    try:
                        client.create_tweet(text=message)
                        worksheet.update_cell(index, 3, 1)
                    except Exception as e:
                        logger.warning(f'exception during tweet! {e}')
        time.sleep(INTERVAL)
    


if __name__ == '__main__':
    main()