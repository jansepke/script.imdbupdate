################
# IMDB Update  #
# by Jandalf   #
################

from resources.lib.top250 import Top250
from resources.lib.movies import Movies
from resources.lib.util import *
            
if __name__ == "__main__":
    log("Starting %s v%s" % (addOnName , addOnVersion))
    createAddOnDir()
    while True:
        choice = dialogSelect(addOnVersion, [l("Top250"), l("Movies"), l("Exit")])
        if choice == 0:
            Top250()
        elif choice == 1:
            Movies()
        else:
            break