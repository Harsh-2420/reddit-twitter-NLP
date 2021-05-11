from flask import Flask, render_template, redirect, url_for, session
import pandas as pd
import json
import plotly
import plotly.express as px
import plotly.graph_objects as go
from gitignore.config import *
import tweepy
from flask_session import Session
import webbrowser

# Initialise Flask App
app = Flask(__name__)
app.secret_key = 'super secret key'
sess = Session()
WORLD = 1
CANADA = 23424775


@app.route('/')
def index():
    # Access Twitter API
    auth = tweepy.OAuthHandler(
        twitter_consumer_key, twitter_consumer_secret, twitter_callback_uri)
    auth.set_access_token(twitter_access_token, twitter_access_token_secret)
    api = tweepy.API(auth)

    # Data Extraction
    top_tweets_df = get_tweets_df(api)
    top_tweets_df = top_tweets_df.to_dict()
    session['top_tweets_df'] = top_tweets_df

    trends = get_trending_tweet_location(api)
    trends = trends.to_dict()
    session['trends'] = trends

    return render_template('index.html')


@app.route('/chart1')
def chart1():
    top_tweets_df = session.get('top_tweets_df', None)
    top_tweets_df = pd.DataFrame(top_tweets_df)
    d = dict(tuple(top_tweets_df.groupby('result_type')))
    fig = go.Figure()
    fig.add_trace(go.Table(
        header=dict(values=['location', 'name', 'text'],
                    fill_color='paleturquoise',
                    align='left'),
        cells=dict(values=[d['popular'].name, d['popular'].location, d['popular'].text],
                   fill_color='lavender',
                   align='left'))
                  )
    fig.add_trace(go.Table(
        header=dict(values=['location', 'name', 'text'],
                    fill_color='paleturquoise',
                    align='left'),
        cells=dict(values=[d['recent'].name, d['recent'].location, d['recent'].text],
                   fill_color='lavender',
                   align='left'))
                  )
    fig.update_layout(width=700, height=600)
    fig.update_layout(
        updatemenus=[go.layout.Updatemenu(
            active=0,
            buttons=list(
                [dict(label='popular',
                      method='update',
                      args=[{'visible': [True, False]},
                            ]),
                 dict(label='recent',
                      method='update',
                      args=[{'visible': [False, True]},
                            ]),
                 ])
        )
        ]
    )

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    header = "Get top tweets based on a keyword"
    description = """
    Use a given keyword to get most popular tweets. Give option for recent and custom keyword
    """
    return render_template('notdash2.html', graphJSON=graphJSON, header=header, description=description)


@app.route('/chart2')
def chart2():
    trends = session.get('trends', None)
    trends = pd.DataFrame(trends)
    trends = trends.sort_values('volume', ascending=False)
    d = dict(tuple(trends.groupby('id')))
    fig = go.Figure()
    fig.add_trace(go.Table(
        header=dict(values=['tweet', 'volume'],
                    fill_color='paleturquoise',
                    align='left'),
        cells=dict(
            values=[d['world'].tweet, d['world'].volume],
            fill_color='lavender',
            align='left')))
    fig.add_trace(go.Table(
        header=dict(values=['tweet', 'volume'],
                    fill_color='paleturquoise',
                    align='left'),
        cells=dict(
            values=[d['canada'].tweet, d['canada'].volume],
            fill_color='lavender',
            align='left')))
    fig.update_layout(width=700, height=600)
    fig.update_layout(
        updatemenus=[go.layout.Updatemenu(
            active=0,
            buttons=list(
                [dict(label='world',
                      method='update',
                      args=[{'visible': [True, False]},
                            ]),
                 dict(label='canada',
                      method='update',
                      args=[{'visible': [False, True]},
                            ]),
                 ])
        )
        ]
    )

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    header = "Trending tweets from location keyword"
    description = """ Using a location keyword (convert to dropdown) to get trending tweets in last 24 hours """
    return render_template('notdash2.html', graphJSON=graphJSON, header=header, description=description)


def get_tweets_df(api):
    top_tweets = tweepy.Cursor(api.search, q='london',
                               result_type='popular').items(3)
    recent_tweets = tweepy.Cursor(api.search, q='london',
                                  result_type='recent').items(3)
    keyword_df = pd.DataFrame()
    name = []
    location = []
    text = []
    result_type = []

    for tweet in top_tweets:
        name.append(tweet.user.name)
        location.append(tweet.user.location)
        text.append(tweet.text)
        result_type.append('popular')

    for tweet in recent_tweets:
        name.append(tweet.user.name)
        location.append(tweet.user.location)
        text.append(tweet.text)
        result_type.append('recent')

    keyword_df['name'] = name
    keyword_df['location'] = location
    keyword_df['text'] = text
    keyword_df['result_type'] = result_type

    return keyword_df


def get_trending_tweet_location(api):

    wrld_trends = api.trends_place(id=WORLD)
    canada_trends = api.trends_place(id=CANADA)
    trends = []
    # i = []
    for trend in wrld_trends[0]['trends']:
        # i.append(WORLD)
        if trend['tweet_volume'] is not None and trend['tweet_volume'] > 10000:
            trends.append((trend['name'], trend['tweet_volume'], 'world'))

    for trend in canada_trends[0]['trends']:
        # i.append(WORLD)
        if trend['tweet_volume'] is not None and trend['tweet_volume'] > 10000:
            trends.append((trend['name'], trend['tweet_volume'], 'canada'))

    # trends.sort(key=lambda x: -x[1])
    trends = pd.DataFrame(trends)
    # trends["id"] = i

    trends.columns = ['tweet', 'volume', 'id']
    return trends


if __name__ == '__main__':

    app.config['SESSION_TYPE'] = 'filesystem'

    sess.init_app(app)
    app.run(debug=True)
