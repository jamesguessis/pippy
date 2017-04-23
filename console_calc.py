import argparse
import os

import requests

from pippy.beatmap import Beatmap
from pippy.pp import calculate_pp, Mods, calculate_pp_by_acc

from pippy import diff

parser = argparse.ArgumentParser()
parser.add_argument('file', help='File or url. If url provided use -link flag', )
parser.add_argument('-link', help='Flag if url provided', action='store_true')
parser.add_argument('-acc', help='Accuracy percentage', metavar="acc%",
                    default=0, type=float)
parser.add_argument('-c100', help='Number of 100s',
                    metavar="100s", default=0, type=int)
parser.add_argument('-c50', help='Number of 50s', metavar="50s",
                    default=0, type=int)
parser.add_argument('-m', help='Number of misses', metavar="miss",
                    default=0, dest='misses', type=int)
parser.add_argument('-c', help='Max combo', metavar="combo", default=0,
                    dest='combo', type=int)
parser.add_argument('-sv', help='Score version 1 or 2', metavar="sv",
                    dest='score_ver', default=1, type=int)
parser.add_argument('-mods', help='Mod string eg. HDDT', metavar="mods", default="")
parser.add_argument('-completion', help='This gives you percentage of completion for failed plays', metavar='complete', type=int, default=0)

args = parser.parse_args()
c100 = args.c100
c50 = args.c50
misses = args.misses
combo = args.combo
acc = args.acc
score_ver = args.score_ver
mod_s = args.mods
web_beatmap = args.link
file_name = args.file
complete = args.completion
if web_beatmap:
    beatmap_id = file_name.rsplit("/", 1)[1]
    data = requests.get("https://osu.ppy.sh/osu/{}"
                        .format(beatmap_id)).content.decode('utf8')
else:
    data = open(file_name, 'r').read()

btmap = Beatmap(data)
good = btmap.parse()
if not good:
    raise ValueError("Beatmap verify failed. "
                     "Either beatmap is not for osu! standart, or it's malformed")
if not combo or combo > btmap.max_combo:
    combo = btmap.max_combo

mods = Mods(mod_s)
btmap.apply_mods(mods)
aim, speed, stars, btmap = diff.main(btmap)
if not acc:
    pp = calculate_pp(aim, speed, btmap, misses, c100, c50, mods, combo, score_ver)
else:
    pp = calculate_pp_by_acc(aim, speed, btmap, acc, mods, combo, misses, score_ver)


# This lets me calculate the map completion percentage because I want it to
if not complete == 0:
    hitobj = []
    numobj = complete
    num = len(btmap.hit_objects)
    if numobj > num:
        numobj = num
    for objects in btmap.hit_objects:
        hitobj.append(objects.time)
    timing = int(hitobj[num - 1]) - int(hitobj[0])
    point = int(hitobj[numobj - 1]) - int(hitobj[0])
    completion = point / timing
else:
    completion = 100


pippy_output = {
    "map": btmap.title,
    "artist": btmap.artist,
    "title": btmap.title,
    "creator": btmap.creator,
    "mods_str": mod_s,
    "ar": btmap.ar,
    "od": btmap.od,
    "hp": btmap.hp,
    "cs": btmap.cs,
    "num_circles": btmap.num_circles,
    "num_sliders": btmap.num_sliders,
    "num_spinners": btmap.num_spinners,
    "num_objects": btmap.num_objects,
    "stars": round(stars, 2),
    "acc": round(pp.acc_percent, 2),
    "combo": combo,
    "max_combo": btmap.max_combo,
    "misses": misses,
    "pp": float("{:.2f}".format(pp.pp)),
    "map_completion": float("{:.2f}".format(completion))
}


print(pippy_output)