import service.spotify.spotify as spotify
import lib.spotify.spotifyUtils as lib
import lib.metadata.metadataUtils as metaUtil
import model.metadata.metadata as meta
import requests as req

def generateCSV(token: str, playlistId: int) -> None:
    url = "https://api.spotify.com/v1/playlists/{}/tracks?fields=items(track(id,artists(id)))&limit=50" \
        .format(playlistId)
    r = req.get(url=url, headers={'Authorization':'Bearer ' + token})
    
    data = r.json()
    r.close()

    if r.status_code != 200:
        print('An error ocurred trying to get tracks of one playlist.\nError: {}\nPlaylistID: {}' \
            .format(data['error'], playlistId))
        return
    
    structure = {}
    structure['metadata'] = {}
    structure['genres'] = []
    
    for track in data['items']:
        if track['track']['id'] is not None and str(track['track']['id']) != "":
            current_metadata = spotify.getTrackMetaData(token, track['track']['id'])
            structure['metadata'] = current_metadata
            for artist_data in track['track']['artists']:
                if (artist_data['id'] is not None):
                    artist, error = spotify.getArtist(token, artist_data['id'])
                    
                    if error is not None:
                        continue
                    
                    for genre in artist.genres:
                        if (genre is not None):
                            if str(genre) not in structure['genres']:
                                structure['genres'].append(str(genre))
            print(structure)
            structure['metadata'] = {}
            structure['genres'] = []
            
def testAddMusics(token: str, playlistID: int) -> None:
    test_musics = []
    test_musics.append({"musicID": "4QfMUPyVRurqeIH1k4a9Ky", "include": False})
    test_musics.append({"musicID": "5UFXAE1QXIGnmALcrQ4DgZ", "include": False})
    test_musics.append({"musicID": "2gMQHahD4hFjnEYjTTyivU", "include": False})
    test_musics.append({"musicID": "3QOruXa2lvqIFvOOa2rYyJ", "include": False})
    test_musics.append({"musicID": "3WHGMx4tWMsJdhHEVmG4ox", "include": False})
    test_musics.append({"musicID": "2ywk9oDKsNUZ7YXxed4AnA", "include": False})
    test_musics.append({"musicID": "1TFjgmDNqtfw2R0ruYZkUI", "include": False})
    test_musics.append({"musicID": "5dvHlfjmu4AaxlTbUYQabN", "include": False})
    test_musics.append({"musicID": "2h96laC0Hjwx49xROS1rYz", "include": False})
    test_musics.append({"musicID": "0ecM7uGyjgJnBliXS2fPP9", "include": False})
    test_musics.append({"musicID": "2aTfkAV3oxoBF5FJvUY4ja", "include": False})
    test_musics.append({"musicID": "3Rl26h1HiMCV0HFHHVb2IM", "include": False})
    
    test_musics.append({"musicID": "0ZALvx5UEaw0lMUexypBI8", "include": True})
    test_musics.append({"musicID": "6WeNs3jrqfw624KlcNYect", "include": True})
    test_musics.append({"musicID": "5413LFXLYAJS85VKs6H6ag", "include": True})
    test_musics.append({"musicID": "2N39ObBUyuEdT2dMvKRTBz", "include": True})
    test_musics.append({"musicID": "01TyFEZu6mHbffsVfxgrFn", "include": True})
    test_musics.append({"musicID": "6Ijmj8Z0L31hCp5pLZnT5U", "include": True})
    test_musics.append({"musicID": "5cW8mZYs5mKGZP5n2azBW3", "include": True})
    test_musics.append({"musicID": "7l8UyITgVXQyadELQgToFP", "include": True})
    test_musics.append({"musicID": "1eoGO19WEflJbAV8BLebhr", "include": True})
    test_musics.append({"musicID": "0ROCe58wXm7sBUPkZaRrnY", "include": True})
    test_musics.append({"musicID": "0qlwDRhrYcE5JC07JbXTer", "include": True})
    test_musics.append({"musicID": "35QAUfIbfIXT3p3cWhaKxZ", "include": True})
    
    data, error = lib.getDataFromPlaylistsFile()
    if error is not None:
        print(error.Message)
        return
        
    for playlist in data['playlists']:
        if playlist['id'] == playlistID:
            for x in range(0, len(test_musics), 1):
                print("Testing Music[{}]. Novos DP's:".format(x))
                
                metadata, error = spotify.getTrackMetaData(token, test_musics[x]['musicID'])
                if error is not None:
                    print(error.Message)
                    continue
                
                dp = meta.Metadata()
                dp.danceability = metaUtil.recalculateDP(playlist['metadata']['danceability']['data'], metadata.danceability)
                dp.energy = metaUtil.recalculateDP(playlist['metadata']['energy']['data'], metadata.energy)
                dp.loudness = metaUtil.recalculateDP(playlist['metadata']['loudness']['data'], metadata.loudness)
                dp.speechiness = metaUtil.recalculateDP(playlist['metadata']['speechiness']['data'], metadata.speechiness)
                dp.acousticness = metaUtil.recalculateDP(playlist['metadata']['acousticness']['data'], metadata.acousticness)
                dp.instrumentalness = metaUtil.recalculateDP(playlist['metadata']['instrumentalness']['data'], metadata.instrumentalness)
                dp.liveness = metaUtil.recalculateDP(playlist['metadata']['liveness']['data'], metadata.liveness)
                dp.valence = metaUtil.recalculateDP(playlist['metadata']['valence']['data'], metadata.valence)
                dp.tempo = metaUtil.recalculateDP(playlist['metadata']['tempo']['data'], metadata.tempo)
                dp.duration_ms = metaUtil.recalculateDP(playlist['metadata']['duration_ms']['data'], metadata.duration_ms)
                
                print('danceability: {} --> variou {}'.format(dp.danceability, float("{:.4f}".format(abs(dp.danceability - playlist['metadata']['danceability']['dp'])))))
                print('energy: {} --> variou {}'.format(dp.energy, float("{:.4f}".format(abs(dp.energy - playlist['metadata']['energy']['dp'])))))
                print('loudness: {} --> variou {}'.format(dp.loudness, float("{:.4f}".format(abs(dp.loudness - playlist['metadata']['loudness']['dp'])))))
                print('speechiness: {} --> variou {}'.format(dp.speechiness, float("{:.4f}".format(abs(dp.speechiness - playlist['metadata']['speechiness']['dp'])))))
                print('acousticness: {} --> variou {}'.format(dp.acousticness, float("{:.4f}".format(abs(dp.acousticness - playlist['metadata']['acousticness']['dp'])))))
                print('instrumentalness: {} --> variou {}'.format(dp.instrumentalness, float("{:.4f}".format(abs(dp.instrumentalness - playlist['metadata']['instrumentalness']['dp'])))))
                print('liveness: {} --> variou {}'.format(dp.liveness, float("{:.4f}".format(abs(dp.liveness - playlist['metadata']['liveness']['dp'])))))
                print('valence: {} --> variou {}'.format(dp.valence, float("{:.4f}".format(abs(dp.valence - playlist['metadata']['valence']['dp'])))))
                print('tempo: {} --> variou {}'.format(dp.tempo, float("{:.4f}".format(abs(dp.tempo - playlist['metadata']['tempo']['dp'])))))
                print('duration_ms: {} --> variou {}'.format(dp.duration_ms, float("{:.4f}".format(abs(dp.duration_ms - playlist['metadata']['duration_ms']['dp'])))))
                print('ERA PARA ADICIONAR? {}\n'.format(test_musics[x]['include']))