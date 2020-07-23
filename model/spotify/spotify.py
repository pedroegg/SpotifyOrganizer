import model.metadata.metadata as meta
import service.spotify.spotify as service

class Track():
    def __init__(self):
        self.id = str
        self.name = str
        self.uri = str
        self.artists = []
        self.genres = []
        self.metadata = meta.Metadata
        
    def CreateTrack(self, token:str, data: {}):
        self.id = data['id']
        self.name = data['name']
        self.uri = data['uri']
        
        for artist_data in data['artists']:
            artist, error = service.getArtist(token, artist_data['id'])
            self.artists.append(artist)
            
            if error is None:
                self.genres.extend(artist.genres)
        
        self.metadata, _ = service.getTrackMetaData(token, self.id)
        
class Artist():
    def __init__(self):
        self.id = str
        self.name = str
        self.uri = str
        self.genres = []
        
    def CreateArtist(self, data: {}):
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
        self.metadata = meta.MetadataList
        
    def CreatePlaylist(self, data: {}):
        a = None
        
    def CreateJSON(self):
        a = None