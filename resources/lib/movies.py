################
# IMDB Update  #
# by Jandalf   #
################

import urllib2
from util import *

class omdbMovie(object):
    def __init__(self, imdbID):
        self.__rating = ""
        self.__votes = ""
        self.__error = False
        self.__imdbID = imdbID
        self.getData()

    def getData(self):
        try:
            response = urllib2.urlopen("http://www.omdbapi.com/?i=%s" % self.__imdbID)
            if response.getcode() == 200:
                data = json.loads(response.read().decode('utf8'))
                if "error" in data:
                    self.__error = True
                elif data["Response"] == "False":
                    self.__error = True
                else:
                    self.__rating = data["imdbRating"]
                    self.__votes = str(data["imdbVotes"])
            else:
                self.__error = True
        except:
            self.__error = True  
    
    def rating(self):   return self.__rating
    def votes(self):    return self.__votes
    def error(self):    return self.__error
    def imdbID(self):   return self.__imdbID

class Movies:
    def __init__(self):
        resume = self.getResume()
        movies = self.getMovies()
        total = len(movies)
        if total > 0:
            self.startProcess(movies, total, resume)
        else:
            dialogOk(l("Info"), l("The_video_library_is_empty_or_the_IMDb_id_doesn't_exist!"))
            
    def getResume(self):
        resume = 0
        RATING_DIFF = 0.001
        if setting("enableResume") == "true":
            try:
                resume = int(readF("resume_movies"))
                if resume != 0:
                    wantResume = dialogYN(l("The_previous_scraping_was_interrupted!"), l("Do_you_want_to_resume?"))
                if not (wantResume):
                    deleteF("resume_movies")
                    resume = 0
            except IOError:
                pass
        return resume

    def getMovies(self):
        movies = executeJSON("VideoLibrary.GetMovies", '{"properties":["imdbnumber","votes","rating"],"sort":{"order":"ascending","method":"label","ignorearticle":true }}')
        return movies["result"]["movies"]

    def startProcess(self, movies, total, resume):
        updated = 0
        unfinished = False
        progress = dialogProgress()
        for count, movie in enumerate(movies):
            if progress.iscanceled():
                writeF("resume_movies", count)
                unfinished = True
                break
            elif count >= resume:
                progress.update((count * 100) // total, "%s %s" % (l("Searching_for"), movie["label"]))
                updated += self.updateMovie(movie)
        progress.close()
        if unfinished:
            dialogOk(l("Abort"), l("The_scraping_was_canceled_by_user!"))
        else:
            deleteF("resume_movies")
        text = "%s: %s %s %s %s!" % (l("Movies_ratings_summary"), updated, l("of"), total, l("were_updated"))
        log(text)
        dialogOk(l("Completed"), text)
                
    def updateMovie(self, movie):
        result = 0
        enableDiff = setting("enableDiff") == "true"
        if movie["imdbnumber"] == "":
            log("%s: %s" % (movie["label"], l("IMDb_id_was_not_found_in_your_database!")))
        else:
            m = omdbMovie(movie["imdbnumber"])
            if m.error():
                log("%s: %s" % (movie["label"], l("There_was_a_problem_with_the_IMDb_site!")))
            else:
                if m.votes() == "0" or m.votes() == "N/A":
                    log("%s: %s" % (movie["label"], l("Nothing_to_do_the_current_rating_is_zero!")))
                elif not(self.shouldUpdate(movie, m, enableDiff)):
                    log("%s: %s" % (movie["label"], l("Nothing_to_do_has_already_been_updated!")))
                else:
                    executeJSON("VideoLibrary.SetMovieDetails", '{"movieid":%s,"rating":%s,"votes":"%s"}' % (movie["movieid"], m.rating(), m.votes()))
                    log("%s: %s %s %s %s %s" % (movie["label"], l("was_updated_to"), m.rating(), l("with"), m.votes(), l("voters!")))
                    result = 1
        return result
    
    def shouldUpdate(self, old, new, enableDiff):
        oldVotes = float(old["votes"].replace(",", ""))
        newVotes = float(new.votes().replace(",", ""))
        result = False
        result = round(float(old["rating"]), 1) != round(float(new.rating()), 1)
        if not(result):
            if enableDiff:
                result = (oldVotes > newVotes or round(oldVotes * 1.001) < newVotes)
            else:
                result = oldVotes != newVotes
        return result
