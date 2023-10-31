import json

import requests
import xbmc
import xbmcaddon
import xbmcgui

from requests.auth import HTTPBasicAuth

from resources.lib.utils import jsonrpc_request, fix_unique_ids


class PlayerMonitor(xbmc.Player):
    def __init__(self):
        super().__init__()

        self.video_info = {}

    def show_message(self, message: str):
        xbmcgui.Dialog().ok("HTTP Scrobbler", message)

    def build_payload(self):
        if not self.video_info:
            return None

        full_data = {
            "dbId": self.video_info.get("id"),
            "title": self.video_info.get("label"),
            "mediaType": self.video_info.get("type"),
            "year": self.video_info.get("year"),
            "uniqueIds": fix_unique_ids(self.video_info.get("uniqueid", {}), self.video_info.get("type"))
        }

        if full_data["mediaType"] == "episode":
            full_data = full_data | {
                "tvShowTitle": self.video_info.get("showtitle"),
                "season": self.video_info.get("season"),
                "episode": self.video_info.get("episode"),
                "firstAired": self.video_info.get("firstaired"),
                "uniqueIds": fix_unique_ids(self.video_info.get("tvshow", {}).get("uniqueid", {}), self.video_info.get("type"))
            }
        elif full_data["mediaType"] == "movie":
            full_data = full_data | {
                "premiered": self.video_info.get("premiered")
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

        try:
            response = requests.post(url, json=json_data, auth=auth)
            response.raise_for_status()
        except Exception as exception:
            xbmc.log("Request failed for URL {}: {}".format(url, str(exception)), level=xbmc.LOGERROR)
            self.show_message("HTTP request failed!")

    def fetch_video_info(self):
        try:
            self.video_info = jsonrpc_request("Player.GetItem", {"playerid": 1, "properties": ["tvshowid", "showtitle", "season", "episode", "firstaired", "premiered", "year", "uniqueid"]}).get("item")
        except:
            self.video_info = None

        if not self.video_info:
            return

        if self.video_info.get("type") == "episode":
            self.video_info["tvshow"] = jsonrpc_request("VideoLibrary.GetTVShowDetails", {"tvshowid": self.video_info.get("tvshowid"), "properties": ["uniqueid"]}).get("tvshowdetails")

    def onAVStarted(self):
        self.fetch_video_info()

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
