from typing import List
from typing import Tuple
import model.error.err as err
import model.metadata.metadata as meta
import service.spotify.spotify as service
import lib.metadata.metadataUtils as metaUtil
import random

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
        self.topAttributes = []
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
        
        relevantAttributes, err = self.FindRelevantAttributes()
        if err is not None:
            self.topAttributes = None
            return
        
        self.topAttributes = self.FindRangeOfTopAttributes(relevantAttributes)
        
    def CreatePlaylistFromFileData(self, data: dict) -> None:
        self.id = data['id']
        self.name = data['name']
        self.genres = data['genres']
        self.topGenres = data['topGenres']
        
        metadataList = meta.MetadataList()
        metadataList.CreateFromFileData(data['metadata'])
        
        self.metadata = metadataList

        relevantAttributes, err = self.FindRelevantAttributes()
        if err is not None:
            self.topAttributes = None
            return
        
        self.topAttributes = self.FindRangeOfTopAttributes(relevantAttributes)
        
    def CreateJSON(self) -> dict:
        playlist = {}
        playlist['name'] = self.name
        playlist['id'] = self.id
        playlist['genres'] = self.genres
        playlist['topGenres'] = self.topGenres
        playlist['metadata'] = self.metadata.CreateJSON()
        
        return playlist
    
    def FindRelevantAttributes(self) -> Tuple[List[str], err.Error]:
        topAttributes = {}
        
        attributesCount = {}
        
        if self.metadata.CheckEmpty():
            return topAttributes, err.Error('Null list')
        
        for column in self.metadata.fields[1:len(self.metadata.fields)-2]:
            columnValues, _ = self.metadata.GetColumnValues(column)
            
            attributesCount[column] = {}
            
            for value in list(columnValues):
                aux = float("{:.3f}".format(value))
                
                if aux in attributesCount[column]:
                    attributesCount[column][aux] += 1
                else:
                    attributesCount[column][aux] = 1
                    
        for column in attributesCount:
            count = self.getAttributeHigherCount(attributesCount, column)
            topAttributes[column] = count

        return sorted(topAttributes, key=topAttributes.get, reverse=True)[:3], None

    def FindRangeOfTopAttributes(self, topAttributesNames: List[str]) -> List[meta.AttributeRanges]:
        attributesRanges = []
        
        for attribute in topAttributesNames:
            values, _ = self.metadata.GetColumnValues(attribute)
            attributeDP = self.metadata.GetColumnDpUsingValues(values)
            
            random.shuffle(values)
            randomValues = values[:int(0.3 * len(values))]

            dpVariations = []

            for attributeValue in randomValues:
                dp = metaUtil.recalculateDP(values, attributeValue)
                varied = float("{:.4f}".format(abs(dp - attributeDP)))

                dpVariations.append(varied)

            highestDP = max(dpVariations)
            lowestDP = min(dpVariations)

            attributeRange = meta.AttributeRanges()
            interval = meta.Range()

            interval.init = lowestDP
            interval.final = highestDP

            attributeRange.name = attribute
            attributeRange.interval = interval

            attributesRanges.append(attributeRange)

        return attributesRanges

    def getAttributeHigherCount(self, attributesCount: dict, column: str) -> int:
        highest = 1
        for val in attributesCount[column]:
            tmp = int(attributesCount[column][val])
            
            if tmp > highest:
                highest = tmp
                
        return highest