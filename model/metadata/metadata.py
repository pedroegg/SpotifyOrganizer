import model.error.err as err
from typing import Tuple
from typing import List
import statistics
import pandas as pd

class Metadata():
    def __init__(self):
        self.id = str
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

    def CreateMetadata(self, data: dict) -> None:
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
        
    def CreateJSON(self) -> dict:
        metadata = {}
        metadata['id'] = self.id
        metadata['danceability'] = self.danceability
        metadata['energy'] = self.energy
        metadata['loudness'] = self.loudness
        metadata['speechiness'] = self.speechiness
        metadata['acousticness'] = self.acousticness
        metadata['instrumentalness'] = self.instrumentalness
        metadata['liveness'] = self.liveness
        metadata['valence'] = self.valence
        metadata['tempo'] = self.tempo
        metadata['duration_ms'] = self.duration_ms
        
        return metadata

class MetadataList():
    """ Class to list metadata information in a Pandas DataFrame"""
    
    def __init__(self):
        self.fields = [
            'id',
            'danceability',
            'energy',
            'speechiness',
            'acousticness',
            'instrumentalness',
            'liveness',
            'loudness',
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
                meta.loudness,
                meta.valence,
                meta.tempo,
                meta.duration_ms
            ], index=self.fields)
        , ignore_index=True)

    def GetMetadataByIndex(self, index: int) -> Tuple[Metadata, err.Error]:
        if index < 0:
            return Metadata(), err.Error('Invalid index')

        if index >= len(list(self.metadataFrame.index)):
            return Metadata(), err.Error('Null list or length smaller than the index requested')

        row = self.metadataFrame.iloc[index]
        meta = Metadata()
        meta.CreateMetadata(dict(row))

        return meta, None
    
    def GetColumnValues(self, column: str) -> Tuple[list, err.Error]:
        if len(list(self.metadataFrame.index)) == 0:
            return None, err.Error('Null list')
        
        return self.metadataFrame[column].tolist()

    def GetByTrackID(self, track_id: int) -> Tuple[Metadata, err.Error]:
        indexes = self.metadataFrame.index[self.metadataFrame['id'] == track_id].tolist()

        if len(indexes) <= 0:
            return Metadata(), err.Error('Music metadata was not found')

        return self.GetMetadataByIndex(indexes[0])

    def Len(self) -> int:
        return len(list(self.metadataFrame.index))
    
    def CheckEmpty(self) -> bool:
        return self.Len() == 0

    def GetMean(self) -> Tuple[Metadata, err.Error]:
        if len(list(self.metadataFrame.index)) == 0:
            return None, err.Error('Null list')

        # Fazer sistema de rankeamento, pegar o TIPO da musica
        # Desvio Padrão
        
        # Da para fazer um loop entre os fields e para cada um fazer esse mesmo comando
        # E ai no final também é possível mandar os dados para a função metadata.CreateMetadata()
        metadata = Metadata()
        metadata.danceability = float("{:.3f}".format(statistics.fmean(self.GetColumnValues('danceability'))))
        metadata.energy = float("{:.3f}".format(statistics.fmean(self.GetColumnValues('energy'))))
        metadata.loudness = float("{:.3f}".format(statistics.fmean(self.GetColumnValues('loudness'))))
        metadata.speechiness = float("{:.3f}".format(statistics.fmean(self.GetColumnValues('speechiness'))))
        metadata.acousticness = float("{:.3f}".format(statistics.fmean(self.GetColumnValues('acousticness'))))
        metadata.instrumentalness = float("{:.3f}".format(statistics.fmean(self.GetColumnValues('instrumentalness'))))
        metadata.liveness = float("{:.3f}".format(statistics.fmean(self.GetColumnValues('liveness'))))
        metadata.valence = float("{:.3f}".format(statistics.fmean(self.GetColumnValues('valence'))))
        metadata.tempo = float("{:.3f}".format(statistics.fmean(self.GetColumnValues('tempo'))))
        metadata.duration_ms = float("{:.3f}".format(statistics.fmean(self.GetColumnValues('duration_ms'))))
        
        return metadata, None
    
    def getDP(self) -> Tuple[Metadata, err.Error]:
        if len(list(self.metadataFrame.index)) == 0:
            return None, err.Error('Null list')
        
        # Fazer sistema de rankeamento, pegar o TIPO da musica
        # Desvio Padrão
        
        metadata = Metadata()
        metadata.danceability = float("{:.3f}".format(statistics.pstdev(self.GetColumnValues('danceability'))))
        metadata.energy = float("{:.3f}".format(statistics.pstdev(self.GetColumnValues('energy'))))
        metadata.loudness = float("{:.3f}".format(statistics.pstdev(self.GetColumnValues('loudness'))))
        metadata.speechiness = float("{:.3f}".format(statistics.pstdev(self.GetColumnValues('speechiness'))))
        metadata.acousticness = float("{:.3f}".format(statistics.pstdev(self.GetColumnValues('acousticness'))))
        metadata.instrumentalness = float("{:.3f}".format(statistics.pstdev(self.GetColumnValues('instrumentalness'))))
        metadata.liveness = float("{:.3f}".format(statistics.pstdev(self.GetColumnValues('liveness'))))
        metadata.valence = float("{:.3f}".format(statistics.pstdev(self.GetColumnValues('valence'))))
        metadata.tempo = float("{:.3f}".format(statistics.pstdev(self.GetColumnValues('tempo'))))
        metadata.duration_ms = float("{:.3f}".format(statistics.pstdev(self.GetColumnValues('duration_ms'))))
        
        return metadata, None
    
    def GetColumnMean(self, column: str) -> Tuple[list, err.Error]:
        if len(list(self.metadataFrame.index)) == 0:
            return None, err.Error('Null list')
        
        return float("{:.3f}".format(statistics.fmean(self.GetColumnValues(column))))
    
    def GetColumnDP(self, column: str) -> Tuple[list, err.Error]:
        if len(list(self.metadataFrame.index)) == 0:
            return None, err.Error('Null list')
        
        return float("{:.3f}".format(statistics.pstdev(self.GetColumnValues(column))))
    
    def Sort(self, field: str) -> None:
        return list(self.metadataFrame[field].sort_values(ascending=True, kind='quicksort'))
    
    def CreateJSONByList(self) -> dict:
        metadata = {}
        
        if self.CheckEmpty():
            return metadata
        
        for column in self.fields[:1]:
            dp, _ = self.GetColumnDP(column)
            data, _ = self.GetColumnValues(column)
            metadata[column]['data'] = data
            metadata[column]['dp'] = dp
        
        return metadata
    
    def CreateJSONByRegister(self) -> dict:
        metadatas = []
        
        if self.CheckEmpty():
            return metadatas
        
        for ind in self.metadataFrame.index:
            metadata = {}
            
            for column in self.fields:
                metadata[column] = self.metadataFrame[column][ind]
                
            metadatas.append(metadata)
        
        return metadatas
    
    def CreateFromFileDataByList(self, data: dict) -> None:
        a = None
        return a
    
    def CreateFromFileDataByRegister(self, data: List[dict]) -> None:
        for meta_data in data:
            metadata = Metadata()
            metadata.CreateMetadata(meta_data)
            
            self.Add(metadata)