from typing import List
from typing import Tuple
import model.error.err as err
import model.metadata.metadata as meta
import service.spotify.spotify as service

def insort_right(a: list, x: dict, lo=0, hi=None):
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
        if x['count'] < a[mid]['count']:
            hi = mid
        else:
            lo = mid+1
    a.insert(lo, x)

class Track():
    def __init__(self):
        self.id = str
        self.name = str
        self.uri = str
        self.artists = []
        self.genres = []
        self.metadata = meta.Metadata()
        
    def CreateTrack(self, token: str, data: dict) -> None:
        self.id = data['id']
        self.name = data['name']
        self.uri = data['uri']
        
        for artist_data in data['artists']:
            artist, error = service.getArtist(token, artist_data['id'])
            self.artists.append(artist)
            
            if error is None:
                self.genres.extend(x for x in artist.genres if x not in self.genres)
        
        self.metadata, _ = service.getTrackMetaData(token, self.id)
        
class Artist():
    def __init__(self):
        self.id = str
        self.name = str
        self.uri = str
        self.genres = []
        
    def CreateArtist(self, data: dict) -> None:
        self.id = data['id']
        self.name = data['name']
        self.uri = data['uri']
        self.genres = data['genres']
        
class Playlist():
    def __init__(self):
        self.name = str
        self.id = str
        self.genres = []
        self.topGenres = []
        self.metadata = meta.MetadataList()
        self.matchedGenre = str
        
    def CreatePlaylistFromJSON(self, token: str, data: dict) -> None:
        self.id = data['id']
        self.name = data['name']
        
        genres_count = {}
        
        for item in data['tracks']['items'][:50]:
            track = Track()
            track.CreateTrack(token, item['track'])
            
            if len(track.genres) > 0:
                for genre in track.genres:
                    if genre in genres_count:
                        genres_count[genre] += 1
                    else:
                        genres_count[genre] = 1
                    
                    if genre not in self.genres:
                        self.genres.append(genre)
            
            if (track.id is not None and track.id != "") and (track.metadata.id == track.id):
                self.metadata.Add(track.metadata)
        
        self.topGenres = sorted(genres_count, key=genres_count.get, reverse=True)[:3]
        
    def CreatePlaylistFromFileData(self, data: dict) -> None:
        self.id = data['id']
        self.name = data['name']
        self.genres = data['genres']
        self.topGenres = data['topGenres']
        
        metadataList = meta.MetadataList()
        metadataList.CreateFromFileData(data['metadata'])
        
        self.metadata = metadataList
        
    def CreateJSON(self) -> dict:
        playlist = {}
        playlist['name'] = self.name
        playlist['id'] = self.id
        playlist['genres'] = self.genres
        playlist['topGenres'] = self.topGenres
        playlist['metadata'] = self.metadata.CreateJSON()
        
        return playlist
    
    def FindRelevantAttributes(self) -> Tuple[List[str], err.Error]:
        topAttributes = []
        
        attributesCount = {}
        
        if self.metadata.CheckEmpty():
            return topAttributes, err.Error('Null list')
        
        for column in self.metadata.fields:
            columnValues, _ = self.metadata.GetColumnValues(column)
            
            attributesCount[column] = {}
            
            for value in list(columnValues):
                aux = float("{:.2f}".format(value))
                
                if aux in attributesCount[column]:
                    attributesCount[column][aux] += 1
                else:
                    attributesCount[column][aux] = 1
                    
        for column in self.metadata.fields:
            topValue = sorted(attributesCount[column], key=attributesCount[column].get, reverse=True)[:1]
            topCount = attributesCount[column][topValue]
            register = {'attribute': column,'value': topValue,'count': topCount}
            
            insort_right(topAttributes, register)

        return list({reg['attribute'] for reg in topAttributes}.values())[:3]
            