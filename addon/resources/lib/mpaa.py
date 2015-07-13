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
FIRST_RUN       = util.settingBool("firstMpaaRun")

class Mpaa:
    def start(self, hidden=False):
        if FIRST_RUN:
            global LANG_MPAA
            langs = ["US", "DE"]
            LANG_MPAA = langs[util.dialogSelect(l("Choose_your_MPAA_system"), langs)]
            util.setting("mpaaLang", LANG_MPAA)
            util.settingBool("firstMpaaRun", False)

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
        if movie["imdbnumber"] == "":
            util.logWarning("%(label)s: no IMDb id" % movie)
        else:
            mpaa = imdbMpaa(movie["imdbnumber"], httphandler, LANG_MPAA)

            formattedRating = ("%s%s" if ":" in FORM_MPAA else "%s %s") % (FORM_MPAA, mpaa.rating())

            if mpaa.error():
                util.logError("%s: problem with MPAA site" % movie["label"])
            elif movie["mpaa"] != formattedRating:
                util.executeJSON('VideoLibrary.SetMovieDetails', {'movieid':movie['movieid'], 'mpaa':formattedRating})
                util.log("%s: updated from %s to %s" % (movie["label"], movie["mpaa"], formattedRating))
                return 1

        return 0