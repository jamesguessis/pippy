import json
import re

import requests


def beatmap_data(bm, key):
    url = 'https://osu.ppy.sh/api/get_beatmaps?k=' + key + '&' + bm
    jsonurl = requests.get(url)
    # enc = jsonurl.headers.get_content_charset()
    text = jsonurl.content.decode()
    jstring = text.strip("[]")
    new = jstring.split("},")
    if len(new) > 1:
        jstring = new[0] + "}"
    json_string = json.loads(jstring)
    b_id = "b=" + json_string['beatmap_id']
    return b_id


def main(url, key):
    try:
        p = re.compile(".*osu.ppy.sh/s/|.*osu.ppy.sh/b/|\?.*")
        a = p.subn('', url)
        bs = re.compile(".*osu.ppy.sh/|/.*")
        c = bs.subn('', url)
        comp = c[0] + "=" + a[0]
        if c[0] == 's' or c[0] == 'b':
            url = "http://osu.ppy.sh/osu/" + beatmap_data(comp, key)[2:]
            return url
        else:
            raise Exception('invalid url')
    except Exception as ex:
        raise
