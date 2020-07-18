# install python-pip (this is just to get pip install command working)
# pip install selenium
# pip install requests
# pip install chromedriver-autoinstaller
# pip install progressbar

import base64
import time
import datetime
import sys
import json
import csv
import progressbar
import statistics
import requests as req
import chromedriver_autoinstaller
from selenium import webdriver

today = datetime.date.today()

# Criar parametro para atualizar o json das playlists
updatePlaylistsJSON = bool(sys.argv[2])

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
# Fazer parametro para varredura de playlists com apenas playlists selecionadas. Poupar tempo e cust

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

def getUserPlaylistsGenres(token, name):
    playlists_data = {}
    playlists_data['playlists'] = []
    # Checar qual playlist falta verificar para fazer update das faltantes ou das musicas faltantes
    # Melhorar performance da funcao, pegando talvez menos musicas de cada playlist para tirar base?
    
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
    
def main():
    # chromedriver_autoinstaller.install()
    token = getSpotifyToken()
    if token != None:
        # print(token)
        name = getUserName(token)
        if name != None:
            getUserPlaylistsGenres(token, name)
        
        # generateCSV(token, '4Uz5RgDqU35EIbjykAhamm')
        # testAddMusics(token, '5I6Xwr1APbaJWJlaiWEbXS')
        # organizeLikedMusics(token)
    
if __name__ == "__main__":
    main()