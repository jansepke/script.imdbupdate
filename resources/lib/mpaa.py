################
# MPAA Update  #
# by semool    #
################

from util import l
from imdbmpaa import imdbMpaa
import util, httplib

HIDE_MPAA       = util.settingBool("hideMpaa")
LANG_MPAA       = util.setting("mpaaLang")
FORM_MPAA       = util.setting("mpaaPrefix")
CHANGED_PREFIX  = util.settingBool("enableMpaaPrefix")

class Mpaa:
    def start(self, hidden=False):
        if hidden:
            global HIDE_MPAA
            HIDE_MPAA = True

        movies = util.getMoviesWith('imdbnumber', 'mpaa')
        total = len(movies)

        if total > 0:
            self.startProcess(movies, total)
        else:
            util.dialogOk(l("Info"), l("The_video_library_is_empty_or_the_IMDb_id_doesn't_exist!"))

        return HIDE_MPAA

    def startProcess(self, movies, total):
        global FORM_MPAA
        updated = 0

        if HIDE_MPAA:
            util.notification(l("Started_updating_movies_ratings"))
        else:
            progress = util.dialogProgress()

        if LANG_MPAA == "DE":
            website = "altersfreigaben.de"
            if not CHANGED_PREFIX:
               FORM_MPAA = "germany:"
        if LANG_MPAA == "US":
            website = "www.omdbapi.com"
            if not CHANGED_PREFIX:
               FORM_MPAA = "Rated"

        httphandler = httplib.HTTPConnection(website)

        for count, movie in enumerate(movies):
            if util.abortRequested() or (not(HIDE_MPAA) and progress.iscanceled()):
                break

            if not(HIDE_MPAA):
                progress.update((count * 100) // total, "%s %s" % (l("Searching_for"), movie["label"]))

            updated += self.updateMovie(movie, httphandler, LANG_MPAA)
        else:
            util.writeDate("mpaa")

        text = "%s: %s %s %s %s!" % (l("Movies_ratings_summary"), updated, l("of"), total, l("were_updated"))
        util.log(text)

        if HIDE_MPAA:
            util.notification(text)
        else:
            progress.close()
            util.dialogOk(l("Completed"), text)
                
    def updateMovie(self, movie, httphandler, LANG_MPAA):
        result = 0

        if movie["imdbnumber"] == "":
            util.log("%s: %s" % (movie["label"], l("IMDb_id_was_not_found_in_your_database!")))
        else:
            mpaa = imdbMpaa(movie["imdbnumber"], httphandler, LANG_MPAA)

            formattedRating = ("%s%s" if ":" in FORM_MPAA else "%s %s") % (FORM_MPAA, mpaa.rating())

            if mpaa.error():
                util.log("%s: %s" % (movie["label"], l("There_was_a_problem_with_the_MPAA_site!")))
            elif not(movie["mpaa"] != formattedRating):
                util.log("%s: %s" % (movie["label"], l("Nothing_to_do_has_already_been_updated!")))
            else:
                util.executeJSON('VideoLibrary.SetMovieDetails', {'movieid':movie['movieid'], 'mpaa':formattedRating})
                util.log("%s: %s %s" % (movie["label"], l("was_updated_to"), formattedRating))
                result = 1

        return result