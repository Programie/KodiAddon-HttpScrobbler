import xbmc

from resources.lib.player_monitor import PlayerMonitor


class MainMonitor(xbmc.Monitor):
    def __init__(self) -> None:
        super().__init__()

        self.player_monitor = PlayerMonitor()

    def onSettingsChanged(self) -> None:
        self.player_monitor.load_settings()
