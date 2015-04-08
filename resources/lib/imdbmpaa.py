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
            if self.__Lang == "DE":
                httphandler.request("GET", "/api/imdb_id/%s" % self.__imdbID)
            if self.__Lang == "US":
                httphandler.request("GET", "/?i=%s" % self.__imdbID)
            response = httphandler.getresponse()
        except (httplib.HTTPException, socket.timeout, socket.gaierror, socket.error):
            self.__error = True
        else:
            if response.status == 200:
                try:
                    if self.__Lang == "DE":
                       data = json.loads(response.read().decode('utf8'))
                       data = str(data)
                       if data == "100" or data == "200" or data == "300":
                          self.__error = True
                       else:
                          self.__rating = data
                    if self.__Lang == "US":
                      data = json.loads(response.read().decode('utf8'))
                      if "error" in data or data["Response"] == "False":
                        self.__error = True
                      else:
                        self.__rating = str(data["Rated"])
                except:
                    self.__error = True
            else:
                self.__error = True
    
    def rating(self):   return self.__rating
    def error(self):    return self.__error
    def imdbID(self):   return self.__imdbID