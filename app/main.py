from flask import Flask, render_template, request, jsonify, redirect
import gspread
from datetime import datetime

app = Flask(__name__)
gc = gspread.service_account(filename='gsheet_credentials.json')
sh = gc.open_by_key('1BW-qsvVEo54Xyv_8L1HK3FHx6e04Da97lwnhu02PgqI')
worksheet = sh.sheet1


class Tweet:

    def __init__(self, message, time, done, row_index):
        self.message = message
        self.time = time
        self.done = done
        self.row_index = row_index

def get_date_time(date_time_str):
        date_time_obj = None
        error_code = None
        try:
            date_time_obj = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')
        except ValueError as e:
            error_code = "Wrong date time format"
        if date_time_obj is not None:
            now_time = datetime.now()
            if not date_time_obj > now_time:
                error_code= "Time must be in the future"
        return date_time_obj, error_code


@app.route('/')
def tweet_list():
    tweet_records = worksheet.get_all_records()
    tweets = []
    for index, tweet in enumerate(tweet_records, start=2):
        tweet = Tweet(**tweet, row_index = index)
        tweets.append(tweet)
    tweets.reverse()
    n_open_tweets = sum(1 for tweet in tweets if not tweet.done)
    return render_template('base.html', tweets = tweets, n_open_tweets = n_open_tweets)

@app.route('/tweet', methods=['POST'])
def add_tweet():
    message = request.form['message']
    if not message:
        return jsonify({"error": "No tweet entered"}), 400
    time = request.form['time']
    if not time:
        return jsonify({"error": "Schedule time not given"}),400
    if len(message) > 280:
        return jsonify({"error": "Tweet too long"})
    date_time_obj, error_code = get_date_time(time)
    if error_code is not None:
        return jsonify({"error": error_code})
    tweet = [str(date_time_obj), message, 0]
    worksheet.append_row(tweet)
    return redirect('/')


@app.route('/delete/<int:row_index>')
def delete_tweet(row_index):
    worksheet.delete_row(row_index)
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)