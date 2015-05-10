################
# IMDB Update  #
# by Jandalf   #
################

from resources.lib.top250 import Top250
from resources.lib.movies import Movies
from resources.lib.mpaa import Mpaa
from resources.lib.util import *
import sys
import time

def gui():
    stop = False
    while not(stop):
        choice = dialogSelect(addOnVersion, [l("Top250"), l("Movies"), l("MPAA_Update"), l("Show_Top250"), l("Exit")])
        if choice == 0:
            stop = Top250().start()
        elif choice == 1:
            stop = Movies().start()
        elif choice == 2:
            stop = Mpaa().start()
        elif choice == 3:
            xbmc.executebuiltin('XBMC.ActivateWindow(10025,special://home/addons/script.imdbupdate/resources/Top250.xsp,return)')
            break
        else:
            break

if __name__ == "__main__":
    log("Starting %s v%s" % (addOnName , addOnVersion))
    createAddOnDir()
    
    args = sys.argv
    count = len(args) - 1
 
    if count == 1 or count == 2:
        if count == 2:
            hidden = args[2].lower() == "hidden"
        else:
            hidden = False

        for typ in args[1].lower().split("|"):
            if typ == "top250":
                Top250().start(hidden)
            elif typ == "movies":
                Movies().start(hidden)
            elif typ == "mpaa":
                Mpaa().start(hidden)
            elif typ == "all":
                Top250().start(hidden)
                time.sleep(10)
                Movies().start(hidden)
                time.sleep(10)
                Mpaa().start(hidden)
            else:
                xbmcgui.Dialog().ok("Status","wrong argument")
                gui()
        
    elif count > 2:
        xbmcgui.Dialog().ok("Status","too much arguments")
        gui()
    else:
        gui()