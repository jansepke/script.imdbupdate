################
# IMDB Update  #
# by Jandalf   #
################

from resources.lib.util import *
import time, datetime

def shouldRun(name):
    try:
        fileContent = readF("last_run_" + name)
        logDebug("Content of last_run_%s: %s" % (name, fileContent))
        structTime  = time.strptime(fileContent, '%Y-%m-%d')
        lastRun = datetime.datetime(*structTime[:6])
        logDebug("Parsed date: %s" % (lastRun))
        now = datetime.datetime.today()
        logDebug("Now: %s" % (now))
        result = now >= (lastRun + datetime.timedelta(7))
    except (IOError, ValueError, TypeError) as e:
       	log("Error while reading file last_run_%s: %s" % (name, str(e)))
        result = True
    return result

while (not abortRequested()):
    time.sleep(10)
    if settingBool("deamonTop250") and shouldRun("top250"):
        xbmc.executebuiltin("RunScript(script.imdbupdate,top250,hidden)")
    if settingBool("deamonMovies") and shouldRun("movies"):
        time.sleep(10)
        xbmc.executebuiltin("RunScript(script.imdbupdate,movies,hidden)")
    if settingBool("deamonMpaa") and shouldRun("mpaa"):
        time.sleep(10)
        xbmc.executebuiltin("RunScript(script.imdbupdate,mpaa,hidden)")
    for i in range(720):
        if abortRequested():
            break
        time.sleep(5)
