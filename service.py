import xbmc

from resources.lib.main_monitor import MainMonitor
from resources.lib.utils import log_message


def main() -> None:
    monitor = MainMonitor()

    log_message("Starting HTTP Scrobbler", level=xbmc.LOGINFO)

    monitor.waitForAbort()

    log_message("Stopping HTTP Scrobbler", level=xbmc.LOGINFO)

    monitor.player_monitor.onAbortRequested()


if __name__ == '__main__':
    main()
