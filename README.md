![](https://raw.githubusercontent.com/Jandalf/script.imdbupdate/master/script.imdbupdate/icon.png)

##Movie Ratings + Top250 + MPAA

This addon updates the ratings of your movies and the Top250 position from IMDb.

#####Attention:
the script gets the ratings from http://omdbapi.com which are only updated once a week, so the votes can differ sometimes.

Bug reports and feature requests are very appreciated.

#####Features:
- update the movie rating and vote count (only if something changed)
- update the IMDb Top250 movies
- update the MPAA rating for movies (US / DE)
- write missing Top250 movies to the [addon_data](http://kodi.wiki/view/Userdata) folder 
- update only movies with more than 0.1% vote increase (much faster)
- run in background
- run periodically
- start parameters for skinners (see below)
- resume movie rating update if it was cancelled
- simple GUI to select what should be updated
- progress bar

#####For Skinners:
Create a button with the function:
```
RunScript( script.imdbupdate, movies [,hidden] )
RunScript( script.imdbupdate, top250 [,hidden] )
RunScript( script.imdbupdate, mpaa [,hidden] )
RunScript( script.imdbupdate, all [,hidden] )
```

#####ToDo:
- [ ] better settings explanation
- [ ] update rating of TV Shows (hard thing)
- [ ] ask for a rating after watching a movie
- [ ] code comments
