################
# MPAA Update  #
# by semool    #
################

import httplib, socket, json

class imdbMpaa(object):

    def __init__(self, imdbID, httphandler, LANG_MPAA):
        self.__rating = ""
        self.__error = False
        self.__imdbID = imdbID
        self.__Lang = LANG_MPAA
        
        self.getData(httphandler)

    def getData(self, httphandler):
        try:
            httphandler.request("GET", "/api2/s/%s/%s/d40f5ad016fa" % (self.__imdbID, self.__Lang))
            response = httphandler.getresponse()
        except (httplib.HTTPException, socket.timeout, socket.gaierror, socket.error):
            self.__error = True
        if self.__error == False:
            try:
                data = response.read().decode('utf8')
                data = str(data)
                if data == "100" or data == "300" or data == "310":
                   self.__error = True
                else:
                   self.__rating = data
            except:
                self.__error = True
        else:
            self.__error = True

    def rating(self):   return self.__rating
    def error(self):    return self.__error
    def imdbID(self):   return self.__imdbID
