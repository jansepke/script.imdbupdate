################
# IMDB Update  #
# by Jandalf   #
################

import urllib2, re
from BeautifulSoup import BeautifulSoup
from util import *

class Top250:
    def __init__(self):
        self.progress = dialogProgress()
        self.progress.update(0, l("Importing_current_IMDb_Top250"))
        self.top250 = self.getTop250()
        if self.top250 == {}:
           dialogOk(l("Top250"), l("There_was_a_problem_with_the_IMDb_site!"))
        else:
            movies = self.getMovies()
            total = len(movies)
            if total > 0:
                self.startProcess(movies, total)
            else:
                dialogOk(l("Info"), l("The_video_library_is_empty_or_the_IMDb_id_doesn't_exist!"))
    
    def getTop250(self):
        top250 = {}
        opener = urllib2.build_opener()
        opener.addheaders = [("User-agent", "Mozilla/5.0")]
        response = opener.open("http://www.imdb.com/chart/top")
        if response.getcode() == 200:
            soup = BeautifulSoup(response)
            top250 = [tt["href"][7:-1].encode('utf-8') for tt in soup.findAll(href=re.compile("/title/tt")) if tt.parent.parent.parent.name == "tr"]
            if len(top250) != 250:
                top250 = {}
            else:
                top250 = dict([(val, key + 1) for key, val in enumerate(top250)])
        return top250
    
    def getMovies(self):
        movies = executeJSON("VideoLibrary.GetMovies", '{"properties" : ["imdbnumber", "top250"], "sort": { "order": "ascending", "method": "label", "ignorearticle": true }}')
        return movies["result"]["movies"]
            
    def startProcess(self, movies, total):
        stats = {"added": 0, "updated": 0, "removed": 0}
        for count, movie in enumerate(movies):
            if self.progress.iscanceled():
                self.progress.close()
                dialogOk(l("Abort"), l("The_scraping_was_canceled_by_user!"))
                break
            else:
                self.progress.update((count * 100) // total, "%s %s" % (l("Searching_for"), movie["label"]))
                result = self.checkMovie(movie)
                if result != "":
                    stats[result] += 1
        dialogOk(l("Completed"), l("Movies_IMDb_Top250_summary"), "%s %s" % (stats["updated"], l("were_updated")), "%s %s %s %s" % (stats["added"], l("were_added_and"), stats["removed"], l("were_removed!")))

    def checkMovie(self, movie):
        imdbNumber = movie["imdbnumber"]
        oldPosition = movie["top250"]
        result = ""
        if imdbNumber == "":
            log("%s: %s" % (movie["label"], l("IMDb_id_was_not_found_in_your_database!")))
        elif imdbNumber in self.top250:
            newPosition = self.top250[imdbNumber]
            if oldPosition != newPosition:
                self.updateMovie(movie, newPosition)
                if oldPosition == 0:
                    log("%s: %s %s!" % (movie["label"], l("was_added_because_now_is_in_IMDb_Top250_at_position"), newPosition))
                    result = "added"
                else:
                    log("%s: %s %s, %s %s!" % (movie["label"], l("the_old_position_in_your_DB_was"), oldPosition, l("the_new_position_from_IMDb_Top250_is"), newPosition))
                    result = "updated"
            else: log("%s: %s" % (movie["label"], l("Nothing_to_do_has_already_been_updated!")))
            del self.top250[imdbNumber]
        elif oldPosition != 0:
            log("%s: %s" % (movie["label"], l("was_removed_because_no_more_in_IMDb_Top250!")))
            self.updateMovie(movie, 0)
            result = "removed"
        return result
    
    def updateMovie(self, movie, position):
        executeJSON("VideoLibrary.SetMovieDetails", '{"movieid":%s,"top250":%s}' % (movie["movieid"], position))
