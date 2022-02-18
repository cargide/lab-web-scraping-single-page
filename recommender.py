# imports
import pickle

import pandas as pd
import numpy as np

import json
from random import randint
from time import sleep

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

from sklearn.cluster import DBSCAN
from sklearn.neighbors import NearestNeighbors

from sklearn import cluster

# read files
spotify = pd.read_csv('spotify.csv')
top_lists = pd.read_csv('top_lists.csv')

std = pickle.load(open('std.p', 'rb'))
kmeans = pickle.load(open('kmeans.p', 'rb'))

# functions
def song_uri(song):
    q='track:'+ song# +'&artist:'+ artists
    uri = sp.search(q=q, limit=1)['tracks']['items'][0]['uri']

    return uri

def find_features(uri):
    try:
        features = sp.audio_features(uri)
    except:
        features = 0
    return features

def is_in_top(top_lists=top_lists):
    print('Please, write your song')
    name = input()

    songs = pd.Series(top_lists.song)

    flag = name in songs.unique()

    return flag, name

def top_reccomendation(name, top_lists=top_lists):
    l = len(top_lists)
    i = randint(0, l)
    while top_lists['song'][i] == name:
        i = randint(0, l)

    song = top_lists['song'][i]
    artist = top_lists['artist'][i]

    return song, artist

# initialization for spotipy
secrets_file = open("SpotifySecret.txt","r")
string = secrets_file.read()
secret_string = string.split('\n')

secrets_dict={}
for line in secret_string:
    if len(line) > 0:
        secrets_dict[line.split(':')[0]]=line.split(':')[1]

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=secrets_dict['cid'],
                                                           client_secret=secrets_dict['cs']))

# recommender
def recommender(spotify=spotify, tops=top_lists, std=std, kmeans=kmeans):
    flag,name =  is_in_top(top_lists)

    if flag:
        #If song in top list, returns another one
        song, artist = top_reccomendation(name)

    else:
        # Clustering
        uri = song_uri(name) #Needs treatment if not found
        features = pd.DataFrame(find_features(uri))
        features.drop(['type', 'id', 'uri', 'track_href', 'analysis_url'], axis=1, inplace=True)
        cols = features.columns
        features_t = std.transform(features)
        features_std = pd.DataFrame(features_t,columns=cols)

        cluster = kmeans.predict(features_std)[0]
        sublist = spotify.loc[spotify['kmeans_cluster'] == cluster][['song', 'artist']].reset_index(drop=True)
        i = randint(0, len(sublist)-1)

        song = sublist['song'][i]
        artist = sublist['artist'][i]

    print('You can listen to "' + song + '" by ' + artist)

recommender()