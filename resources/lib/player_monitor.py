import json

import requests
import xbmc
import xbmcaddon
import xbmcgui

from requests.auth import HTTPBasicAuth


class PlayerMonitor(xbmc.Player):
    def __init__(self):
        super().__init__()

        self.video_info: xbmc.InfoTagVideo | None = None

    def show_message(self, message: str):
        xbmcgui.Dialog().ok("HTTP Scrobbler", message)

    def build_payload(self):
        if not self.video_info:
            return None

        full_data = {
            "dbId": self.video_info.getDbId(),
            "title": self.video_info.getTitle(),
            "mediaType": self.video_info.getMediaType(),
            "imdbId": self.video_info.getIMDBNumber(),
            "year": self.video_info.getYear(),
            "originalTitle": self.video_info.getOriginalTitle()
        }

        if full_data["mediaType"] == "episode":
            full_data = full_data | {
                "tvShowTitle": self.video_info.getTVShowTitle(),
                "season": self.video_info.getSeason(),
                "episode": self.video_info.getEpisode(),
                "firstAired": self.video_info.getFirstAiredAsW3C()
            }

        return full_data

    def send_request(self, event: str):
        json_data = {"event": event} | self.build_payload()

        url = xbmcaddon.Addon().getSetting("url")
        if not url:
            xbmc.log("HTTP Scrobbler URL not configured!", level=xbmc.LOGERROR)
            self.show_message("HTTP Scrobbler URL not configured!")
            return

        username = xbmcaddon.Addon().getSetting("username")
        password = xbmcaddon.Addon().getSetting("password")

        if username or password:
            auth = HTTPBasicAuth(username, password)
        else:
            auth = None

        xbmc.log("Sending data to URL {}: {}".format(url, json.dumps(json_data)), level=xbmc.LOGINFO)

        response = requests.post(url, json=json_data, auth=auth)
        if not response.ok:
            xbmc.log("Request failed for URL {}: {}".format(response.url, response.reason), level=xbmc.LOGERROR)
            self.show_message("HTTP request failed!")

    def onAVStarted(self):
        try:
            self.video_info = self.getVideoInfoTag()
        except:
            self.video_info = None

        if not self.video_info:
            return

        self.send_request("start")

    def onPlayBackPaused(self):
        if not self.video_info:
            return

        self.send_request("pause")

    def onPlayBackResumed(self):
        if not self.video_info:
            return

        self.send_request("resume")

    def onPlayBackStopped(self):
        if not self.video_info:
            return

        self.send_request("stop")

    def onPlayBackEnded(self):
        if not self.video_info:
            return

        self.send_request("end")
