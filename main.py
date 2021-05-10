import pandas as pd
import numpy as np
from gitignore.config import *

# Reddit imports
import praw
import requests
from datetime import datetime


# Dash and Plotly
import plotly.express as px
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

app = dash.Dash(__name__)

# Getting Reddit Data
reddit = praw.Reddit(client_id=reddit_client_id, client_secret=reddit_client_secret,
                     username=reddit_username, user_agent=reddit_user_agent)
keyword = 'london'
subreddit = reddit.subreddit(keyword)

# Creating the Data Frame
df = pd.DataFrame()
id_list = []
title = []
author = []
comments = []
date = []
for sub in subreddit.hot(limit=125):
    time = datetime.utcfromtimestamp(sub.created).strftime('%Y-%m-%d')
    id_list.append(sub.id)
    title.append(sub.title)
    author.append(sub.author)
    comments.append(sub.num_comments)
    date.append(time)

columns = ['post_id', 'title', 'author', 'total comments', 'date posted']
df['post_id'] = id_list
df['title'] = title
df['author'] = author
df['total comments'] = comments
df['date'] = date
