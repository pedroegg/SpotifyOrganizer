from selenium import webdriver
from urllib.parse import urlparse
import time
import lib.spotify.spotifyUtils as lib
import model.metadata.metadata as meta
import model.spotify.spotify as model
import model.error.err as err
import os
import datetime
import requests as req
import progressbar

def getSpotifyToken() -> str:
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

def getUserName(token: str) -> tuple(str, err.Error):
    url = "https://api.spotify.com/v1/me"
    r = req.get(url=url, headers={'Authorization':'Bearer ' + token})
    data = r.json()
    r.close()

    if r.status_code != 200:
        error = err.Error('An error ocurred trying to get the user info.\nError: {}'.format(data['error']))
        return '', error
    
    return str(data['display_name']), None

def getTrackMetaData(token: str, track_id: str) -> tuple(meta.Metadata, err.Error):
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

def addMusicToPlaylists(token: str, track: model.Track, playlists: list) -> err.Error:
    # Reduzir o numero de requests para adicionar a playlist
    # Fazer adicionar varias musicas para a mesma playlist por vez
    # E nao em varias playlists cada musica
    # VERIFICAR E ARRUMAR DUPLICATA
    for playlist in playlists['playlists']:
        url = "https://api.spotify.com/v1/playlists/{}/tracks?uris={}".format(playlist['id'], track.uri)
        
        print("Music {} {} matched with {} {} in genre {}" \
                    .format(track.name, track.genres, playlist['name'], \
                        playlist['topGenres'], playlist['matchedGenre']), end='\n\n')
        
        r = req.post(url=url, headers={'Authorization':'Bearer ' + token})
        data = r.json()
        r.close()

        if r.status_code != 201:
            error = err.Error('An error ocurred trying to add one track in a playlist.\nError: {} \
                \nPlaylistID: {} \nMusic: {}'.format(data['error'], playlist['id'], track.name))
            
            return error
            
def getArtist(token: str, artistID: str) -> tuple(model.Artist, err.Error):
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

def getLikedMusicsByRangeURL(token: str, limitDate: datetime.date, url: str) -> tuple(list, str, err.Error):
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

def getLikedMusics(token: str, limitDate: datetime.date) -> tuple(list, err.Error):
    url = "https://api.spotify.com/v1/me/tracks?offset=0&limit=50"
    tracks = []
    
    segment_tracks, next_field, error = getLikedMusicsByRangeURL(token, limitDate, url)
    while error is None:
        tracks.extend(segment_tracks)
        
        if next_field is None:
            break
            
        segment_tracks, next_field, error = getLikedMusicsByRangeURL(token, limitDate, next_field)

    return tracks, error

def getUserPlaylistsByRangeURL(token: str, name: str, count: int, bar: progressbar.ProgressBar, url: str) -> tuple(list, int, str, err.Error):
    playlists = []
    
    r = req.get(url=url, headers={'Authorization':'Bearer ' + token})
    
    data = r.json()
    r.close()

    if r.status_code != 200:
        error = err.Error('An error ocurred trying to get the user playlists.\nError: {}\nURL: {}' \
            .format(data['error'], url))
        
        return playlists, None, count, error
    
    total = data['total']
    plus_percentage = total/100
    
    playlists_data = data['items']
    for playlist_data in playlists_data:
        if playlist_data['owner']['display_name'] == name:
            # sys.stderr.write("Playlist: {}".format(playlist['name']) + '\r')
            # sys.stderr.flush()
            # Fazer o print da playlist atual também
            playlist = model.Playlist()
            
            playlist.CreatePlaylistFromJSON(playlist_data)
            
            """
            genres, top3genres, metadatas = getPlaylistGenres(token, str(playlist['id']))
            dp_metadata = getMetadataDP(metadatas)
            playlists_data['playlists'].append({
                'name': str(playlist['name']),
                'id': str(playlist['id']),
                'genres': genres,
                'topGenres': top3genres,
                'metadata': dp_metadata
            })
            """
            
        count += plus_percentage
        try:
            bar.update(count)
        except ValueError:
            bar.update(100)
    
    return playlists, count, data['next'], None

def getUserPlaylists(token: str) -> list(model.Playlist):
    a = None