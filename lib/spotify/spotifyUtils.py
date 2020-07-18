import os
import json
import model.error.err as error

def getTokenFromURL(url: str) -> str:
    return str(url).split('#')[1].split('&')[0].split('=')[1]

def getDataFromPlaylistsFile() -> tuple({}, error.Error):
    if not os.path.exists("data/playlists.json"):
        return {}, error.Error("You need to have a playlists.json file! Run it again with the update json parameter.")
    
    with open("data/playlists.json", "r") as json_file:
        data = json.load(json_file)
    
    return data, None

def classifyMusicPlaylistsByGenre(genre_list: []) -> tuple([], error.Error):
    selected_playlists = {}
    
    data, err = getDataFromPlaylistsFile()
    if err != None:
        print(err.Message)
        return selected_playlists, err
    
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

def classifyMusicPlaylistsByTop3Genre(genre_list: []) -> tuple([], error.Error):
    selected_playlists = {}
    
    data, err = getDataFromPlaylistsFile()
    if err != None:
        print(err.Message)
        return selected_playlists, err
    
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

def classifyMusicPlaylistsByMetadadata(genre_list: []) -> tuple([], error.Error):
    abc = None