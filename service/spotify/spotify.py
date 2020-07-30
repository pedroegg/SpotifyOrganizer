from selenium import webdriver
from urllib.parse import urlparse
from typing import Tuple
from typing import List
import time
import lib.spotify.spotifyUtils as lib
import model.metadata.metadata as meta
import model.spotify.spotify as model
import model.error.err as err
import os
import datetime
import requests as req
import progressbar

def getToken() -> str:
    url = "https://accounts.spotify.com/authorize?client_id={}&response_type=token&redirect_uri={}" \
        "&scope=user-read-private playlist-read-private user-library-read " \
        "playlist-read-collaborative playlist-modify-public playlist-modify-private" \
        .format(os.getenv('CLIENT_ID'), 'https://www.google.com.br')
    
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--mute-audio")
    chrome_options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    
    while 'google' not in '{uri.scheme}://{uri.netloc}/'.format(uri=urlparse(driver.current_url)):
        # Do the login...
        time.sleep(2)
    
    # Tratar falha, deny do login
    
    token = lib.getTokenFromURL(driver.current_url)
    driver.close()
    return token

def getUserName(token: str) -> Tuple[str, err.Error]:
    url = "https://api.spotify.com/v1/me"
    r = req.get(url=url, headers={'Authorization':'Bearer ' + token})
    data = r.json()
    r.close()

    if r.status_code != 200:
        error = err.Error('An error ocurred trying to get the user info.\nError: {}'.format(data['error']))
        return '', error
    
    return str(data['display_name']), None

def getTrackMetaData(token: str, track_id: str) -> Tuple[meta.Metadata, err.Error]:
    url = "https://api.spotify.com/v1/audio-features/{}".format(str(track_id))
    r = req.get(url=url, headers={'Authorization':'Bearer ' + token})
    data = r.json()
    r.close()
    
    metadata = meta.Metadata()

    if r.status_code != 200:
        error = err.Error('An error ocurred trying to get the metadata of a song.\nError: {}\nTrackID: {}' \
            .format(data['error'], track_id))
            
        return metadata, error
    
    metadata.CreateMetadata(data)

    return metadata, None

def addMusicToPlaylists(token: str, track: model.Track, playlists: List[model.Playlist]) -> None:
    # Reduzir o numero de requests para adicionar a playlist
    # Fazer adicionar varias musicas para a mesma playlist por vez
    # E nao em varias playlists cada musica
    # VERIFICAR E ARRUMAR DUPLICATA
    for playlist in playlists:
        url = "https://api.spotify.com/v1/playlists/{}/tracks?uris={}".format(playlist.id, track.uri)
        
        print("Music {} {} matched with {} {} in genre {}" \
                    .format(track.name, track.genres, playlist.name, \
                        playlist.topGenres, playlist.matchedGenre), end='\n\n')
        
        r = req.post(url=url, headers={'Authorization':'Bearer ' + token})
        data = r.json()
        r.close()

        if r.status_code != 201:
            error = err.Error('An error ocurred trying to add one track in a playlist.\nError: {} \
                \nPlaylistID: {} \nMusic: {}'.format(data['error'], playlist.id, track.name))
            
            print(error.Message)
            
            
def getArtist(token: str, artistID: str) -> Tuple[model.Artist, err.Error]:
    url = "https://api.spotify.com/v1/artists/{}".format(artistID)
    r = req.get(url=url, headers={'Authorization':'Bearer ' + token})
    data = r.json()
    r.close()
    
    artist = model.Artist()
    
    if r.status_code != 200:
        error = err.Error('An error ocurred trying to get the Artist of a music.\nError: {}\nArtistID: {}' \
            .format(data['error'], artistID))
        
        return artist, error
    
    artist.CreateArtist(data)
    
    return artist, None

