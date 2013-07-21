################
# IMDB Update  #
# by Jandalf   #
################

import urllib2, socket
import simplejson as json

class imdbMovie(object):
    def __init__(self, imdbID):
        self.__rating = ""
        self.__votes = ""
        self.__error = False
        self.__imdbID = imdbID
        self.getData()

    def getData(self):
        try:
            response = urllib2.urlopen("http://www.omdbapi.com/?i=%s" % self.__imdbID)
        except (urllib2.URLError, socket.timeout):
            self.__error = True
        else:
            if response.getcode() == 200:
                data = json.loads(response.read().decode('utf8'))
                if "error" in data or data["Response"] == "False":
                    self.__error = True
                else:
                    self.__rating = data["imdbRating"]
                    self.__votes = str(data["imdbVotes"])
            else:
                self.__error = True
    
    def rating(self):   return self.__rating
    def votes(self):    return self.__votes
    def error(self):    return self.__error
    def imdbID(self):   return self.__imdbID
