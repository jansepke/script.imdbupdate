################
# IMDB Update  #
# by Jandalf   #
################

import urllib2, re, socket, csv
from BeautifulSoup import BeautifulSoup
from util import *

HIDE_TOP250 = settingBool("hideTop250")

class Top250:
    def start(self, hidden=False):
        if hidden:
            global HIDE_TOP250
            HIDE_TOP250 = True

        if HIDE_TOP250:
            notification(l("Importing_current_IMDb_Top250"))
        else:
            self.progress = dialogProgress()
            self.progress.update(0, l("Importing_current_IMDb_Top250"))

        self.top250 = self.getTop250()

        if self.top250 == {}:
            dialogOk(l("Top250"), l("There_was_a_problem_with_the_IMDb_site!"))
        else:
            movies = getMoviesWith('imdbnumber', 'top250')
            length = len(movies)
            if length > 0:
                self.startProcess(movies, length)
            else:
                dialogOk(l("Info"), l("The_video_library_is_empty_or_the_IMDb_id_doesn't_exist!"))

        if not(HIDE_TOP250):
            self.progress.close()

        return HIDE_TOP250

    def getTop250(self):
        opener = urllib2.build_opener()
        opener.addheaders = [("User-agent", "Mozilla/5.0")]

        try:
            response = opener.open("http://www.imdb.com/chart/top")
        except (urllib2.URLError, socket.timeout):
            logDebug("Top250: Could not connect to imdb.com")
            return {}

        if response.getcode() == 200:
            soup = BeautifulSoup(response).findAll("a", href=re.compile("/title/tt"), title=True)
            top250 = [{"id": tt["href"][7:16].encode('utf-8'), "label": tt.contents[0]} for tt in soup if tt.parent.parent.name == "tr"]
            return {v["id"]: {"position": k, "label": v["label"]} for k, v in enumerate(top250, start=1)} if len(top250) == 250 else {}
            
    def startProcess(self, movies, length):
        stats = {"added": 0, "updated": 0, "removed": 0}

        for count, movie in enumerate(movies):
            if abortRequested() or (not(HIDE_TOP250) and self.progress.iscanceled()):
                break

            result = self.checkMovie(movie)
            if result != None:
                stats[result] += 1

            if not(HIDE_TOP250):
                self.progress.update((count * 100) // length, "%s %s" % (l("Searching_for"), movie["label"]))
        else:
            writeDate("top250")
            missing = [[v["position"], k, v["label"]] for k,v in self.top250.iteritems()]
            missing.sort(key=lambda x: x[0])
            missing.insert(0, ["Position", "IMDb ID", "Name"])
            writeCSV("missingTop250.csv", missing)

        stats["missing"] = len(self.top250)
        log("Movies IMDb Top250 summary: updated: %(updated)s, added: %(added)s, removed: %(removed)s, missing: %(missing)s" % stats)

        if HIDE_TOP250:
            notification("%s %s" % (l("Completed"), l("Top250")))
        else:
            dialogOk(l("Completed"), l("Movies_IMDb_Top250_summary"), "%s %s" % (stats["updated"], l("were_updated")), "%s %s %s %s" % (stats["added"], l("were_added_and"), stats["removed"], l("were_removed!")))

    def checkMovie(self, movie):
        imdbNumber = movie["imdbnumber"]
        oldPosition = movie["top250"]

        if imdbNumber == "":
            log("%(label)s: IMDb id is missing" % movie)
            return None

        if imdbNumber in self.top250:
            newPosition = self.top250[imdbNumber]["position"]
            del self.top250[imdbNumber]

            if oldPosition == newPosition:
                logDebug("%(label)s: up to date" % movie)
                return None

            self.updateMovie(movie, newPosition)

            if oldPosition == 0:
                log("%s: added at position %s" % (movie["label"], newPosition))
                return "added"

            log("%s: updated from %s to %s" % (movie["label"], oldPosition, newPosition))
            return "updated"

        if oldPosition != 0:
            log("%(label)s: was removed because no more in IMDb Top250" % movie)
            self.updateMovie(movie, 0)
            return "removed"
    
    def updateMovie(self, movie, position):
        executeJSON('VideoLibrary.SetMovieDetails', {'movieid': movie['movieid'], 'top250': position})