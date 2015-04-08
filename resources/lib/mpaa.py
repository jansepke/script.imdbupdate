################
# MPAA Update  #
# by semool    #
################

from util import *
from imdbmpaa import imdbMpaa
import httplib

HIDE_MPAA = settingBool("hideMpaa")
LANG_MPAA = addOn.getSetting("mpaaLang")
FORM_MPAA = addOn.getSetting("mpaaFormat")

class Mpaa:
    def start(self, hidden=False):
        if hidden:
            global HIDE_MPAA
            HIDE_MPAA = True
        movies = getMoviesWith('imdbnumber', 'mpaa')
        total = len(movies)
        if total > 0:
            self.startProcess(movies, total)
        else:
            dialogOk(l("Info"), l("The_video_library_is_empty_or_the_IMDb_id_doesn't_exist!"))
        return HIDE_MPAA

    def startProcess(self, movies, total):
        updated = 0
        resume = 0
        if HIDE_MPAA:
            notification(l("Started_updating_movies_ratings"))
        else:
            progress = dialogProgress()
        if LANG_MPAA == "DE":
            SITEUSE = "altersfreigaben.de"
        if LANG_MPAA == "US":
            SITEUSE = "www.omdbapi.com"
        httphandler = httplib.HTTPConnection(SITEUSE)
        for count, movie in enumerate(movies):
            if abortRequested() or (not(HIDE_MPAA) and progress.iscanceled()):
                break
            if not(HIDE_MPAA):
                progress.update((count * 100) // total, "%s %s" % (l("Searching_for"), movie["label"]))
            updated += self.updateMovie(movie, httphandler, LANG_MPAA)
        text = "%s: %s %s %s %s!" % (l("Movies_ratings_summary"), updated, l("of"), total, l("were_updated"))
        log(text)
        if HIDE_MPAA:
            notification(text)
        else:
            progress.close()
            dialogOk(l("Completed"), text)
                
    def updateMovie(self, movie, httphandler, LANG_MPAA):
        result = 0
        if movie["imdbnumber"] == "":
            log("%s: %s" % (movie["label"], l("IMDb_id_was_not_found_in_your_database!")))
        else:
            mpaa = imdbMpaa(movie["imdbnumber"], httphandler, LANG_MPAA)
            if ":" in FORM_MPAA:
                FINAL_RATING = "%s%s" % (FORM_MPAA, mpaa.rating())
            else:
            	  FINAL_RATING = "%s %s" % (FORM_MPAA, mpaa.rating())
            if mpaa.error():
                log("%s: %s" % (movie["label"], l("There_was_a_problem_with_the_MPAA_site!")))
            elif not(self.shouldUpdate(movie, FINAL_RATING)):
                log("%s: %s" % (movie["label"], l("Nothing_to_do_has_already_been_updated!")))
            else:
                executeJSON('VideoLibrary.SetMovieDetails', {'movieid':movie['movieid'], 'mpaa':FINAL_RATING})
                log("%s: %s %s" % (movie["label"], l("was_updated_to"), FINAL_RATING))
                result = 1
        return result

    def shouldUpdate(self, old, new):
        oldRating = old["mpaa"]
        newRating = new
        result = oldRating != newRating
        return result