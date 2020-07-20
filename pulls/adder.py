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
import csv
import progressbar
import statistics
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
import bisect

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
                
            playlists = classifyMusicPlaylistsByTop3Genre(music_genres)
            if playlists is None:
                return None
            
            addMusicToPlaylists(token, music['track'], music_genres, playlists)
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
                genres, top3genres, metadatas = getPlaylistGenres(token, str(playlist['id']))
                dp_metadata = getMetadataDP(metadatas)
                playlists_data['playlists'].append({
                    'name': str(playlist['name']),
                    'id': str(playlist['id']),
                    'genres': genres,
                    'topGenres': top3genres,
                    'metadata': dp_metadata
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
    url = "https://api.spotify.com/v1/playlists/{}/tracks?fields=items(track(id,artists(id)))&limit=50" \
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
    metadatas = createMetadataDPStructure()
    
    for track in data['items']:
        if track['track']['id'] is not None and str(track['track']['id']) != "":
            current_metadata = getTrackMetaData(token, track['track']['id'])
            metadatas = mapMetadataDPValues(metadatas, current_metadata)
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
    return genres, top_genres, metadatas

def addMusicToPlaylists(token, music, music_genres, playlists):
    # Reduzir o numero de requests para adicionar a playlist
    # Fazer adicionar varias musicas para a mesma playlist por vez
    # E nao em varias playlists cada musica
    # VERIFICAR E ARRUMAR DUPLICATA
    for playlist in playlists['playlists']:
        url = "https://api.spotify.com/v1/playlists/{}/tracks?uris={}".format(playlist['id'], music['uri'])
        
        print("Music {} {} matched with {} {} in genre {}" \
                    .format(music['name'], music_genres, playlist['name'], \
                        playlist['topGenres'], playlist['matchedGenre']), end='\n\n')
        
        r = req.post(url=url, headers={'Authorization':'Bearer ' + token})
        data = r.json()
        r.close()

        if r.status_code != 201:
            print('An error ocurred trying to add one track in a playlist.\nError: {}\nPlaylistID: {}' \
                "\nMusic: {}".format(data['error'], playlist['id'], music['name']))
    

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
    
    selected_playlists = {}
    selected_playlists['playlists'] = []
    
    with open("playlists.json", "r") as json_file:
        data = json.load(json_file)
        
    for playlist in data['playlists']:
        for top_genre in playlist['topGenres']:
            if str(top_genre) in genre_list:
                selected_playlists['playlists'].append({
                    'id': playlist['id'],
                    'name': playlist['name'],
                    'genres': playlist['genres'],
                    'matchedGenre': str(top_genre)
                })
                break
            
    return selected_playlists

    
def classifyMusicPlaylistsByTotalGenres(genre_list):
    abc = None
    
def classifyMusicPlaylistsByTop3Genre(genre_list):
    if not path.exists("playlists.json"):
        print("You need to have a playlists.json file! Run it again with the update json parameter.")
        return None
    
    selected_playlists = {}
    selected_playlists['playlists'] = []
    
    with open("playlists.json", "r") as json_file:
        data = json.load(json_file)
        
    for playlist in data['playlists']:  
        for top_genre in playlist['topGenres']:
            if str(top_genre) in genre_list:
                selected_playlists['playlists'].append({
                    'id': playlist['id'],
                    'name': playlist['name'],
                    'topGenres': playlist['topGenres'],
                    'matchedGenre': str(top_genre)
                })
                break
            
    return selected_playlists
    
def classifyMusicPlaylistsByGroupGenre(genre_list):
    abc = None
    
def classifyMusicPlaylistsByMetadadata(genre_list):
    abc = None
    
def getTrackMetaData(token, track_id):
    url = "https://api.spotify.com/v1/audio-features/{}".format(str(track_id))
    r = req.get(url=url, headers={'Authorization':'Bearer ' + token})
    data = r.json()
    r.close()

    if r.status_code != 200:
        print('An error ocurred trying to get the metadata of a song.\nError: {}\nTrackID: {}' \
            .format(data['error'], track_id))
        return None
    
    data['danceability'] = float("{:.3f}".format(data['danceability']))
    data['energy'] = float("{:.3f}".format(data['energy']))
    data['loudness'] = float("{:.3f}".format(data['loudness']))
    data['speechiness'] = float("{:.3f}".format(data['speechiness']))
    data['acousticness'] = float("{:.3f}".format(data['acousticness']))
    data['instrumentalness'] = float("{:.3f}".format(data['instrumentalness']))
    data['liveness'] = float("{:.3f}".format(data['liveness']))
    data['valence'] = float("{:.3f}".format(data['valence']))
    data['tempo'] = float("{:.3f}".format(data['tempo']))
    data['duration_ms'] = float("{:.3f}".format(data['duration_ms']))
    
    return data

def getMetadataMedia(metadatas):
    if metadatas['danceability'] is None or len(metadatas['danceability']) == 0:
        return metadatas
    
    # Fazer sistema de rankeamento, pegar o TIPO da musica
    # Desvio Padrão
    
    metadata = {}
    metadata['danceability'] = "{:.3f}".format(statistics.fmean(metadatas['danceability']))
    metadata['energy'] = "{:.3f}".format(statistics.fmean(metadatas['energy']))
    metadata['loudness'] = "{:.3f}".format(statistics.fmean(metadatas['loudness']))
    metadata['mode'] = statistics.mode(metadatas['mode'])
    metadata['speechiness'] = "{:.3f}".format(statistics.fmean(metadatas['speechiness']))
    metadata['acousticness'] = "{:.3f}".format(statistics.fmean(metadatas['acousticness']))
    metadata['instrumentalness'] = "{:.3f}".format(statistics.fmean(metadatas['instrumentalness']))
    metadata['liveness'] = "{:.3f}".format(statistics.fmean(metadatas['liveness']))
    metadata['valence'] = "{:.3f}".format(statistics.fmean(metadatas['valence']))
    metadata['tempo'] = "{:.3f}".format(statistics.fmean(metadatas['tempo']))
    metadata['duration_ms'] = "{:.3f}".format(statistics.fmean(metadatas['duration_ms']))
    return metadata


def getMetadataDP(metadatas):
    if metadatas['danceability'] is None or len(metadatas['danceability']) == 0:
        return metadatas
    
    # Fazer sistema de rankeamento, pegar o TIPO da musica
    # Desvio Padrão
    
    metadatas['danceability']['dp'] = "{:.3f}".format(statistics.pstdev(metadatas['danceability']['data']))
    metadatas['energy']['dp'] = "{:.3f}".format(statistics.pstdev(metadatas['energy']['data']))
    metadatas['loudness']['dp'] = "{:.3f}".format(statistics.pstdev(metadatas['loudness']['data']))
    metadatas['mode']['dp'] = statistics.pstdev(metadatas['mode']['data'])
    metadatas['speechiness']['dp'] = "{:.3f}".format(statistics.pstdev(metadatas['speechiness']['data']))
    metadatas['acousticness']['dp'] = "{:.3f}".format(statistics.pstdev(metadatas['acousticness']['data']))
    metadatas['instrumentalness']['dp'] = "{:.3f}".format(statistics.pstdev(metadatas['instrumentalness']['data']))
    metadatas['liveness']['dp'] = "{:.3f}".format(statistics.pstdev(metadatas['liveness']['data']))
    metadatas['valence']['dp'] = "{:.3f}".format(statistics.pstdev(metadatas['valence']['data']))
    metadatas['tempo']['dp'] = "{:.3f}".format(statistics.pstdev(metadatas['tempo']['data']))
    metadatas['duration_ms']['dp'] = "{:.3f}".format(statistics.pstdev(metadatas['duration_ms']['data']))
    return metadatas

def createMetadataStructure():
    metadatas = {}
    metadatas['danceability'] = []
    metadatas['energy'] = []
    metadatas['loudness'] = []
    metadatas['mode'] = []
    metadatas['speechiness'] = []
    metadatas['acousticness'] = []
    metadatas['instrumentalness'] = []
    metadatas['liveness'] = []
    metadatas['valence'] = []
    metadatas['tempo'] = []
    metadatas['duration_ms'] = []
    return metadatas

def createMetadataDPStructure():
    metadatas = {}
    metadatas['danceability'] = {}
    metadatas['danceability']['data'] = []
    metadatas['danceability']['dp'] = 0
    
    metadatas['energy'] = {}
    metadatas['energy']['data'] = []
    metadatas['energy']['dp'] = 0
    
    metadatas['loudness'] = {}
    metadatas['loudness']['data'] = []
    metadatas['loudness']['dp'] = 0
    
    metadatas['mode'] = {}
    metadatas['mode']['data'] = []
    metadatas['mode']['dp'] = 0
    
    metadatas['speechiness'] = {}
    metadatas['speechiness']['data'] = []
    metadatas['speechiness']['dp'] = 0
    
    metadatas['acousticness'] = {}
    metadatas['acousticness']['data'] = []
    metadatas['acousticness']['dp'] = 0

    metadatas['instrumentalness'] = {}
    metadatas['instrumentalness']['data'] = []
    metadatas['instrumentalness']['dp'] = 0
    
    metadatas['liveness'] = {}
    metadatas['liveness']['data'] = []
    metadatas['liveness']['dp'] = 0
    
    metadatas['valence'] = {}
    metadatas['valence']['data'] = []
    metadatas['valence']['dp'] = 0
    
    metadatas['tempo'] = {}
    metadatas['tempo']['data'] = []
    metadatas['tempo']['dp'] = 0

    metadatas['duration_ms'] = {}
    metadatas['duration_ms']['data'] = []
    metadatas['duration_ms']['dp'] = 0
    
    return metadatas

def mapMetadataValues(metadatas, current_metadata):
    metadatas['danceability'].append(current_metadata['danceability'])
    metadatas['energy'].append(current_metadata['energy'])
    metadatas['loudness'].append(current_metadata['loudness'])
    metadatas['mode'].append(current_metadata['mode'])
    metadatas['speechiness'].append(current_metadata['speechiness'])
    metadatas['acousticness'].append(current_metadata['acousticness'])
    metadatas['instrumentalness'].append(current_metadata['instrumentalness'])
    metadatas['liveness'].append(current_metadata['liveness'])
    metadatas['valence'].append(current_metadata['valence'])
    metadatas['tempo'].append(current_metadata['tempo'])
    metadatas['duration_ms'].append(current_metadata['duration_ms'])
    return metadatas

def mapMetadataDPValues(metadatas, current_metadata):
    insort(metadatas['danceability']['data'], current_metadata['danceability'])
    insort(metadatas['energy']['data'], current_metadata['energy'])
    insort(metadatas['loudness']['data'], current_metadata['loudness'])
    insort(metadatas['mode']['data'], current_metadata['mode'])
    insort(metadatas['speechiness']['data'], current_metadata['speechiness'])
    insort(metadatas['acousticness']['data'], current_metadata['acousticness'])
    insort(metadatas['instrumentalness']['data'], current_metadata['instrumentalness'])
    insort(metadatas['liveness']['data'], current_metadata['liveness'])
    insort(metadatas['valence']['data'], current_metadata['valence'])
    insort(metadatas['tempo']['data'], current_metadata['tempo'])
    insort(metadatas['duration_ms']['data'], current_metadata['duration_ms'])
    return metadatas

def generateCSV(token, playlistId):
    url = "https://api.spotify.com/v1/playlists/{}/tracks?fields=items(track(id,artists(id)))&limit=50" \
        .format(playlistId)
    r = req.get(url=url, headers={'Authorization':'Bearer ' + token})
    
    data = r.json()
    r.close()

    if r.status_code != 200:
        print('An error ocurred trying to get tracks of one playlist.\nError: {}\nPlaylistID: {}' \
            .format(data['error'], playlistId))
        return ''
    
    structure = {}
    structure['metadata'] = {}
    structure['genres'] = []
    
    for track in data['items']:
        if track['track']['id'] is not None and str(track['track']['id']) != "":
            current_metadata = getTrackMetaData(token, track['track']['id'])
            structure['metadata'] = current_metadata
            for artist in track['track']['artists']:
                if (artist['id'] is not None):
                    genres_artist = getArtistGenres(token, artist['id'])
                    for genre in genres_artist:
                        if (genre is not None):
                            if str(genre) not in structure['genres']:
                                structure['genres'].append(str(genre))
            print(structure)
            structure['metadata'] = {}
            structure['genres'] = []

"""
* @function: findRelevantAttributes
* @param: playlistID
* @return: Top 3 

Metodo para definir o top 3 atributos mais importantes seguindo fluxo

"""
"""
def findRelevantAttributes( playlistID ):

    tops = []

    with open("playlists.json", "r") as json_file:
        data = json.load(json_file)

    lengthDanceability = 0
    metadatas['danceability'] = []
    metadatas['energy'] = []
    metadatas['loudness'] = []
    metadatas['speechiness'] = []
    metadatas['acousticness'] = []
    metadatas['instrumentalness'] = []
    metadatas['liveness'] = []
    metadatas['valence'] = []
    metadatas['tempo'] = []

    for playlist in data['playlists']:
        if playlist['id'] == playlistID:
            for danceability_datas in playlist['metadata']['danceability']['data']:

                # Conta quando x valor repete pela playlist, cada vez diminuindo sua magnitude/precisao
                metadatas['danceability'].append( playlist['metadata']['danceability']['data'].count( "{:.3f}".format(  ) ) ) # Musicas com praticamente mesmo atributo
                metadatas['danceability'].append( playlist['metadata']['danceability']['data'].count( "{:.2f}".format(  ) ) ) # Musicas com atributo com variacao aceitavel
                metadatas['danceability'].append( playlist['metadata']['danceability']['data'].count( "{:.1f}".format(  ) ) ) # Musicas com atributo pouco parecido


    return tops
"""

"""
Metodo para inserir de forma organizada em estrutura
Metodo usado em mapMetadataValues(metadatas, current_metadata)

"""

def insort(a, x, lo=0, hi=None):
    """Insert item x in list a, and keep it sorted assuming a is sorted.
    If x is already in a, insert it to the right of the rightmost x.
    Optional args lo (default 0) and hi (default len(a)) bound the
    slice of a to be searched.
    """

    if lo < 0:
        raise ValueError('lo must be non-negative')
    if hi is None:
        hi = len(a)
    while lo < hi:
        mid = (lo+hi)//2
        if x < a[mid]:
            hi = mid
        else:
            lo = mid+1
    a.insert(lo, x)

def main():
    chromedriver_autoinstaller.install()
    token = getSpotifyToken()
    if token != None:
        # print(token)
        name = getUserName(token)
        if name != None:
            getUserPlaylistsGenres(token, name)
            # generateCSV(token, '4Uz5RgDqU35EIbjykAhamm')
            mapMetadataDPValues(token, name)   
        # organizeLikedMusics(token)


     
    
if __name__ == "__main__":
    main()