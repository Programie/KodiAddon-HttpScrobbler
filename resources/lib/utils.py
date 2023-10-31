import xbmc


def get_unique_ids(video_info: xbmc.InfoTagVideo):
    ids = {}

    imdb_id = video_info.getIMDBNumber()
    if imdb_id is not None and imdb_id.startswith("tt"):
        ids["imdb"] = imdb_id

    for provider in ("imdb", "tvdb", "tmdb", "anidb"):
        unique_id = video_info.getUniqueID(provider)
        if unique_id is not None and unique_id != "":
            ids[provider] = unique_id

    unique_id = video_info.getUniqueID("unknown")
    if unique_id is not None and unique_id != "":
        media_type = video_info.getMediaType()
        if media_type == "episode":
            ids["tvdb"] = unique_id
        elif media_type == "movie":
            ids["tmdb"] = unique_id

    return ids
