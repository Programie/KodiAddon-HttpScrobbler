# HTTP Scrobbler for Kodi

This addon for Kodi provides a simple scrobbler sending requests for movies and episodes to any HTTP endpoint. The data is sent as JSON using a POST request.

Work on a [backend for this addon](https://github.com/Programie/Tracky) is currently in progress.

## Installation

Just [download this repository](https://github.com/Programie/KodiAddon-HttpScrobbler/archive/refs/heads/main.zip) as zip archive and install it in Kodi using "Install from zip file" in the add-on browser (Settings > Addons). NOTE requires "Enable Unknown Sources" to be enabled first.

After that, configure the backend, username and password in the Addon settings.

## Data sent to the endpoint

The addon sends a HTTP POST request containing a JSON payload.

A request is sent once the playback starts, pauses, resumes or stops.

Additionally to that, it's also possible to regularly send the current progress while playing movies or episodes (i.e. not paused). This feature can be configured on the "Interval" page in the addon settings.

Available values for the `event` property:

| Event    | Description                                                 |
|----------|-------------------------------------------------------------|
| start    | Start playback                                              |
| pause    | Pause playback                                              |
| resume   | Resume playback after pausing it                            |
| stop     | Playback stopped (not finished)                             |
| end      | Playback has finished (not stopped before reaching the end) |
| interval | Triggered while playback in configured interval             |

### Playback progress reporting

The `progress` property is especially useful in combination with the `interval` event as it contains the current playback progress.

There are two properties in the `progress` map:

- `time`: Contains the current playback position in seconds
- `percent`: Contains the current playback progress in percent

Additional to that, the `duration` property in the root contains the total runtime in seconds of the played back media.

**Note:** The duration as well as the progress time and percent information are only available while the playback is active (i.e. not available in the `end` event).

### Data structure

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
