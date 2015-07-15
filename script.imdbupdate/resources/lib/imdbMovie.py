################
# IMDB Update  #
# by Jandalf   #
################

import httplib, socket, json, util

RATING_DIFF = 0.001
ENABLE_DIFF = util.settingBool("enableDiff")
SEPARATOR = util.setting("separator").strip()

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
                        self.__votes = int(data["imdbVotes"])
                except:
                    self.__error = True
            else:
                self.__error = True

    def shouldUpdate(self, old):
        oldVotes = 0 if old["votes"] == '' else util.stringToFloat(old["votes"])
        newVotes = self.__votes

        votesChange = (oldVotes != newVotes) if not ENABLE_DIFF else (oldVotes > newVotes or round(oldVotes * (1 + RATING_DIFF)) < newVotes)

        oldRating = round(float(old["rating"]), 1)
        newRating = round(float(self.__rating), 1)

        return (oldRating != newRating) or votesChange
    
    def rating(self):   return self.__rating
    def votes(self):    return "{:,}".format(self.__votes).replace(",", SEPARATOR)
    def error(self):    return self.__error
    def imdbID(self):   return self.__imdbID