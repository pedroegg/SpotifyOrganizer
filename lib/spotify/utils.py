def getTokenFromURL(url):
    return str(url).split('#')[1].split('&')[0].split('=')[1]