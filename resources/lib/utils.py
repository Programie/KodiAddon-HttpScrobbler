import json

import xbmc


def jsonrpc_request(method: str, params=None):
    request = {
        "jsonrpc": "2.0",
        "method": method,
        "id": 1
    }

    if params is not None:
        request["params"] = params

    request_json = json.dumps(request)

    xbmc.log("Sending JSON-RPC request: {}".format(request_json), level=xbmc.LOGDEBUG)
    response_json = xbmc.executeJSONRPC(request_json)
    xbmc.log("Response from JSON-RPC request: {}".format(response_json), level=xbmc.LOGDEBUG)

    return json.loads(response_json).get("result", {})


def fix_unique_ids(video_info: dict):
    unique_ids = video_info.get("uniqueid", {})

    if len(unique_ids.keys()) == 1:
        unique_id = unique_ids.get("unknown")

        # unique_ids only contains the "unknown" property
        if unique_id is not None and unique_id != "":
            media_type = video_info.get("type")
            if media_type == "episode":
                unique_ids["tvdb"] = unique_id
            elif media_type == "movie":
                unique_ids["tmdb"] = unique_id

            # Remove "unknown" property
            del unique_ids["unknown"]

    return unique_ids
