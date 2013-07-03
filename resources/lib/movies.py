################
# IMDB Update  #
# by Jandalf   #
################

from util import *
from imdbMovie import imdbMovie

RATING_DIFF     = 0.001
HIDE_MOVIE      = settingBool("hideMovie")
ENABLE_RESUME   = settingBool("enableResume") and not(HIDE_MOVIE)
ENABLE_DIFF     = settingBool("enableDiff")

class Movies:
    def start(self):
        resume = self.getResume()
        movies = self.getMovies()
        total = len(movies)
        if total > 0:
            self.startProcess(movies, total, resume)
        else:
            dialogOk(l("Info"), l("The_video_library_is_empty_or_the_IMDb_id_doesn't_exist!"))
        return HIDE_MOVIE
            
    def getResume(self):
        wantResume = False
        if ENABLE_RESUME and not(HIDE_MOVIE):
            try:
                resume = int(readF("resume_movies"))
                if resume > 0:
                    wantResume = dialogYN(l("The_previous_scraping_was_interrupted!"), l("Do_you_want_to_resume?"))
            except IOError, ValueError:
                resume = 0
        if not(wantResume) or not(ENABLE_RESUME) or HIDE_MOVIE:
            deleteF("resume_movies")
            resume = 0
        return resume

    def getMovies(self):
        movies = executeJSON("VideoLibrary.GetMovies", '{"properties":["imdbnumber","votes","rating"],"sort":{"order":"ascending","method":"label","ignorearticle":true }}')
        return movies["result"]["movies"]


    def writeResume(self, count):
        if ENABLE_RESUME:
            writeF("resume_movies", count)

    def startProcess(self, movies, total, resume):
        updated = 0
        unfinished = False
        if HIDE_MOVIE:
            notification(l("Started_updating_movies_ratings"))
        else:
            progress = dialogProgress()
        for count, movie in enumerate(movies):
            if HIDE_MOVIE:
                updated += self.updateMovie(movie)
            elif progress.iscanceled():
                self.writeResume(count)
                unfinished = True
                break
            elif count >= resume:
                progress.update((count * 100) // total, "%s %s" % (l("Searching_for"), movie["label"]))
                updated += self.updateMovie(movie)
        if not(HIDE_MOVIE):
            progress.close()
        if unfinished:
            dialogOk(l("Abort"), l("The_scraping_was_canceled_by_user!"))
        else:
            deleteF("resume_movies")
        text = "%s: %s %s %s %s!" % (l("Movies_ratings_summary"), updated, l("of"), total, l("were_updated"))
        log(text)
        if HIDE_MOVIE:
            notification(text)
        else:
            dialogOk(l("Completed"), text)
                
    def updateMovie(self, movie):
        result = 0
        if movie["imdbnumber"] == "":
            log("%s: %s" % (movie["label"], l("IMDb_id_was_not_found_in_your_database!")))
        else:
            m = imdbMovie(movie["imdbnumber"])
            if m.error():
                log("%s: %s" % (movie["label"], l("There_was_a_problem_with_the_IMDb_site!")))
            else:
                if (m.votes() == "0") or (m.votes() == "N/A"):
                    log("%s: %s" % (movie["label"], l("Nothing_to_do_the_current_rating_is_zero!")))
                elif not(self.shouldUpdate(movie, m)):
                    log("%s: %s" % (movie["label"], l("Nothing_to_do_has_already_been_updated!")))
                else:
                    executeJSON("VideoLibrary.SetMovieDetails", '{"movieid":%s,"rating":%s,"votes":"%s"}' % (movie["movieid"], m.rating(), m.votes()))
                    log("%s: %s %s %s %s %s" % (movie["label"], l("was_updated_to"), m.rating(), l("with"), m.votes(), l("voters!")))
                    result = 1
        return result
    
    def shouldUpdate(self, old, new):
        oldVotes = float(old["votes"].replace(",", ""))
        newVotes = float(new.votes().replace(",", ""))
        result = False
        result = round(float(old["rating"]), 1) != round(float(new.rating()), 1)
        if not(result):
            if ENABLE_DIFF:
                result = ((oldVotes > newVotes) or (round(oldVotes * (1 + RATING_DIFF)) < newVotes))
            else:
                result = oldVotes != newVotes
        return result
