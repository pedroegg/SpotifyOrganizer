from selenium import webdriver
from urllib.parse import urlparse
import time
import lib.spotify.spotifyUtils as lib
import model.metadata.metadata as meta
import os
import requests as req

def getSpotifyToken():
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

def getUserName(token):
    url = "https://api.spotify.com/v1/me"
    r = req.get(url=url, headers={'Authorization':'Bearer ' + token})
    data = r.json()
    r.close()

    if r.status_code != 200:
        print('An error ocurred trying to get the user info.\nError: {}'.format(data['error']))
        return None
    
    return str(data['display_name'])

def getTrackMetaData(token, track_id):
    url = "https://api.spotify.com/v1/audio-features/{}".format(str(track_id))
    r = req.get(url=url, headers={'Authorization':'Bearer ' + token})
    data = r.json()
    r.close()

    if r.status_code != 200:
        print('An error ocurred trying to get the metadata of a song.\nError: {}\nTrackID: {}' \
            .format(data['error'], track_id))
        return None

    return meta.Metadata().CreateMetadata(data)

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