import model.error.err as err
from typing import Tuple
from typing import List
import statistics
import pandas as pd

class AttributeRanges():
    def __init__(self):
        self.name = str
        self.interval = Range()

class Range():
    def __init__(self):
        self.init = float
        self.final = float

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
        if self.CheckEmpty():
            return None, err.Error('Null list')
        
        return self.metadataFrame[column].tolist(), None

    def GetByTrackID(self, track_id: int) -> Tuple[Metadata, err.Error]:
        indexes = self.metadataFrame.index[self.metadataFrame['id'] == track_id].tolist()

        if len(indexes) <= 0:
            return Metadata(), err.Error('Music metadata was not found')

        return self.GetMetadataByIndex(indexes[0]), None

    def Len(self) -> int:
        return len(list(self.metadataFrame.index))
    
    def CheckEmpty(self) -> bool:
        return self.Len() == 0

    def GetMean(self) -> Tuple[Metadata, err.Error]:
        if self.CheckEmpty():
            return None, err.Error('Null list')

        # Fazer sistema de rankeamento, pegar o TIPO da musica
        # Desvio Padrão
        
        # Da para fazer um loop entre os fields e para cada um fazer esse mesmo comando
        # E ai no final também é possível mandar os dados para a função metadata.CreateMetadata()
        danceabilityValues, _ = self.GetColumnValues('danceability')
        energyValues, _ = self.GetColumnValues('energy')
        loudnessValues, _ = self.GetColumnValues('loudness')
        speechinessValues, _ = self.GetColumnValues('speechiness')
        acousticnessValues, _ = self.GetColumnValues('acousticness')
        instrumentalnessValues, _ = self.GetColumnValues('instrumentalness')
        livenessValues, _ = self.GetColumnValues('liveness')
        valenceValues, _ = self.GetColumnValues('valence')
        tempoValues, _ = self.GetColumnValues('tempo')
        duration_msValues, _ = self.GetColumnValues('duration_ms')

        metadata = Metadata()
        metadata.danceability = float("{:.3f}".format(statistics.fmean(danceabilityValues)))
        metadata.energy = float("{:.3f}".format(statistics.fmean(energyValues)))
        metadata.loudness = float("{:.3f}".format(statistics.fmean(loudnessValues)))
        metadata.speechiness = float("{:.3f}".format(statistics.fmean(speechinessValues)))
        metadata.acousticness = float("{:.3f}".format(statistics.fmean(acousticnessValues)))
        metadata.instrumentalness = float("{:.3f}".format(statistics.fmean(instrumentalnessValues)))
        metadata.liveness = float("{:.3f}".format(statistics.fmean(livenessValues)))
        metadata.valence = float("{:.3f}".format(statistics.fmean(valenceValues)))
        metadata.tempo = float("{:.3f}".format(statistics.fmean(tempoValues)))
        metadata.duration_ms = float("{:.3f}".format(statistics.fmean(duration_msValues)))
        
        return metadata, None
    
    def getDP(self) -> Tuple[Metadata, err.Error]:
        if self.CheckEmpty():
            return None, err.Error('Null list')
        
        # Fazer sistema de rankeamento, pegar o TIPO da musica
        # Desvio Padrão

        danceabilityValues, _ = self.GetColumnValues('danceability')
        energyValues, _ = self.GetColumnValues('energy')
        loudnessValues, _ = self.GetColumnValues('loudness')
        speechinessValues, _ = self.GetColumnValues('speechiness')
        acousticnessValues, _ = self.GetColumnValues('acousticness')
        instrumentalnessValues, _ = self.GetColumnValues('instrumentalness')
        livenessValues, _ = self.GetColumnValues('liveness')
        valenceValues, _ = self.GetColumnValues('valence')
        tempoValues, _ = self.GetColumnValues('tempo')
        duration_msValues, _ = self.GetColumnValues('duration_ms')
        
        metadata = Metadata()
        metadata.danceability = float("{:.3f}".format(statistics.pstdev(danceabilityValues)))
        metadata.energy = float("{:.3f}".format(statistics.pstdev(energyValues)))
        metadata.loudness = float("{:.3f}".format(statistics.pstdev(loudnessValues)))
        metadata.speechiness = float("{:.3f}".format(statistics.pstdev(speechinessValues)))
        metadata.acousticness = float("{:.3f}".format(statistics.pstdev(acousticnessValues)))
        metadata.instrumentalness = float("{:.3f}".format(statistics.pstdev(instrumentalnessValues)))
        metadata.liveness = float("{:.3f}".format(statistics.pstdev(livenessValues)))
        metadata.valence = float("{:.3f}".format(statistics.pstdev(valenceValues)))
        metadata.tempo = float("{:.3f}".format(statistics.pstdev(tempoValues)))
        metadata.duration_ms = float("{:.3f}".format(statistics.pstdev(duration_msValues)))
        
        return metadata, None
    
    def GetColumnMean(self, column: str) -> Tuple[list, err.Error]:
        if self.CheckEmpty():
            return None, err.Error('Null list')

        values, _ = self.GetColumnValues(column)
        
        return float("{:.3f}".format(statistics.fmean(values))), None
    
    def GetColumnDP(self, column: str) -> Tuple[list, err.Error]:
        if self.CheckEmpty():
            return None, err.Error('Null list')

        values, _ = self.GetColumnValues(column)
        
        return float("{:.3f}".format(statistics.pstdev(values))), None

    def GetColumnMeanUsingValues(self, values: list) -> list:
        return float("{:.3f}".format(statistics.fmean(values)))
    
    def GetColumnDpUsingValues(self, values: list) -> list:
        return float("{:.3f}".format(statistics.pstdev(values)))
    
    def Sort(self, field: str) -> None:
        return list(self.metadataFrame[field].sort_values(ascending=True, kind='quicksort'))
    
    def CreateJSON(self) -> dict:
        metadatas = []
        
        if self.CheckEmpty():
            return metadatas
        
        for ind in self.metadataFrame.index:
            metadata = {}
            
            for column in self.fields:
                metadata[column] = self.metadataFrame[column][ind]
                
            metadatas.append(metadata)
        
        return metadatas
    
    def CreateFromFileData(self, data: List[dict]) -> None:
        for meta_data in data:
            metadata = Metadata()
            metadata.CreateMetadata(meta_data)
            
            self.Add(metadata)
