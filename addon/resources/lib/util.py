################
# IMDB Update  #
# by Jandalf   #
################

import xbmc, xbmcaddon, xbmcgui, xbmcvfs, urllib2, socket, csv
import os, datetime, json, subprocess

addOn = xbmcaddon.Addon("script.imdbupdate")
addOnName = addOn.getAddonInfo("name")
addOnVersion = addOn.getAddonInfo("version")
addOnProfile = xbmc.translatePath(addOn.getAddonInfo("profile"))
addOnPath = xbmc.translatePath(addOn.getAddonInfo("path"))
addOnIcon = os.path.join(addOnPath, "icon.png")

STRINGS = {
    "Never_Checked!": 30200,
    "Edit_IMDb_id": 30171,
    "Updating_old_IMDb_Top250": 30149,
    "the_new_position_from_IMDb_Top250_is": 30148,
    "Look_xbmc.log_file_to_see_what_has_been_done!": 30169,
    "were_updated": 30153,
    "Check_the_ratings_of_all_your_tv_shows!": 30167,
    "Started_updating_movies_ratings": 30180,
    "Importing_current_IMDb_Top250": 30143,
    "No_Top250_information_available!": 30142,
    "The_video_library_is_empty_or_the_IMDb_id_doesn't_exist!": 30141,
    "Movies_IMDb_Top250_summary": 30140,
    "the_old_position_in_your_DB_was": 30147,
    "was_added_because_now_is_in_IMDb_Top250_at_position": 30146,
    "The_scraping_was_canceled_by_user!": 30145,
    "Abort": 30144,
    "This_check_is_disabled_in_the_add-on_settings!": 30170,
    "Path_for_missing_TOP250_txt_file": 30201,
    "Do_you_want_to_update_all_your_TV_Shows_(no_episodes)_ratings?": 30174,
    "of": 30183,
    "Edit_the_IMDb_id_of_your_tv_shows!": 30168,
    "Are_you_sure_to_want_delete_all_IMDb_id?": 30132,
    "Started_updating_tv_shows_ratings": 30181,
    "All_IMDb_id_have_been_deleted!": 30133,
    "Searching_for": 30150,
    "Complete": 30198,
    "on_a_total_of": 30156,
    "movies!": 30157,
    "There_was_a_problem_with_the_IMDb_site!": 30118,
    "IMDb_id_was_not_found_in_your_database!": 30119,
    "Delete_all_IMDd_id_...": 30130,
    "Which_to_restore?_(back_to_skip)": 30131,
    "Everything_has_been_done!_Click_OK_and_exit!": 30136,
    "IMDb_id_has_been_deleted!_Now_is_ready_for_a_new_scraping!": 30137,
    "Click_OK_and_exit!": 30134,
    "Completed": 30135,
    "Activate_scraping_for_TV_Shows": 30110,
    "Edit": 30111,
    "View_tv_shows_list_to_delete_individual_IMDb_id_and_reassign_during_new_scraping": 30112,
    "This_may_take_a_while_depends_on_the_amount_of_data!": 30139,
    "There_was_a_problem_with_XBMC_database!": 30158,
    "Error": 30115,
    "Nothing_to_do_has_already_been_updated!": 30116,
    "Nothing_to_do_the_current_rating_is_zero!": 30117,
    "Current_TV_Show:_": 30161,
    "Check_the_ratings_of_all_your_movies!": 30166,
    "Proceed": 30127,
    "Movies_ratings_summary": 30178,
    "You_can_resume_from_where_it_was_interrupted!": 30179,
    "The_previous_scraping_was_interrupted!": 30176,
    "was_removed_because_no_more_in_IMDb_Top250!": 30151,
    "Check_the_Top250_list_of_all_your_movies!": 30165,
    "Exit": 30126,
    "Exit": 30172,
    "Do_you_want_to_update_all_your_movies_ratings?": 30173,
    "were_removed!": 30155,
    "This_TV_Show_was_skipped!": 30160,
    "The_video_library_is_empty..._nothing_to_do!": 30129,
    "Which_is_correct?_(back_to_skip)": 30163,
    "TV_Shows_ratings_summary": 30182,
    "Info": 30128,
    "Incomplete": 30199,
    "The_first_launch_could_ask_you_to_choose_the_correct_TV_Show!": 30175,
    "If_not_in_list_start_virtual_keyboard_...": 30162,
    "Do_you_want_to_update_IMDb_Top250?": 30138,
    "Now_your_movies_in_the_IMDb_Top250_are": 30152,
    "voters_and_set_IMDb_id_to": 30164,
    "were_added_and": 30154,
    "Do_you_want_to_resume?": 30177,
    "was_skipped!": 30159,
    "with": 30121,
    "was_updated_to": 30120,
    "New_rating_is": 30123,
    "voters!": 30122,
    "Select_a_TV_Show_from_the_list_to_delete_the_IMDb_id!": 30125,
    "Edit_TV_Shows_procedure_has_been_activated!": 30124,
    "Activate_scraping_for_Movies": 30109,
    "Activate_scraping_for_Top250": 30108,
    "Don't_ask_any_confirmation_run_immediately_(First_time_it's_advisable_to_have_both_disabled)": 30107,
    "Use_the_new_GUI_instead_of_the_old_sequential_method": 30106,
    "Hide_progress_dialog_(notifications_will_be_used_if_activated)": 30105,
    "Don't_ask_any_confirmation_run_immediately": 30104,
    "TV_Shows": 30103,
    "Movies": 30102,
    "Top250": 30101,
    "Show_Top250": 30202,
    "MPAA_Update": 30203,
    "Choose_your_MPAA_system": 30204
}

