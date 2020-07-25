import os
import json
import datetime
import requests as req
import model.error.err as err
import model.spotify.spotify as model
import service.spotify.spotify as service

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

def organizeLikedMusics(token: str, limitDate: datetime.date):
    print("Collecting recently saved musics and adding to playlists... Please, wait.")
    
    tracks, error = service.getLikedMusics(token, limitDate)
    if error is not None:
        return error
    
    for track in tracks:
        playlists, error = classifyMusicPlaylistsByTop3Genre(track.genres)
        if error is not None:
            continue
        
        service.addMusicToPlaylists(token, track, playlists)