def getLikedMusicsByRangeURL(token: str, limitDate: datetime.date, url: str) -> Tuple[List[model.Track], str, err.Error]:
    tracks = []
    
    r = req.get(url=url, headers={'Authorization':'Bearer ' + token})
    data = r.json()
    r.close()
    
    # Handlear erro de instabilidade de servidor! Se não vai falhar a parada
    # Colocar um backoff para tentar 5 vezes? O objetivo desse handlear que disse é para não
    # Parar o select das musicas por causa de instabilidade de servidor
        
    if r.status_code != 200:
        error = err.Error('An error ocurred trying to get liked musics.\nError: {}\nURL: {}' \
            .format(data['error'], url))
        return tracks, None, error
    
    for items in data['items']:
        date_parts = str(items['added_at']).split('-')
        day = int(date_parts[2].split('T')[0])
        month = int(date_parts[1])
        year = int(date_parts[0])
        
        item_date = datetime.date(year, month, day)
        if item_date < limitDate:
            data['next'] = None
            break
        
        track = model.Track()
        track.CreateTrack(token, items['track'])
        
        tracks.append(track)
        
    return tracks, data['next'], None

def getLikedMusics(token: str, limitDate: datetime.date) -> Tuple[List[model.Track], err.Error]:
    url = "https://api.spotify.com/v1/me/tracks?offset=0&limit=50"
    tracks = []
    
    tracks_segment, next_field, error = getLikedMusicsByRangeURL(token, limitDate, url)
    while error is None:
        tracks.extend(tracks_segment)
        
        if next_field is None:
            break
            
        tracks_segment, next_field, error = getLikedMusicsByRangeURL(token, limitDate, next_field)

    return tracks, error

def getPlaylist(token: str, playlist_id: str) -> Tuple[model.Playlist, err.Error]:
    fields = "id,name,tracks(items(track(artists(id),id,name,uri)))"
    url = "https://api.spotify.com/v1/playlists/{}?fields={}".format(playlist_id, fields)
    
    r = req.get(url=url, headers={'Authorization':'Bearer ' + token})
    data = r.json()
    r.close()
    
    playlist = model.Playlist()
    
    if r.status_code != 200:
        error = err.Error('An error ocurred trying to get a playlist.\nError: {}\nPlaylistID: {}' \
            .format(data['error'], playlist_id))
        
        return playlist, error
    
    playlist.CreatePlaylistFromJSON(token, data)
    
    return playlist, None

def getUserPlaylistsByRangeURL(token: str, name: str, count: int, bar: progressbar.ProgressBar, url: str) -> Tuple[List[model.Playlist], int, str, err.Error]:
    playlists = []
    
    r = req.get(url=url, headers={'Authorization':'Bearer ' + token})
    
    data = r.json()
    r.close()

    if r.status_code != 200:
        error = err.Error('An error ocurred trying to get the user playlists.\nError: {}\nURL: {}' \
            .format(data['error'], url))
        
        return playlists, count, None, error
    
    total = data['total']
    plus_percentage = total/100
    
    for playlist_data in data['items']:
        if playlist_data['owner']['display_name'] == name:
            # sys.stderr.write("Playlist: {}".format(playlist['name']) + '\r')
            # sys.stderr.flush()
            # Fazer o print da playlist atual também
            playlist, error = getPlaylist(token, playlist_data['id'])
            if error is not None:
                continue
            
            playlists.append(playlist)
            
        count += plus_percentage
        try:
            bar.update(count)
        except ValueError:
            bar.update(100)
    
    return playlists, count, data['next'], None

def getUserPlaylists(token: str) -> Tuple[List[model.Playlist], err.Error]:
    playlists = []
    
    username, error = getUserName(token)
    if error is not None:
        return playlists, error
    
    url = "https://api.spotify.com/v1/me/playlists?limit=50&offset=0"
    
    bar = progressbar.ProgressBar(maxval=100, widgets=[progressbar.Bar('=', '[', ']'), ' ', \
        progressbar.Percentage()])
    bar.start()
    
    playlists_segment, count, next_field, error = getUserPlaylistsByRangeURL(token, \
        username, 0, bar, url)
    while error is None:
        playlists.extend(playlists_segment)
        
        if next_field is None:
            break
        
        playlists_segment, count, next_field, error = getUserPlaylistsByRangeURL(token, \
            username, count, bar, next_field)
    
    bar.finish()
    
    return playlists, error