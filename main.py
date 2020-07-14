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
from os import path
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
    
def classifyMusicPlaylistsByMetadadata(genre_list):
    abc = None

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
            
def testAddMusics(token, playlistID):
    test_musics = []
    test_musics.append({"musicID": "4QfMUPyVRurqeIH1k4a9Ky", "include": False})
    test_musics.append({"musicID": "5UFXAE1QXIGnmALcrQ4DgZ", "include": False})
    test_musics.append({"musicID": "2gMQHahD4hFjnEYjTTyivU", "include": False})
    test_musics.append({"musicID": "3QOruXa2lvqIFvOOa2rYyJ", "include": False})
    test_musics.append({"musicID": "3WHGMx4tWMsJdhHEVmG4ox", "include": False})
    test_musics.append({"musicID": "2ywk9oDKsNUZ7YXxed4AnA", "include": False})
    test_musics.append({"musicID": "1TFjgmDNqtfw2R0ruYZkUI", "include": False})
    test_musics.append({"musicID": "5dvHlfjmu4AaxlTbUYQabN", "include": False})
    test_musics.append({"musicID": "2h96laC0Hjwx49xROS1rYz", "include": False})
    test_musics.append({"musicID": "0ecM7uGyjgJnBliXS2fPP9", "include": False})
    test_musics.append({"musicID": "2aTfkAV3oxoBF5FJvUY4ja", "include": False})
    test_musics.append({"musicID": "3Rl26h1HiMCV0HFHHVb2IM", "include": False})
    
    test_musics.append({"musicID": "0ZALvx5UEaw0lMUexypBI8", "include": True})
    test_musics.append({"musicID": "6WeNs3jrqfw624KlcNYect", "include": True})
    test_musics.append({"musicID": "5413LFXLYAJS85VKs6H6ag", "include": True})
    test_musics.append({"musicID": "2N39ObBUyuEdT2dMvKRTBz", "include": True})
    test_musics.append({"musicID": "01TyFEZu6mHbffsVfxgrFn", "include": True})
    test_musics.append({"musicID": "6Ijmj8Z0L31hCp5pLZnT5U", "include": True})
    test_musics.append({"musicID": "5cW8mZYs5mKGZP5n2azBW3", "include": True})
    test_musics.append({"musicID": "7l8UyITgVXQyadELQgToFP", "include": True})
    test_musics.append({"musicID": "1eoGO19WEflJbAV8BLebhr", "include": True})
    test_musics.append({"musicID": "0ROCe58wXm7sBUPkZaRrnY", "include": True})
    test_musics.append({"musicID": "0qlwDRhrYcE5JC07JbXTer", "include": True})
    test_musics.append({"musicID": "35QAUfIbfIXT3p3cWhaKxZ", "include": True})
    
    with open("playlists.json", "r") as json_file:
        data = json.load(json_file)
        
    for playlist in data['playlists']:
        if playlist['id'] == playlistID:
            for x in range(0, len(test_musics), 1):
                print("Testing Music[{}]. Novos DP's:".format(x))
                meta = getTrackMetaData(token, test_musics[x]['musicID'])
                dp = {}
                dp['danceability'] = recalculateDP(playlist['metadata']['danceability']['data'], meta['danceability'])
                dp['energy'] = recalculateDP(playlist['metadata']['energy']['data'], meta['energy'])
                dp['loudness'] = recalculateDP(playlist['metadata']['loudness']['data'], meta['loudness'])
                dp['mode'] = recalculateDP(playlist['metadata']['mode']['data'], meta['mode'])
                dp['speechiness'] = recalculateDP(playlist['metadata']['speechiness']['data'], meta['speechiness'])
                dp['acousticness'] = recalculateDP(playlist['metadata']['acousticness']['data'], meta['acousticness'])
                dp['instrumentalness'] = recalculateDP(playlist['metadata']['instrumentalness']['data'], meta['instrumentalness'])
                dp['liveness'] = recalculateDP(playlist['metadata']['liveness']['data'], meta['liveness'])
                dp['valence'] = recalculateDP(playlist['metadata']['valence']['data'], meta['valence'])
                dp['tempo'] = recalculateDP(playlist['metadata']['tempo']['data'], meta['tempo'])
                dp['duration_ms'] = recalculateDP(playlist['metadata']['duration_ms']['data'], meta['duration_ms'])
                print('danceability: {} --> variou {}'.format(dp['danceability'], float("{:.4f}".format(abs(dp['danceability'] - playlist['metadata']['danceability']['dp'])))))
                print('energy: {} --> variou {}'.format(dp['energy'], float("{:.4f}".format(abs(dp['energy'] - playlist['metadata']['energy']['dp'])))))
                print('loudness: {} --> variou {}'.format(dp['loudness'], float("{:.4f}".format(abs(dp['loudness'] - playlist['metadata']['loudness']['dp'])))))
                print('mode: {} --> variou {}'.format(dp['mode'], float("{:.4f}".format(abs(dp['mode'] - playlist['metadata']['mode']['dp'])))))
                print('speechiness: {} --> variou {}'.format(dp['speechiness'], float("{:.4f}".format(abs(dp['speechiness'] - playlist['metadata']['speechiness']['dp'])))))
                print('acousticness: {} --> variou {}'.format(dp['acousticness'], float("{:.4f}".format(abs(dp['acousticness'] - playlist['metadata']['acousticness']['dp'])))))
                print('instrumentalness: {} --> variou {}'.format(dp['instrumentalness'], float("{:.4f}".format(abs(dp['instrumentalness'] - playlist['metadata']['instrumentalness']['dp'])))))
                print('liveness: {} --> variou {}'.format(dp['liveness'], float("{:.4f}".format(abs(dp['liveness'] - playlist['metadata']['liveness']['dp'])))))
                print('valence: {} --> variou {}'.format(dp['valence'], float("{:.4f}".format(abs(dp['valence'] - playlist['metadata']['valence']['dp'])))))
                print('tempo: {} --> variou {}'.format(dp['tempo'], float("{:.4f}".format(abs(dp['tempo'] - playlist['metadata']['tempo']['dp'])))))
                print('duration_ms: {} --> variou {}'.format(dp['duration_ms'], float("{:.4f}".format(abs(dp['duration_ms'] - playlist['metadata']['duration_ms']['dp'])))))
                print('ERA PARA ADICIONAR? {}\n'.format(test_musics[x]['include']))


def recalculateDP(array, value):
    arr = array.copy()
    arr.append(value)
    return float("{:.3f}".format(statistics.pstdev(arr)))

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