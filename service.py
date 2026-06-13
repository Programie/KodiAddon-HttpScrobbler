import xbmc

from resources.lib.main_monitor import MainMonitor


def main() -> None:
    monitor = MainMonitor()

    xbmc.log("Starting HTTP Scrobbler", level=xbmc.LOGINFO)

    monitor.waitForAbort()

    xbmc.log("Stopping HTTP Scrobbler", level=xbmc.LOGINFO)

    monitor.player_monitor.onAbortRequested()


if __name__ == '__main__':
    main()
