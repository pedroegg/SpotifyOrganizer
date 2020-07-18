import model.error.err as err
import statistics

class Metadata():
    def __init__(self):
        self.music_id = int
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
        self.music_id = data['id']
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
    def __init__(self) -> None:
        self.music_id_list = []
        self.danceability_list = []
        self.energy_list = []
        self.loudness_list = []
        self.speechiness_list = []
        self.acousticness_list = []
        self.instrumentalness_list = []
        self.liveness_list = []
        self.valence_list = []
        self.tempo_list = []
        self.duration_ms_list = []
        
    def Add(self, meta: Metadata) -> None:
        self.music_id_list.append(meta.music_id)
        self.danceability_list.append(meta.danceability)
        self.energy_list.append(meta.energy)
        self.loudness_list.append(meta.loudness)
        self.speechiness_list.append(meta.speechiness)
        self.acousticness_list.append(meta.acousticness)
        self.instrumentalness_list.append(meta.instrumentalness)
        self.liveness_list.append(meta.liveness)
        self.valence_list.append(meta.valence)
        self.tempo_list.append(meta.tempo)
        self.duration_ms_list.append(meta.duration_ms)
        
    def Get(self, index: int) -> tuple(Metadata, err.Error):
        if index < 0:
            return Metadata(), err.Error('Invalid index')
        
        if self.music_id_list is None or index >= len(self.music_id_list):
            return Metadata(), err.Error('Null list or length smaller than the index requested')
        
        meta = Metadata()
        meta.music_id = self.music_id_list[index]
        meta.danceability = self.danceability_list[index]
        meta.energy = self.energy_list[index]
        meta.loudness = self.loudness_list[index]
        meta.speechiness = self.speechiness_list[index]
        meta.acousticness = self.acousticness_list[index]
        meta.instrumentalness = self.instrumentalness_list[index]
        meta.liveness = self.liveness_list[index]
        meta.valence = self.valence_list[index]
        meta.tempo = self.tempo_list[index]
        meta.duration_ms = self.duration_ms_list[index]
        
        return meta, None
    
    def GetByMusicID(self, music_id: int) -> tuple(Metadata, err.Error):
        for index, meta_id in enumerate(self.music_id_list):
            if meta_id == music_id:
                return self.Get(index)
        
        return Metadata(), err.Error('Music metadata was not found')
        
    def Len(self) -> int:
        return len(MetadataList)
    
    def GetMedia(self) -> tuple(Metadata, err.Error):
        if self.music_id_list is None or len(self.music_id_list) == 0:
            return None, err.Error('Null list')
        
        # Fazer sistema de rankeamento, pegar o TIPO da musica
        # Desvio Padrão
        
        metadata = Metadata()
        metadata.danceability = float("{:.3f}".format(statistics.fmean(self.danceability_list)))
        metadata.energy = float("{:.3f}".format(statistics.fmean(self.energy_list)))
        metadata.loudness = float("{:.3f}".format(statistics.fmean(self.loudness_list)))
        metadata.speechiness = float("{:.3f}".format(statistics.fmean(self.speechiness_list)))
        metadata.acousticness = float("{:.3f}".format(statistics.fmean(self.acousticness_list)))
        metadata.instrumentalness = float("{:.3f}".format(statistics.fmean(self.instrumentalness_list)))
        metadata.liveness = float("{:.3f}".format(statistics.fmean(self.liveness_list)))
        metadata.valence = float("{:.3f}".format(statistics.fmean(self.valence_list)))
        metadata.tempo = float("{:.3f}".format(statistics.fmean(self.tempo_list)))
        metadata.duration_ms = float("{:.3f}".format(statistics.fmean(self.duration_ms_list)))
        
        return metadata, None
    
    def getDP(self) -> tuple(Metadata, err.Error):
        if self.music_id_list is None or len(self.music_id_list) == 0:
            return None, err.Error('Null list')
        
        # Fazer sistema de rankeamento, pegar o TIPO da musica
        # Desvio Padrão
        
        metadata = Metadata()
        metadata.danceability = float("{:.3f}".format(statistics.pstdev(self.danceability_list)))
        metadata.energy = float("{:.3f}".format(statistics.pstdev(self.energy_list)))
        metadata.loudness = float("{:.3f}".format(statistics.pstdev(self.loudness_list)))
        metadata.speechiness = float("{:.3f}".format(statistics.pstdev(self.speechiness_list)))
        metadata.acousticness = float("{:.3f}".format(statistics.pstdev(self.acousticness_list)))
        metadata.instrumentalness = float("{:.3f}".format(statistics.pstdev(self.instrumentalness_list)))
        metadata.liveness = float("{:.3f}".format(statistics.pstdev(self.liveness_list)))
        metadata.valence = float("{:.3f}".format(statistics.pstdev(self.valence_list)))
        metadata.tempo = float("{:.3f}".format(statistics.pstdev(self.tempo_list)))
        metadata.duration_ms = float("{:.3f}".format(statistics.pstdev(self.duration_ms_list)))
        
        return metadata, None
    
    def Sort(self) -> None:
        self.danceability_list.sort()
        self.energy_list.sort()
        self.loudness_list.sort()
        self.speechiness_list.sort()
        self.acousticness_list.sort()
        self.instrumentalness_list.sort()
        self.liveness_list.sort()
        self.valence_list.sort()
        self.tempo_list.sort()
        self.duration_ms_list.sort()