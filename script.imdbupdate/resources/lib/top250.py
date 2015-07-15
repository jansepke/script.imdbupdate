################
# IMDB Update  #
# by Jandalf   #
################

import re, util
from BeautifulSoup import BeautifulSoup
from util import l

HIDE_TOP250  = util.settingBool("hideTop250")
OPEN_MISSING = util.settingBool("openMissingFile")

class Top250:
    def start(self, hidden=False):
        if hidden:
            global HIDE_TOP250
            HIDE_TOP250 = True

        if HIDE_TOP250:
            util.notification(l("Importing_current_IMDb_Top250"))
        else:
            self.progress = util.dialogProgress()
            self.progress.update(0, l("Importing_current_IMDb_Top250"))

        self.top250 = self.getTop250()
        self.notMissing = set()

        if self.top250 == {}:
            util.dialogOk(l("Top250"), l("There_was_a_problem_with_the_IMDb_site!"))
        else:
            movies = util.getMoviesWith('imdbnumber', 'top250')
            length = len(movies)
            if length > 0:
                self.startProcess(movies, length)
            else:
                util.dialogOk(l("Info"), l("The_video_library_is_empty_or_the_IMDb_id_doesn't_exist!"))

        if not(HIDE_TOP250):
            self.progress.close()

        return HIDE_TOP250

    def getTop250(self):
        response = util.request("http://www.imdb.com/chart/top")
        if response == None:
            return {}

        soup = BeautifulSoup(response).find("tbody", {"class": "lister-list"}).findAll("a", href=re.compile("/title/tt"), title=True)
        top250 = {}
        for idx, tt in enumerate(soup, start=1):
            top250[tt["href"][7:16].encode('utf-8')] = {"position": idx, "label": tt.contents[0], "link": "http://www.imdb.com" + tt["href"]}
            
        return top250 if len(top250) == 250 else {}
            
    def startProcess(self, movies, length):
        stats = {"added": 0, "updated": 0, "removed": 0}

        for count, movie in enumerate(movies):
            if util.abortRequested() or (not(HIDE_TOP250) and self.progress.iscanceled()):
                break

            result = self.checkMovie(movie)
            if result != None:
                stats[result] += 1

            if not(HIDE_TOP250):
                self.progress.update((count * 100) // length, "%s %s" % (l("Searching_for"), movie["label"]))
        else:
            util.writeDate("top250")
            self.createMissingCSV()
            if OPEN_MISSING:
                util.openFile("missingTop250.csv")

        stats["missing"] = len(self.top250)
        util.log("Movies IMDb Top250 summary: updated: %(updated)s, added: %(added)s, removed: %(removed)s, missing: %(missing)s" % stats)

        if HIDE_TOP250:
            util.notification("%s %s" % (l("Completed"), l("Top250")))
        else:
            util.dialogOk(l("Completed"), l("Movies_IMDb_Top250_summary"), "%s %s" % (stats["updated"], l("were_updated")), "%s %s %s %s" % (stats["added"], l("were_added_and"), stats["removed"], l("were_removed!")))

    def checkMovie(self, movie):
        imdbNumber = movie["imdbnumber"]
        oldPosition = movie["top250"]

        if imdbNumber == "":
            util.logWarning("%(label)s: no IMDb id" % movie)
            return None

        if imdbNumber in self.top250:
            newPosition = self.top250[imdbNumber]["position"]
            self.notMissing.add(imdbNumber)

            if oldPosition == newPosition:
                util.logDebug("%(label)s: up to date" % movie)
                return None

            self.updateMovie(movie, newPosition)

            if oldPosition == 0:
                util.log("%s: added at position %s" % (movie["label"], newPosition))
                return "added"

            util.log("%s: updated from %s to %s" % (movie["label"], oldPosition, newPosition))
            return "updated"

        if oldPosition != 0:
            util.log("%(label)s: was removed because no more in IMDb Top250" % movie)
            self.updateMovie(movie, 0)
            return "removed"
    
    def updateMovie(self, movie, position):
        util.executeJSON('VideoLibrary.SetMovieDetails', {'movieid': movie['movieid'], 'top250': position})

    def createMissingCSV(self):
        missing = [[v["position"], k, v["label"], v["link"]] for k,v in self.top250.iteritems() if k not in self.notMissing]
        missing.sort(key=lambda x: x[0])
        missing.insert(0, ["Position", "IMDb ID", "Name", "Link"])
        util.writeCSV("missingTop250.csv", missing)