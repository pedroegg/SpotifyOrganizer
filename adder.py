# install python-pip (this is just to get pip install command working)
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
# Fazer cada playlist ter os seus generos mais compativeis, os tops, os que mais bateram
# Fazer o selecionamento das playlists por metadados
# Fazer o selecionamento das playlists por top genre
# Fazer uma maneira mais facil de editar o json
# Fazer parametro para varredura de playlists com apenas playlists selecionadas. Poupar tempo e custo


"""
face <a ng-href="https://www.facebook.com/
apple <a ng-href="https://appleid.apple.com
phone <div class="row ng-scope" ng-if="phoneBtnEnabled">
email <input ng-model="form.username"
"""

def getSpotifyToken():
    url = "https://accounts.spotify.com/authorize?client_id={}&response_type=token&redirect_uri={}" \
        "&scope=user-read-private playlist-read-private user-library-read " \
        "playlist-read-collaborative playlist-modify-public playlist-modify-private" \
        .format(clientId, 'https://www.google.com.br')
        
    chromedriver_autoinstaller.install()
    
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--mute-audio")
    chrome_options.add_argument('--no-sandbox')
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

def organizeLikedMusics(token):
    def LikedMusicsInRange(url):
        r = req.get(url=url, headers={'Authorization':'Bearer ' + token})
        data = r.json()
        r.close()
        
        if r.status_code != 200:
            print('An error ocurred trying to get liked musics.\nError: {}\nURL: {}' \
                .format(data['error'], url))
            return
        
        for music in data['items']:
            date_parts = str(music['added_at']).split('-')
            day = int(date_parts[2].split('T')[0])
            month = int(date_parts[1])
            year = int(date_parts[0])
            
            music_date = datetime.date(year, month, day)
            if not (music_date >= limitDate):
                return None

            # Fazer tratamento para vibes usando get-audio-features/
            music_genres = []
            for artist in music['track']['artists']:
                if artist['id'] is not None:
                    genres = getArtistGenres(token, str(artist['id']))
                    for genre in genres:
                        if (genre is not None) and (str(genre) not in music_genres):
                            music_genres.append(str(genre))
                
                playlistsIds = classifyMusicPlaylistsByTop3Genre(music_genres)
                if playlistsIds is None:
                    return None
                
                addMusicToPlaylists(token, str(music['track']['uri']), playlistsIds)
                music_genres = []
        
        return data['next']
    
    print("Collecting recently saved musics and adding to playlists... Please, wait.")
    
    next_field = LikedMusicsInRange("https://api.spotify.com/v1/me/tracks?offset=0&limit=50")
    while next_field is not None:
        next_field = LikedMusicsInRange(next_field)
    
        
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
                genres, top3genres = getPlaylistGenres(token, str(playlist['id']))
                playlists_data['playlists'].append({
                    'name': str(playlist['name']),
                    'id': str(playlist['id']),
                    'genres': genres,
                    'topGenres': top3genres
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
    url = "https://api.spotify.com/v1/playlists/{}/tracks?fields=items(track(artists(id)))&limit=50" \
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
    count_genres = {}
    
    for track in data['items']:
        for artist in track['track']['artists']:
            if (artist['id'] is not None) and (str(artist['id']) not in artists):
                artists.append(str(artist['id']))
    
    for artist in artists:
        genres_artist = getArtistGenres(token, artist)
        if genres_artist is not None:
            for genre in genres_artist:
                if (genre is not None):
                    if str(genre) not in genres:
                        genres.append(str(genre))
                    if str(genre) in count_genres:
                        count_genres[str(genre)] += 1
                    else:
                        count_genres[str(genre)] = 1
    
    top_genres = sorted(count_genres, key=count_genres.get, reverse=True)[:3]
    return genres, top_genres

def addMusicToPlaylists(token, musicUri, playlistsIds):
    # Reduzir o numero de requests para adicionar a playlist
    # Fazer adicionar varias musicas para a mesma playlist por vez
    # E nao em varias playlists cada musica
    print("Adding music {} to playlists {}".format(musicUri, playlistsIds))
    for playlist in playlistsIds:
        url = "https://api.spotify.com/v1/playlists/{}/tracks?uris={}".format(playlist, musicUri)
        r = req.post(url=url, headers={'Authorization':'Bearer ' + token})
        data = r.json()
        r.close()

        if r.status_code != 201:
            print('An error ocurred trying to add one track in a playlist.\nError: {}\nPlaylistID: {}' \
                "\nMusicURI: {}".format(data['error'], playlist, musicUri))
    

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

def classifyMusicPlaylistsByGenre(genre_list):
    if not path.exists("playlists.json"):
        print("You need to have a playlists.json file! Run it again with the update json parameter.")
        return None
    
    selected_playlists = []
    
    with open("playlists.json", "r") as json_file:
        data = json.load(json_file)
        
    for playlist in data['playlists']:
        for genre in genre_list:
            if str(genre) in playlist['genres']:
                selected_playlists.append(str(playlist['id']))
                break
            
    return selected_playlists

    
def classifyMusicPlaylistsByTotalGenres(genre_list):
    abc = None
    
def classifyMusicPlaylistsByTop3Genre(genre_list):
    if not path.exists("playlists.json"):
        print("You need to have a playlists.json file! Run it again with the update json parameter.")
        return None
    
    selected_playlists = []
    
    with open("playlists.json", "r") as json_file:
        data = json.load(json_file)
        
    for playlist in data['playlists']:
        for genre in genre_list:
            if str(genre) in playlist['topGenres']:
                selected_playlists.append(str(playlist['id']))
                break
            
    return selected_playlists
    
def classifyMusicPlaylistsByGroupGenre(genre_list):
    abc = None
    
def classifyMusicPlaylistsByMetadadata(genre_list):
    abc = None
    
def main():
    chromedriver_autoinstaller.install()
    token = getSpotifyToken()
    if token != None:
        # print(token)
        name = getUserName(token)
        if name != None:
            getUserPlaylistsGenres(token, name)
        
        organizeLikedMusics(token)
    

if __name__ == "__main__":
    main()