################
# IMDB Update  #
# by Jandalf   #
################

from resources.lib.util import *
import time, datetime

def shouldRun(name):
    try:
        lastRun = datetime.datetime.strptime(readF("last_run_" + name), "%Y-%m-%d").date()
        result = datetime.date.today() >= (lastRun + datetime.timedelta(7))
    except TypeError:
        lastRun = datetime(*(time.strptime(readF("last_run_" + name), "%Y-%m-%d")[0:6])).date()
        result = datetime.date.today() >= (lastRun + datetime.timedelta(7))
    except (IOError, ValueError):
        result = True
    return result

while (not abortRequested()):
    time.sleep(10)
    if settingBool("deamonTop250") and shouldRun("top250"):
        xbmc.executebuiltin("RunScript(script.imdbupdate,top250,hidden)")
    if settingBool("deamonMovies") and shouldRun("movies"):
        time.sleep(10)
        xbmc.executebuiltin("RunScript(script.imdbupdate,movies,hidden)")
    for i in range(720):
        if abortRequested():
            break
        time.sleep(5)
