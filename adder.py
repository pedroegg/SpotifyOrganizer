# install python-pip
# pip install selenium
# pip install requests
# pip install chromedriver-autoinstaller
# pip install progressbar

import base64
import webbrowser
import time
import datetime
import sys
import json
import progressbar
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

# CONTORNAR ERRO DE SERVICO 500
# Mudar nome da funcao que gera o playlist.json para generatePlaylistsJSON
# Fazer funcoes mais pequenas, para fracionar mais, como por exemplo uma para pegar generos da musica
# Fazer a funcao que pega os generos e liga a playlists
# Fazer a funcao que adiciona nas playlists

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

def getLikedMusics(token):
    def LikedMusicsInRange(url, count, bar):
        r = req.get(url=url, headers={'Authorization':'Bearer ' + token})
        data = r.json()
        r.close()
        
        if r.status_code != 200:
            print('An error ocurred trying to get liked musics.\nError: {}\nURL: {}' \
                .format(data['error'], url))
            return None, count
        
        total = data['total']
        plus_percentage = total/100
        
        for music in data['items']:
            date_parts = str(music['added_at']).split('-')
            day = int(date_parts[2].split('T')[0])
            month = int(date_parts[1])
            year = int(date_parts[0])
            
            music_date = datetime.date(year, month, day)
            if music_date >= limitDate:
                # Fazer tratamento para vibes usando get-audio-features/
                music_genres = []
                for artist in music['track']['artists']:
                    if artist['id'] is not None:
                        genres = getArtistGenres(token, str(artist['id']))
                        for genre in genres:
                            if (genre is not None) and (str(genre) not in music_genres):
                                music_genres.append(str(genre))
                
                # Procurar no json os generos e adicionar nas playlists (bolar um algoritmo)
                count += plus_percentage
                try:
                    bar.update(count)
                except ValueError:
                    bar.update(100)
        
        return data['next'], count
    
    print("Collecting recently saved musics and adding to playlists... Please, wait.")
    bar = progressbar.ProgressBar(maxval=100, \
        widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    bar.start()
    
    next_field, count = LikedMusicsInRange("https://api.spotify.com/v1/me/tracks?offset=0&limit=50", 0, bar)
    while next_field is not None:
        next_field, count = LikedMusicsInRange(next_field, count, bar)
    
    bar.finish()
        
def getArtistGenres(token, artistID):
    url = "https://api.spotify.com/v1/artists/{}".format(artistID)
    
    r = req.get(url=url, headers={'Authorization':'Bearer ' + token})
    
    data = r.json()
    r.close()
    
    if r.status_code != 200:
        print('An error ocurred trying to get the Artist of a music.\nError: {}\nArtistID: {}' \
            .format(data['error'], artistID))
        return None
    
    return data['genres']

def getUserPlaylistsGenres(token, name):
    playlists_data = {}
    playlists_data['playlists'] = []
    # Checar qual playlist falta verificar para fazer update das faltantes ou das musicas faltantes
    # Melhorar performance da funcao, pegando talvez menos musicas de cada playlist para tirar base?
    # Incluir campo de genero mais destacado da playlist?
    
    def getPlaylistInRange(url, count, bar):
        r = req.get(url=url, headers={'Authorization':'Bearer ' + token})
        
        data = r.json()
        r.close()
    
        if r.status_code != 200:
            print('An error ocurred trying to get the user playlists.\nError: {}\nURL: {}' \
                .format(data['error'], url))
            return None, count
        
        total = data['total']
        plus_percentage = total/100
        
        playlists = data['items']
        for playlist in playlists:
            if playlist['owner']['display_name'] == name:
                # sys.stderr.write("Playlist: {}".format(playlist['name']) + '\r')
                # sys.stderr.flush()
                # Fazer o print da playlist atual também
                # Arrumar o problema do Artista None
                playlists_data['playlists'].append({
                    'name': str(playlist['name']),
                    'id': str(playlist['id']),
                    'genres': getPlaylistGenres(token, str(playlist['id']))
                })
            count += plus_percentage
            try:
                bar.update(count)
            except ValueError:
                bar.update(100)
        
        return data['next'], count
    
    if (not path.exists("playlists.json")) or updatePlaylistsJSON:
        print("Updating playlists.json file and analyzing your playlists genres... Please, wait.")
        bar = progressbar.ProgressBar(maxval=100, \
            widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
        bar.start()
        
        next_field, count = getPlaylistInRange("https://api.spotify.com/v1/me/playlists?limit=50&offset=0", 0, bar)
        while next_field is not None:
            next_field, count = getPlaylistInRange(next_field, count, bar)
        
        bar.finish()
        
        with open(file='playlists.json', mode='w', encoding='utf8') as json_file:
            json.dump(playlists_data, json_file, ensure_ascii=False, indent=4)

        
def getPlaylistGenres(token, playlistId):
    url = "https://api.spotify.com/v1/playlists/{}/tracks?fields=items(track(artists(id)))&limit=100" \
        .format(playlistId)
    r = req.get(url=url, headers={'Authorization':'Bearer ' + token})
    
    data = r.json()
    r.close()

    if r.status_code != 200:
        print('An error ocurred trying to get tracks of one playlist.\nError: {}\nPlaylistID: {}' \
            .format(data['error'], playlistId))
        return ''
    
    artists = []
    genres = []
    
    for track in data['items']:
        for artist in track['track']['artists']:
            if (artist['id'] is not None) and (str(artist['id']) not in artists):
                artists.append(str(artist['id']))
    
    for artist in artists:
        genres_artist = getArtistGenres(token, artist)
        if genres_artist is not None:
            for genre in genres_artist:
                if (genre is not None) and (str(genre) not in genres):
                    genres.append(str(genre))
                
    return genres
    
def getUserName(token):
    url = "https://api.spotify.com/v1/me"
    r = req.get(url=url, headers={'Authorization':'Bearer ' + token})
    
    data = r.json()
    r.close()

    if r.status_code != 200:
        print('An error ocurred trying to get the user info.\nError: {}'.format(data['error']))
        return None
    
    return str(data['display_name'])

def getTokenFromURL(url):
    return str(url).split('#')[1].split('&')[0].split('=')[1]

def main():
    token = getSpotifyToken()
    if token != None:
        # print(token)
        name = getUserName(token)
        if name != None:
            getUserPlaylistsGenres(token, name)
            # getLikedMusics(token)
    

if __name__ == "__main__":
    main()