import model.error.err as err
import statistics
import pandas as pd

class Metadata():
    def __init__(self):
        self.id = int
        self.danceability = float
        self.energy = float
        self.loudness = float
        self.speechiness = float
        self.acousticness = float
        self.instrumentalness = float
        self.liveness = float
        self.valence = float
        self.tempo = float
        self.duration_ms = float

    def CreateMetadata(self, data: {}):
        self.id = data['id']
        self.danceability = float("{:.3f}".format(data['danceability']))
        self.energy = float("{:.3f}".format(data['energy']))
        self.loudness = float("{:.3f}".format(data['loudness']))
        self.speechiness = float("{:.3f}".format(data['speechiness']))
        self.acousticness = float("{:.3f}".format(data['acousticness']))
        self.instrumentalness = float("{:.3f}".format(data['instrumentalness']))
        self.liveness = float("{:.3f}".format(data['liveness']))
        self.valence = float("{:.3f}".format(data['valence']))
        self.tempo = float("{:.3f}".format(data['tempo']))
        self.duration_ms = float("{:.3f}".format(data['duration_ms']))
        
    def CreateJSON(self) -> {}:
        a = None
        
class MetadataList():
    """ Class to list metadata information in a Pandas DataFrame"""
    def __init__(self) -> None:
      self.fields= [
        'id',
        'danceability',
        'energy',
        'loudness',
        'speechiness',
        'acousticness'
        'instrumentalness',
        'liveness',
        'valence',
        'tempo',
        'duration_ms',
      ]

    self.metadataFrame = pd.DataFrame(columns=self.fields)

        
    def Add(self, meta: Metadata) -> None:
        self.metadataFrame = self.metadataFrame.append(
            pd.Series([
                meta.id,
                meta.danceability,
                meta.energy,
                meta.speechiness,
                meta.acousticness,
                meta.instrumentalness,
                meta.liveness,
                meta.valence,
                meta.tempo,
                meta.duration_ms
            ], index=self.fields)
        )
        
    def Get(self, index: int) -> tuple(Metadata, err.Error):
        if index < 0:
            return Metadata(), err.Error('Invalid index')
        
        if index >= len(list(self.metadataFrame.index)):
            return Metadata(), err.Error('Null list or length smaller than the index requested')
        
        row = self.metadataFrame.iloc[index]
        meta = Metadata.CreateMetadata(dict(row))
        
        return meta, None
    
    def GetByMusicID(self, id: int) -> tuple(Metadata, err.Error):
        indexes = self.metadataFrame.index[self.metadataFrame['id'] == id].tolist()

        if len(indexes) <= 0:
            return Metadata(), err.Error('Music metadata was not found')
            
        return self.Get(indexes[0])
        
    def Len(self) -> int:
        return len(list(self.metadataFrame.index))
    
    def GetMedia(self) -> tuple(Metadata, err.Error):
        if len(list(self.metadataFrame.index)) == 0:
            return None, err.Error('Null list')
        
        # Fazer sistema de rankeamento, pegar o TIPO da musica
        # Desvio Padrão
        metadata = Metadata()
        metadata.danceability = float("{:.3f}".format(statistics.fmean(self.metadataFrame['danceability'].tolist())))
        metadata.energy = float("{:.3f}".format(statistics.fmean(self.metadataFrame['energy'].tolist())))
        metadata.loudness = float("{:.3f}".format(statistics.fmean(self.metadataFrame['loudness'].tolist())))
        metadata.speechiness = float("{:.3f}".format(statistics.fmean(self.metadataFrame['speechiness'].tolist())))
        metadata.acousticness = float("{:.3f}".format(statistics.fmean(self.metadataFrame['acousticness'].tolist())))
        metadata.instrumentalness = float("{:.3f}".format(statistics.fmean(self.metadataFrame['instrumentalness'].tolist())))
        metadata.liveness = float("{:.3f}".format(statistics.fmean(self.metadataFrame['liveness'].tolist())))
        metadata.valence = float("{:.3f}".format(statistics.fmean(self.metadataFrame['valence'].tolist())))
        metadata.tempo = float("{:.3f}".format(statistics.fmean(self.metadataFrame['tempo'].tolist())))
        metadata.duration_ms = float("{:.3f}".format(statistics.fmean(self.metadataFrame['duration_ms'].tolist())))
        
        return metadata, None
    
    def getDP(self) -> tuple(Metadata, err.Error):
        if len(list(self.metadataFrame.index)) == 0:
            return None, err.Error('Null list')
        
        # Fazer sistema de rankeamento, pegar o TIPO da musica
        # Desvio Padrão
        
        metadata = Metadata()
        metadata.danceability = float("{:.3f}".format(statistics.pstdev(self.metadataFrame['danceability'].tolist())))
        metadata.energy = float("{:.3f}".format(statistics.pstdev(self.metadataFrame['energy'].tolist())))
        metadata.loudness = float("{:.3f}".format(statistics.pstdev(self.metadataFrame['loudness'].tolist())))
        metadata.speechiness = float("{:.3f}".format(statistics.pstdev(self.metadataFrame['speechiness'].tolist())))
        metadata.acousticness = float("{:.3f}".format(statistics.pstdev(self.metadataFrame['acousticness'].tolist())))
        metadata.instrumentalness = float("{:.3f}".format(statistics.pstdev(self.metadataFrame['instrumentalness'].tolist())))
        metadata.liveness = float("{:.3f}".format(statistics.pstdev(self.metadataFrame['liveness'].tolist())))
        metadata.valence = float("{:.3f}".format(statistics.pstdev(self.metadataFrame['valence'].tolist())))
        metadata.tempo = float("{:.3f}".format(statistics.pstdev(self.metadataFrame['tempo'].tolist())))
        metadata.duration_ms = float("{:.3f}".format(statistics.pstdev(self.metadataFrame['duration_ms'].tolist())))
        
        return metadata, None
    
    def Sort(self, field) -> None:
        return list(self.metadataFrame[field].sort_values(ascending=True, kind='quicksort'))
