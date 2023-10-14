import xbmc

from resources.lib.player_monitor import PlayerMonitor


def main():
    monitor = xbmc.Monitor()
    player_monitor = PlayerMonitor()

    xbmc.log("Starting HTTP Scrobbler", level=xbmc.LOGINFO)

    monitor.waitForAbort()

    xbmc.log("Stopping HTTP Scrobbler", level=xbmc.LOGINFO)


if __name__ == '__main__':
    main()
