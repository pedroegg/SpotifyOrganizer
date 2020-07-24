import os
import json
import datetime
import requests as req
import model.error.err as err
import model.spotify.spotify as model

def getTokenFromURL(url: str) -> str:
    return str(url).split('#')[1].split('&')[0].split('=')[1]

def getDataFromPlaylistsFile() -> tuple(dict, err.Error):
    if not os.path.exists("data/playlists.json"):
        return {}, err.Error("You need to have a playlists.json file! Run it again with the update json parameter.")
    
    with open("data/playlists.json", "r") as json_file:
        data = json.load(json_file)
    
    return data, None

def classifyMusicPlaylistsByGenre(genre_list: list) -> tuple(list, err.Error):
    selected_playlists = {}
    
    data, error = getDataFromPlaylistsFile()
    if error is not None:
        return selected_playlists, error
    
    selected_playlists['playlists'] = []
        
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
            
    return selected_playlists, None

def classifyMusicPlaylistsByTop3Genre(genre_list: list) -> tuple(dict, err.Error):
    selected_playlists = {}
    
    data, error = getDataFromPlaylistsFile()
    if error is not None:
        return selected_playlists, error
    
    selected_playlists['playlists'] = []
        
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
            
    return selected_playlists, None

def classifyMusicPlaylistsByMetadadata(genre_list: list) -> tuple(list, err.Error):
    abc = None
    
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