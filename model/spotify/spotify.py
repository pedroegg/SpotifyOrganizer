import model.metadata.metadata as meta
import service.spotify.spotify as service

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
                for genre in artist.genres:
                    if genre not in self.genres:
                        self.genres.append(genre)
        
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
        metadataList.CreateFromFileDataByRegister(data['metadata'])
        
        self.metadata = metadataList
        
    def CreateJSON(self) -> dict:
        playlist = {}
        playlist['name'] = self.name
        playlist['id'] = self.id
        playlist['genres'] = self.genres
        playlist['topGenres'] = self.topGenres
        playlist['metadata'] = self.metadata.CreateJSONByRegister()
        
        return playlist