import os
import json
import datetime
from typing import Tuple
from typing import List
import model.error.err as err
import model.spotify.spotify as model
import model.metadata.metadata as metaModel
import lib.metadata.metadataUtils as metaUtil
import service.spotify.spotify as service

def getTokenFromURL(url: str) -> str:
    return str(url).split('#')[1].split('&')[0].split('=')[1]

def checkExistencePlaylistsFile() -> bool:
    if not os.path.exists("data/playlists.json"):
        return False
    return True

def getDataFromPlaylistsFile() -> Tuple[dict, err.Error]:
    if not os.path.exists("data/playlists.json"):
        return {}, err.Error("You need to have a playlists.json file! Run it again with the update json parameter.")
    
    with open("data/playlists.json", "r") as json_file:
        data = json.load(json_file)
    
    return data, None

def classifyMusicPlaylistsByGenre(genre_list: List[str]) -> Tuple[List[model.Playlist], err.Error]:
    selected_playlists = []
    
    data, error = getDataFromPlaylistsFile()
    if error is not None:
        return selected_playlists, error
        
    for playlist_data in data['playlists']:
        playlist = model.Playlist()
        playlist.CreatePlaylistFromFileData(playlist_data)
        for genre in playlist.genres:
            if genre in genre_list:
                selected_playlists.append(playlist)
                break
            
    return selected_playlists, None

def classifyMusicPlaylistsByTop3Genre(genre_list: List[str]) -> Tuple[List[model.Playlist], err.Error]:
    selected_playlists = []
    
    data, error = getDataFromPlaylistsFile()
    if error is not None:
        return selected_playlists, error
        
    for playlist_data in data['playlists']:
        playlist = model.Playlist()
        playlist.CreatePlaylistFromFileData(playlist_data)
        for top_genre in playlist.topGenres:
            if top_genre in genre_list:
                playlist.matchedGenre = top_genre
                selected_playlists.append(playlist)
                break
            
    return selected_playlists, None

def classifyMusicPlaylistsByMetadata(music_metadata: metaModel.Metadata) -> Tuple[List[model.Playlist], err.Error]:
    selected_playlists = []
    
    data, error = getDataFromPlaylistsFile()
    if error is not None:
        return selected_playlists, error
        
    for playlist_data in data['playlists']:
        playlist = model.Playlist()
        playlist.CreatePlaylistFromFileData(playlist_data)

        track_meta = music_metadata.CreateJSON()
        ok = True

        if playlist.metadata.CheckEmpty():
            continue

        for attribute in playlist.topAttributes:
            values, _ = playlist.metadata.GetColumnValues(attribute.name)
            attributeDP = playlist.metadata.GetColumnDpUsingValues(values)

            dp = metaUtil.recalculateDP(values, track_meta[attribute.name])
            varied = float("{:.4f}".format(abs(dp - attributeDP)))

            init = attribute.interval.init
            final = attribute.interval.final

            if not (init <= varied <= final):
                ok = False
                break

        if ok:
            selected_playlists.append(playlist)
            break
            
    return selected_playlists, None

def organizeLikedMusics(token: str, limitDate: datetime.date) -> err.Error:
    print("Collecting recently saved musics and adding to playlists... Please, wait.")
    
    tracks, error = service.getLikedMusics(token, limitDate)
    if error is not None:
        return error
    
    for track in tracks:
        playlists, error = classifyMusicPlaylistsByMetadata(track.metadata)
        if error is not None:
            continue
        
        service.addMusicToPlaylists(token, track, playlists, False, True)
        
def writePlaylistJSON(token: str) -> err.Error:
    print("Updating playlists.json file and analyzing your playlists genres... Please, wait.")
    
    playlists, error = service.getUserPlaylists(token)
    if error is not None:
        return error
    
    json_playlists = {}
    json_playlists['playlists'] = []
    
    for playlist in playlists:
        json_playlists['playlists'].append(playlist.CreateJSON())
    
    with open(file='data/playlists.json', mode='w', encoding='utf8') as json_file:
        json.dump(json_playlists, json_file, ensure_ascii=False, indent=4)