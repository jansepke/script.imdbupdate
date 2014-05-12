#IMDB-Update

This addon updates the ratings of your movies and the Top250 position from IMDb.

#####Attention:
the script gets the ratings from http://omdbapi.com which are only updated once a week, so the votes can differ sometimes.

Bug reports and feature requests are very appreciated.

#####Features:
 - update the movie rating and vote count (only if something changed)
 - update the IMDB Top250 movies
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
```
