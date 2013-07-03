################
# IMDB Update  #
# by Jandalf   #
################

from resources.lib.top250 import Top250
from resources.lib.movies import Movies
from resources.lib.util import *
import sys

def gui():
    stop = False
    while not(stop):
        choice = dialogSelect(addOnVersion, [l("Top250"), l("Movies"), l("Exit")])
        if choice == 0:
            stop = Top250().start()
        elif choice == 1:
            stop = Movies().start()
        else:
            break

if __name__ == "__main__":
    log("Starting %s v%s" % (addOnName , addOnVersion))
    createAddOnDir()
    
    count = len(sys.argv) - 1
 
    if count == 1:
        arg = sys.argv[1].lower()
        if arg == "top250":
            Top250().start()
        elif arg == "movies":
            Movies().start()
        else:
            xbmcgui.Dialog().ok("Status","wrong argument")
            gui()
    elif count > 1:
        xbmcgui.Dialog().ok("Status","too much arguments")
        gui()
    else:
        gui()