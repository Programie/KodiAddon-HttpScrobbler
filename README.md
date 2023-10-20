# HTTP Scrobbler for Kodi

This addon for Kodi provides a simple scrobbler sending requests for movies and episodes to any HTTP endpoint. The data is sent as JSON using a POST request.

Work on a [backend for this addon](https://github.com/Programie/Tracky) is currently in progress.

## Data structure

The following examples provide the usual structure which will be used for sending the data to the endpoint.

Not all of those properties might be set in every request as they might not be available for the media content being played back. Especially the `originalTitle` property is only set if Kodi shows an alternative title (i.e. if the original one is in a different language).

**Movies**

```json
{
  "dbId": 123,
  "title": "Back to the Future",
  "originalTitle": "",
  "mediaType": "movie",
  "imdbId": "tt0088763",
  "year": 1985
}
```

**Episodes**

```json
{
  "dbId": 1234,
  "title": "Member Berries",
  "originalTitle": "",
  "mediaType": "episode",
  "imdbId": "tt4197088",
  "year": 2016,
  "tvShowTitle": "South Park",
  "season": 20,
  "episode": 1,
  "firstAired": "2016-09-14"
}
```