# apt install python-pip
# pip install selenium
# pip install requests
# pip install chromedriver-autoinstaller

import base64
import webbrowser
import time
import datetime
import sys
import json
import requests as req
import chromedriver_autoinstaller
from os import path
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

clientId = "648f3dc76d64441abf6a5fc53fcdd843"

waitLoginOption = True
facebookOption = False
appleOption = False
phoneOption = False
emailOption = False

today = datetime.date.today()

# Criar parametro para atualizar o json das playlists
updatePlaylistsJSON = False

# Limit date is the date under x days from today. This date is used to get musics where date is
# equal or greater than this date
# Fazer parametros de chamada do programa
# Fazer o tratamento para o GMT
limitDate = datetime.date(today.year, today.month, today.day - int(sys.argv[1]))

# waitLoginTime = 20 # Seconds

"""
face <a ng-href="https://www.facebook.com/
apple <a ng-href="https://appleid.apple.com
phone <div class="row ng-scope" ng-if="phoneBtnEnabled">
email <input ng-model="form.username"
"""

def getSpotifyToken():
    url = "https://accounts.spotify.com/authorize?client_id={}&response_type=token&redirect_uri={}" \
        "&scope=user-read-private playlist-read-private user-library-read " \
        "playlist-read-collaborative".format(clientId, 'https://www.google.com.br')
    
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--mute-audio")
    chrome_options.add_argument('--no-sandbox')
    chromedriver_autoinstaller.install()
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    
    if waitLoginOption:
        while 'google' not in '{uri.scheme}://{uri.netloc}/'.format(uri=urlparse(driver.current_url)):
            # Do the login...
            time.sleep(2)
    
    # Tratar falha, deny do login
    
    token = getTokenFromURL(driver.current_url)
    
    driver.close()
    
    return token

def getTodayLikedMusics(token):
    url = "https://api.spotify.com/v1/me/tracks?offset=0&limit=50"
    
    r = req.get(url=url, headers={'Authorization':'Bearer ' + token})
    
    data = r.json()
    r.close()
    
    if r.status_code != 200:
        print('An error ocurred trying to get today liked musics.\nError: {}'.format(data['error']))
        return None
    
    for music in data['items']:
        date_parts = str(music['added_at']).split('-')
        day = int(date_parts[2].split('T')[0])
        month = int(date_parts[1])
        year = int(date_parts[0])
        
        music_date = datetime.date(year, month, day)
        if music_date >= limitDate:
            # Tratar caso de ter mais musicas
            # Fazer tratamento para vibes usando get-audio-features/
            genres = getArtistGenres(token, music['track']['artists'][0]['id'])
            
            print("Genres = {}".format(genres))
            
def getArtistGenres(token, artistID):
    url = "https://api.spotify.com/v1/artists/{}".format(artistID)
    
    r = req.get(url=url, headers={'Authorization':'Bearer ' + token})
    
    data = r.json()
    r.close()
    
    if r.status_code != 200:
        print('An error ocurred trying to get the Artist of a music.\nError: {}'.format(data['error']))
        return None
    
    return data['genres']

def getUserPlaylists(token, name):
    if (not path.exists("playlists.json")) or updatePlaylistsJSON:
        url = "https://api.spotify.com/v1/me/playlists?limit=50&offset=0"
        r = req.get(url=url, headers={'Authorization':'Bearer ' + token})
        
        data = r.json()
        r.close()
    
        if r.status_code != 200:
            print('An error ocurred trying to get the user playlists.\nError: {}'.format(data['error']))
            return None
        
        # Tratar caso de ter mais playlists
        jsonfile = open(file="playlists.json", mode="w", encoding="utf-8")
        
        playlists_data = {}
        playlists_data['playlists'] = []
        
        playlists = data['items']
        for playlist in playlists:
            if playlist['owner']['display_name'] == name:
                playlists_data['playlists'].append({
                    'name': playlist['name'],
                    'id': playlist['id'],
                    'genres': getPlaylistGenres(token, playlist['id'])
                })
        
        while data['next'] != "null":
            url = data['next']
            r = req.get(url=url, headers={'Authorization':'Bearer ' + token})
            data = r.json()
            r.close()
            if r.status_code != 200:
                print('An error ocurred trying to get the user playlists.\nError: {}'.format(data['error']))
                return None
            
            playlists = data['items']
            for playlist in playlists:
                if playlist['owner']['display_name'] == name:
                    playlists_data['playlists'].append({
                        'name': playlist['name'],
                        'id': playlist['id'],
                        'genres': getPlaylistGenres(token, playlist['id'])
                    })
        
        json.dump(playlists_data, jsonfile)

        
def getPlaylistGenres(token, playlistId):
    url = "https://api.spotify.com/v1/playlists/{}/tracks?fields=items(track(artists(id)))".format(playlistId)
    r = req.get(url=url, headers={'Authorization':'Bearer ' + token})
    
    data = r.json()
    r.close()

    if r.status_code != 200:
        print('An error ocurred trying to get tracks of one playlist.\nError: {}'.format(data['error']))
        return ''
    
    artists = []
    genres = []
    
    for track in data['items']:
        for artist in track['track']['artists']:
            if artist['id'] not in artists:
                artists.append(artist['id'])
    
    for artist in artists:
        genres_artist = getArtistGenres(token, artist)
        if genres_artist is not None:
            for genre in genres_artist:
                if genre not in genres:
                    genres.append(genre)
                
    return genres
    
def getUserName(token):
    url = "https://api.spotify.com/v1/me"
    r = req.get(url=url, headers={'Authorization':'Bearer ' + token})
    
    data = r.json()
    r.close()

    if r.status_code != 200:
        print('An error ocurred trying to get the user info.\nError: {}'.format(data['error']))
        return None
    
    return data['display_name']

def getTokenFromURL(url):
    return str(url).split('#')[1].split('&')[0].split('=')[1]

def main():
    token = getSpotifyToken()
    if token != None:
        # print(token)
        name = getUserName(token)
        if name != None:
            getUserPlaylists(token, name)
            # getTodayLikedMusics(token)
    

if __name__ == "__main__":
    main()