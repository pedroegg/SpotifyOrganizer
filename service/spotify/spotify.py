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

    if r.status_code != 200:
        error = err.Error('An error ocurred trying to get the metadata of a song.\nError: {}\nTrackID: {}' \
            .format(data['error'], track_id))
            
        return meta.Metadata(), error
    
    metadata = meta.Metadata()
    metadata.CreateMetadata(data)

    return metadata, None

def addMusicToPlaylists(token: str, music: dict, music_genres: list, playlists: list) -> err.Error:
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
            error = err.Error('An error ocurred trying to add one track in a playlist.\nError: {} \
                \nPlaylistID: {} \nMusic: {}'.format(data['error'], playlist['id'], music['name']))
            
            return error
            
def getArtist(token: str, artistID: str) -> tuple(model.Artist, err.Error):
    url = "https://api.spotify.com/v1/artists/{}".format(artistID)
    r = req.get(url=url, headers={'Authorization':'Bearer ' + token})
    data = r.json()
    r.close()
    
    if r.status_code != 200:
        error = err.Error('An error ocurred trying to get the Artist of a music.\nError: {}\nArtistID: {}' \
            .format(data['error'], artistID))
        
        return model.Artist(), error
    
    artist = model.Artist()
    artist.CreateArtist(data)
    
    return artist, None

def getLikedMusics(token: str, limitDate: datetime.date) -> tuple(list, err.Error):
    url = "https://api.spotify.com/v1/me/tracks?offset=0&limit=50"
    tracks = []
    
    segment_tracks, next_field, error = lib.getLikedMusicsByRangeURL(token, limitDate, url)
    while error is None:
        tracks.extend(segment_tracks)
        
        if next_field is None:
            break
            
        segment_tracks, next_field, error = lib.getLikedMusicsByRangeURL(token, limitDate, next_field)

    return tracks, error