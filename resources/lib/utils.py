import json
import xbmc

from typing import Any


def jsonrpc_request(method: str, params=None) -> Any:
    request = {
        "jsonrpc": "2.0",
        "method": method,
        "id": 1
    }

    if params is not None:
        request["params"] = params

    request_json = json.dumps(request)

    log_message(f"Sending JSON-RPC request: {request_json}", level=xbmc.LOGDEBUG)
    response_json = xbmc.executeJSONRPC(request_json)
    log_message(f"Response from JSON-RPC request: {request_json}", level=xbmc.LOGDEBUG)

    return json.loads(response_json).get("result", {})


def show_message(message: str) -> None:
    jsonrpc_request("GUI.ShowNotification", {"title": "HTTP Scrobbler", "message": message})


def fix_unique_ids(unique_ids: dict, media_type: str) -> dict:
    if len(unique_ids.keys()) == 1:
        unique_id = unique_ids.get("unknown")

        # unique_ids only contains the "unknown" property
        if unique_id is not None and unique_id != "":
            if isinstance(unique_id, str) and unique_id.startswith("tt"):
                # ID starting with "tt" is an IMDb ID
                unique_ids["imdb"] = unique_id
            elif media_type == "episode":
                unique_ids["tvdb"] = unique_id
            elif media_type == "movie":
                unique_ids["tmdb"] = unique_id

            # Remove "unknown" property
            del unique_ids["unknown"]

    return unique_ids


def log_message(message: str, level: int):
    xbmc.log(msg=f"HTTP Scrobbler: {message}", level=level)
