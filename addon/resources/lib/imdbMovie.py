################
# IMDB Update  #
# by Jandalf   #
################

import httplib, socket, json

class imdbMovie(object):
    
    def __init__(self, imdbID, httphandler):
        self.__rating = ""
        self.__votes = ""
        self.__error = False
        self.__imdbID = imdbID
        
        self.getData(httphandler)

    def getData(self, httphandler):
        try:
            httphandler.request("GET", "/?i=%s" % self.__imdbID)
            response = httphandler.getresponse()
        except (httplib.HTTPException, socket.timeout, socket.gaierror, socket.error):
            self.__error = True
        else:
            if response.status == 200:
                try:
                    data = json.loads(response.read().decode('utf8'))
                    if "error" in data or data["Response"] == "False":
                        self.__error = True
                    else:
                        self.__rating = data["imdbRating"]
                        self.__votes = str(data["imdbVotes"])
                except:
                    self.__error = True
            else:
                self.__error = True
    
    def rating(self):   return self.__rating
    def votes(self):    return self.__votes
    def error(self):    return self.__error
    def imdbID(self):   return self.__imdbID