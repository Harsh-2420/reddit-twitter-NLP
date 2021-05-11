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


@app.route('/')
def index():
    # Access Twitter API
    auth = tweepy.OAuthHandler(
        twitter_consumer_key, twitter_consumer_secret, twitter_callback_uri)
    auth.set_access_token(twitter_access_token, twitter_access_token_secret)
    api = tweepy.API(auth)
    df = get_df(api)
    df = df.to_dict()
    session['df'] = df
    return render_template('index.html')


@app.route('/chart1')
def chart1():
    df = session.get('df', None)
    df = pd.DataFrame(df)
    fig = go.Figure()
    fig.add_trace(go.Table(
        header=dict(values=list(df.columns),
                    fill_color='paleturquoise',
                    align='left'),
        cells=dict(values=[df.name, df.location, df.text],
                   fill_color='lavender',
                   align='left'))
                  )

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    header = "Fruit in North America"
    description = """
    A academic study of the number of apples, oranges and bananas in the cities of
    San Francisco and Montreal would probably not come up with this chart.
    """
    return render_template('notdash2.html', graphJSON=graphJSON, header=header, description=description)


@app.route('/chart2')
def chart2():
    df = pd.DataFrame({
        "Vegetables": ["Lettuce", "Cauliflower", "Carrots", "Lettuce", "Cauliflower", "Carrots"],
        "Amount": [10, 15, 8, 5, 14, 25],
        "City": ["London", "London", "London", "Madrid", "Madrid", "Madrid"]
    })

    fig = px.bar(df, x="Vegetables", y="Amount", color="City", barmode="stack")

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    header = "Vegetables in Europe"
    description = """
    The rumor that vegetarians are having a hard time in London and Madrid can probably not be
    explained by this chart.
    """
    return render_template('notdash2.html', graphJSON=graphJSON, header=header, description=description)


def get_df(api):
    tweets = tweepy.Cursor(api.search, q='london',
                           result_type='popular').items(3)
    keyword_df = pd.DataFrame()
    name = []
    location = []
    text = []

    for tweet in tweets:
        name.append(tweet.user.name)
        location.append(tweet.user.location)
        text.append(tweet.text)

    keyword_df['name'] = name
    keyword_df['location'] = location
    keyword_df['text'] = text

    return keyword_df


if __name__ == '__main__':

    app.config['SESSION_TYPE'] = 'filesystem'

    sess.init_app(app)
    app.run(debug=True)
