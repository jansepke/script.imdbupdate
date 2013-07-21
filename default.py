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
    
    args = sys.argv
    count = len(args) - 1
 
    if count == 1 or count == 2:
        typ = args[1].lower()
        if count == 2:
            hidden = args[2].lower() == "hidden"
        else:
            hidden = False
        if typ == "top250":
            Top250().start(hidden)
        elif typ == "movies":
            Movies().start(hidden)
        else:
            xbmcgui.Dialog().ok("Status","wrong argument")
            gui()
    elif count > 2:
        xbmcgui.Dialog().ok("Status","too much arguments")
        gui()
    else:
        gui()