'''Abort request'''
def abortRequested():
    return xbmc.abortRequested

'''Settings'''
def setting(name, newValue = None):
    if newValue is not None:
        addOn.setSetting(name, newValue)
    else:
        return addOn.getSetting(name)

def settingBool(name, newValue = None):
    if newValue is not None:
        addOn.setSetting(name, str(newValue).lower())
    else:
        return setting(name) == "true"

'''Log'''
def log(msg):
    xbmc.log("[%s] - %s" % (addOnName, msg.encode('utf-8')))

'''Log Debug'''
def logDebug(msg):
    xbmc.log("[%s] - %s" % (addOnName, msg.encode('utf-8')), level=xbmc.LOGDEBUG)

'''Language String'''
def l(string_id):
    if string_id in STRINGS:
        return addOn.getLocalizedString(STRINGS[string_id])
    else:
        log('String is missing: %s' % string_id)
        return string_id

'''GUI'''
def notification(msg):
    xbmc.executebuiltin("Notification(%s,%s,5000,%s)" % (addOnName, msg.encode('utf-8'), addOnIcon))

def dialogOk(a, b="", c="", d=""):
    return xbmcgui.Dialog().ok("%s - %s" % (addOnName, a), b, c, d)

def dialogYN(a="", b="", c=""):
    return xbmcgui.Dialog().yesno(addOnName, a, b, c)

def dialogProgress():
    result = xbmcgui.DialogProgress()
    result.create(addOnName)
    return result

def dialogSelect(heading, choices):
    return xbmcgui.Dialog().select("%s %s" % (addOnName, heading), choices)

'''JSON'''
def getMoviesWith(*fields):
    params = {'properties':fields, 'sort':{'order':'ascending', 'method':'label', 'ignorearticle':True }}
    movies = executeJSON('VideoLibrary.GetMovies', params)
    return movies["result"]["movies"]

def executeJSON(method, params):
    data = json.dumps({'jsonrpc':'2.0', 'method':method, 'params':params, 'id':1})
    result = json.loads(xbmc.executeJSONRPC(data))
    if "error" in result:
        log("method: " + method + "params: " + str(params) + " throws: " + str(result["error"]))
        result = []
    return result

'''Write last run date'''
def writeDate(name):
    writeF("last_run_" + name, datetime.date.today())

'''File system'''
def createAddOnDir():
    if not(xbmcvfs.exists(addOnProfile)):
        xbmcvfs.mkdir(addOnProfile)

def readF(name):
    return file(os.path.join(addOnProfile, name), "r").read()
    
def writeF(name, data):
    file(os.path.join(addOnProfile, name), "w").write(str(data))

def writeCSV(name, data):
    try:
        with open(os.path.join(addOnProfile, name), 'wb') as fp:
            a = csv.writer(fp, delimiter=';')
            a.writerows(data)
    except IOError:
        log("Could not write file " + name)

def openFile(name):
    subprocess.Popen(os.path.join(addOnProfile, name), shell=True)
    
def deleteF(name):
    delFile = os.path.join(addOnProfile, str(name))
    if xbmcvfs.exists(delFile):
        xbmcvfs.delete(delFile)

def request(url):
    opener = urllib2.build_opener()
    opener.addheaders = [("User-agent", "Mozilla/5.0")]

    try:
        response = opener.open(url)
        if response.getcode() != 200:
            raise urllib2.HTTPError("Status Code != 200")
    except (urllib2.URLError, urllib2.HTTPError, socket.timeout):
        logDebug("Could not connect to " + url)
        response = None

    return response