import sys
from datetime import datetime, timedelta
import service.spotify.spotify as spotify
import lib.spotify.spotifyUtils as lib
import env.env
import test.test as test
import chromedriver_autoinstaller

# CONTORNAR ERRO DE SERVICO 500
# Mudar nome da funcao que gera o playlist.json para generatePlaylistsJSON
# Fazer funcoes mais pequenas, para fracionar mais, como por exemplo uma para pegar generos da musica
# Fazer a funcao que pega os generos e liga a playlists
# Fazer a funcao que adiciona nas playlists
# Fazer cada playlist ter os seus generos mais compativeis, os tops, os que mais bateram
# Fazer o selecionamento das playlists por metadados
# Fazer o selecionamento das playlists por top genre
# Fazer uma maneira mais facil de editar o json
# Fazer parametro para varredura de playlists com apenas playlists selecionadas. Poupar tempo e custo
# Fazer parametros de chamada do programa
# Fazer o tratamento para o GMT

# Criar parametro para atualizar o json das playlists
updatePlaylistsJSON = bool(int(sys.argv[2]))

# Limit date is the date under x days from today. This date is used to get musics where date is
# equal or greater than this date
limitDate = datetime.today() - timedelta(days=int(sys.argv[1]))
limitDate = limitDate.date()
   
def main():
    chromedriver_autoinstaller.install() # If chrome doesn't appear, comment this line
    token = spotify.getToken()
    if token != "":
        if (not lib.checkExistencePlaylistsFile()) or (updatePlaylistsJSON):
            error = lib.writePlaylistJSON(token)
            if error is not None:
                print(error.Message)
        
        # test.generateCSV(token, '4Uz5RgDqU35EIbjykAhamm') # didn't tested it again
        # test.testAddMusics(token, '5I6Xwr1APbaJWJlaiWEbXS')
        error = lib.organizeLikedMusics(token, limitDate)
        if error is not None:
            print(error.Message)
    
if __name__ == "__main__":
    main()