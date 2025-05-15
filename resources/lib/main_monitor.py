import xbmc

from resources.lib.player_monitor import PlayerMonitor


class MainMonitor(xbmc.Monitor):
    def __init__(self):
        super().__init__()

        self.player_monitor = PlayerMonitor()

    def onSettingsChanged(self):
        self.player_monitor.load_settings()
