################
# IMDB Update  #
# by Jandalf   #
################

from imdbMovie import imdbMovie
import util

HIDE_MOVIES = util.settingBool("hideMovies")
ENABLE_RESUME = util.settingBool("enableResume") and not(HIDE_MOVIES)

class Movies:
    def start(self, hidden=False):
        if hidden:
            global HIDE_MOVIES
            HIDE_MOVIES = True

        movies = util.getMoviesWith('imdbnumber', 'votes', 'rating')
        total = len(movies)

        if total > 0:
            self.startProcess(movies, total)
        else:
            util.dialogOk(util.l("Info"), util.l("The_video_library_is_empty_or_the_IMDb_id_doesn't_exist!"))

        return HIDE_MOVIES

    def getResume(self):
        wantResume = False
        if ENABLE_RESUME:
            try:
                resume = int(util.readF("resume_movies"))
                if resume > 0:
                    wantResume = util.dialogYN(util.l("The_previous_scraping_was_interrupted!"), util.l("Do_you_want_to_resume?"))
            except (IOError, ValueError):
                resume = 0

        if not(wantResume) or not(ENABLE_RESUME):
            util.deleteF("resume_movies")
            resume = 0

        return resume

    def writeResume(self, count):
        if ENABLE_RESUME:
            util.writeF("resume_movies", count)

    def startProcess(self, movies, total):
        updated = 0
        resume = self.getResume()

        if HIDE_MOVIES:
            util.notification(util.l("Started_updating_movies_ratings"))
        else:
            progress = util.dialogProgress()

        for count, movie in enumerate(movies):
            if util.abortRequested() or (not(HIDE_MOVIES) and progress.iscanceled()):
                self.writeResume(count)
                break
            if count >= resume:
                if not(HIDE_MOVIES):
                    progress.update((count * 100) // total, "%s %s" % (util.l("Searching_for"), movie["label"]))
                updated += self.updateMovie(movie)
        else:
            util.deleteF("resume_movies")
            util.writeDate("movies")

        text = "%s: %s %s %s %s!" % (util.l("Movies_ratings_summary"), updated, util.l("of"), total, util.l("were_updated"))
        util.log(text)

        if HIDE_MOVIES:
            util.notification(text)
        else:
            progress.close()
            util.dialogOk(util.l("Completed"), text)

    def updateMovie(self, movie):
        if movie["imdbnumber"] == "":
            util.logWarning("%s: no IMDb id" % movie["label"])
        else:
            imdb = imdbMovie(movie["imdbnumber"])

            if imdb.error():
                util.logError("%s: problem with omdbapi.com" % movie["label"])
            elif (imdb.votes() == "0") or (imdb.votes() == "N/A"):
                util.logWarning("%s: no votes available" % movie["label"])
            elif not(imdb.shouldUpdate(movie)):
                util.logDebug("%s: is up to date" % movie["label"])
            else:
                util.executeJSON('VideoLibrary.SetMovieDetails', {'movieid': movie['movieid'], 'rating': float(imdb.rating()), 'votes': imdb.votes()})
                util.log("%s: updated from %s (%s) to %s (%s)" % (movie["label"], movie["rating"], movie["votes"], imdb.rating(), imdb.votes()))
                return 1

        return 0
