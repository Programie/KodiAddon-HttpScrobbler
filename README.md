# HTTP Scrobbler for Kodi

This addon for Kodi provides a simple scrobbler sending requests for movies and episodes to any HTTP endpoint. The data is sent as JSON using a POST request.

Work on a [backend for this addon](https://github.com/Programie/Tracky) is currently in progress.

## Installation

Just [download this repository](https://github.com/Programie/KodiAddon-HttpScrobbler/archive/refs/heads/main.zip) as zip archive and install it in Kodi using "Install from zip file" in the add-on browser (Settings > Addons). NOTE requires "Enable Unknown Sources" to be enabled first.

After that, configure the backend, username and password in the Addon settings.

## Data structure

The following examples provide the usual structure which will be used for sending the data to the endpoint.

Not all of those properties might be set in every request as they might not be available for the media content being played back.

**Movies**

```json
{
  "event": "start",
  "dbId": 123,
  "title": "Back to the Future",
  "mediaType": "movie",
  "year": 1985,
  "premiered": "",
  "uniqueIds": {
    "imdb": "tt0088763"
  },
  "duration": 6960,
  "progress": {
    "time": 0,
    "percent": 0.0
  }
}
```

**Episodes**

```json
{
  "event": "start",
  "dbId": 1234,
  "title": "Member Berries",
  "mediaType": "episode",
  "year": 2016,
  "uniqueIds": {
    "tvdb": "75897"
  },
  "duration": 1330,
  "progress": {
    "time": 0,
    "percent": 0.0
  },
  "tvShowTitle": "South Park",
  "season": 20,
  "episode": 1,
  "firstAired": "2016-09-14"
}
```
