import json

import requests
import xbmc
import xbmcaddon
import xbmcgui

from requests.auth import HTTPBasicAuth

from resources.lib.timer import Timer
from resources.lib.utils import jsonrpc_request, fix_unique_ids


class PlayerMonitor(xbmc.Player):
    def __init__(self):
        super().__init__()

        self.settings = None
        self.interval_timer = None

        self.video_info = {}

        self.load_settings()

    def show_message(self, message: str):
        xbmcgui.Dialog().ok("HTTP Scrobbler", message)

    def load_settings(self):
        self.settings = xbmcaddon.Addon().getSettings()

    def build_payload(self, event: str):
        if not self.video_info:
            return None

        total_time = self.getTotalTime() if self.isPlaying() else None
        current_time = self.getTime() if self.isPlaying() else None

        if total_time is not None:
            if total_time < 0:
                total_time = 0
            else:
                total_time = int(total_time)

        if current_time is not None:
            if current_time < 0:
                current_time = 0
            else:
                current_time = int(current_time)

        if total_time and current_time is not None:
            progress_percent = (current_time / total_time) * 100
        else:
            progress_percent = None

        full_data = {
            "event": event,
            "dbId": self.video_info.get("id"),
            "title": self.video_info.get("label"),
            "mediaType": self.video_info.get("type"),
            "year": self.video_info.get("year"),
            "uniqueIds": fix_unique_ids(self.video_info.get("uniqueid", {}), self.video_info.get("type")),
            "duration": total_time,
            "progress": {
                "time": current_time,
                "percent": progress_percent
            }
        }

        if full_data["mediaType"] == "episode":
            full_data = {
                **full_data,
                "tvShowTitle": self.video_info.get("showtitle"),
                "season": self.video_info.get("season"),
                "episode": self.video_info.get("episode"),
                "firstAired": self.video_info.get("firstaired"),
                "uniqueIds": fix_unique_ids(self.video_info.get("tvshow", {}).get("uniqueid", {}), self.video_info.get("type"))
            }
        elif full_data["mediaType"] == "movie":
            full_data = {
                **full_data,
                "premiered": self.video_info.get("premiered")
            }

        return full_data

    def send_request(self, event: str):
        json_data = self.build_payload(event)

        url = self.settings.getString("url")
        if not url:
            xbmc.log("HTTP Scrobbler URL not configured!", level=xbmc.LOGERROR)
            self.show_message("HTTP Scrobbler URL not configured!")
            return

        username = self.settings.getString("username")
        password = self.settings.getString("password")

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

    def start_interval_timer(self):
        if not self.settings.getBool("useInterval"):
            return

        self.interval_timer = Timer(self.settings.getInt("interval"), self.onInterval)
        self.interval_timer.start()

    def stop_interval_timer(self):
        if not self.interval_timer or not self.interval_timer.is_alive():
            return

        self.interval_timer.stop()

    def onAVStarted(self):
        self.fetch_video_info()

        self.send_request("start")
        self.start_interval_timer()

    def onPlayBackPaused(self):
        if not self.video_info:
            return

        self.send_request("pause")
        self.stop_interval_timer()

    def onPlayBackResumed(self):
        if not self.video_info:
            return

        self.send_request("resume")
        self.start_interval_timer()

    def onPlayBackStopped(self):
        if not self.video_info:
            return

        self.send_request("stop")
        self.stop_interval_timer()

    def onPlayBackEnded(self):
        if not self.video_info:
            return

        self.send_request("end")
        self.stop_interval_timer()

    def onInterval(self):
        if not self.video_info:
            return

        self.send_request("interval")
