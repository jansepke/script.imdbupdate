################
# IMDB Update  #
# by Jandalf   #
################

from util import *
from imdbMovie import imdbMovie
import httplib

RATING_DIFF = 0.001
HIDE_MOVIES = settingBool("hideMovies")
ENABLE_RESUME = settingBool("enableResume") and not(HIDE_MOVIES)
ENABLE_DIFF = settingBool("enableDiff")

class Movies:
    def start(self, hidden=False):
        if hidden:
            global HIDE_MOVIES
            HIDE_MOVIES = True
        movies = getMoviesWith('imdbnumber', 'votes', 'rating')
        total = len(movies)
        if total > 0:
            self.startProcess(movies, total)
        else:
            dialogOk(l("Info"), l("The_video_library_is_empty_or_the_IMDb_id_doesn't_exist!"))
        return HIDE_MOVIES
            
    def getResume(self):
        wantResume = False
        if ENABLE_RESUME:
            try:
                resume = int(readF("resume_movies"))
                if resume > 0:
                    wantResume = dialogYN(l("The_previous_scraping_was_interrupted!"), l("Do_you_want_to_resume?"))
            except (IOError, ValueError):
                resume = 0
        if not(wantResume) or not(ENABLE_RESUME):
            deleteF("resume_movies")
            resume = 0
        return resume

    def writeResume(self, count):
        if ENABLE_RESUME:
            writeF("resume_movies", count)

    def startProcess(self, movies, total):
        updated = 0
        resume = self.getResume()
        if HIDE_MOVIES:
            notification(l("Started_updating_movies_ratings"))
        else:
            progress = dialogProgress()
        httphandler = httplib.HTTPConnection("www.omdbapi.com")
        for count, movie in enumerate(movies):
            if abortRequested() or (not(HIDE_MOVIES) and progress.iscanceled()):
                self.writeResume(count)
                break
            if count >= resume:
                if not(HIDE_MOVIES):
                    progress.update((count * 100) // total, "%s %s" % (l("Searching_for"), movie["label"]))
                updated += self.updateMovie(movie, httphandler)
        else:
            deleteF("resume_movies")
            writeDate("movies")
        text = "%s: %s %s %s %s!" % (l("Movies_ratings_summary"), updated, l("of"), total, l("were_updated"))
        log(text)
        if HIDE_MOVIES:
            notification(text)
        else:
            progress.close()
            dialogOk(l("Completed"), text)
                
    def updateMovie(self, movie, httphandler):
        result = 0
        if movie["imdbnumber"] == "":
            log("%s: %s" % (movie["label"], l("IMDb_id_was_not_found_in_your_database!")))
        else:
            imdb = imdbMovie(movie["imdbnumber"], httphandler)
            if imdb.error():
                log("%s: %s" % (movie["label"], l("There_was_a_problem_with_the_IMDb_site!")))
            elif (imdb.votes() == "0") or (imdb.votes() == "N/A"):
                log("%s: %s" % (movie["label"], l("Nothing_to_do_the_current_rating_is_zero!")))
            elif not(self.shouldUpdate(movie, imdb)):
                log("%s: %s" % (movie["label"], l("Nothing_to_do_has_already_been_updated!")))
            else:
                executeJSON('VideoLibrary.SetMovieDetails', {'movieid':movie['movieid'], 'rating':float(imdb.rating()), 'votes':imdb.votes()})
                log("%s: %s %s %s %s %s" % (movie["label"], l("was_updated_to"), imdb.rating(), l("with"), imdb.votes(), l("voters!")))
                result = 1
        return result
    
    def shouldUpdate(self, old, new):
        if old["votes"] == '':
            oldVotes = 0
        else:
            oldVotes = float(old["votes"].replace(",", ""))
        newVotes = float(new.votes().replace(",", ""))
        oldRating = round(float(old["rating"]), 1)
        newRating = round(float(new.rating()), 1)
        result = oldRating != newRating or (ENABLE_DIFF and ((oldVotes > newVotes) or (round(oldVotes * (1 + RATING_DIFF)) < newVotes))) or oldVotes != newVotes
        return result