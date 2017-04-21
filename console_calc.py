import argparse
import os

import requests

from pippy.parser.beatmap import Beatmap
from pippy.pp.counter import calculate_pp, Mods, calculate_pp_by_acc

from pippy import diff

parser = argparse.ArgumentParser()
parser.add_argument('file', help='File or url. If url provided use -l flag', )
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
aim, speed, stars, btmap = diff.counter.main(btmap)
if not acc:
    pp = calculate_pp(aim, speed, btmap, misses, c100, c50, mods, combo, score_ver)
else:
    pp = calculate_pp_by_acc(aim, speed, btmap, acc, mods, combo, misses, score_ver)

pippy_output = {}
pippy_output["map"] = btmap.title
pippy_output["artist"] = btmap.artist
pippy_output["title"] = btmap.title
pippy_output["creator"] = btmap.creator
pippy_output["mods_str"] = mod_s
pippy_output["ar"] = btmap.ar
pippy_output["od"] = btmap.od
pippy_output["hp"] = btmap.hp
pippy_output["num_circles"] = btmap.num_circles
pippy_output["num_sliders"] = btmap.num_sliders
pippy_output["num_spinners"] = btmap.num_spinners
pippy_output["num_objects"] = btmap.num_objects
pippy_output["stars"] = round(stars, 2)
pippy_output["acc"] = "{}".format(round(pp.acc_percent, 2))
pippy_output["combo"] = combo
pippy_output["max_combo"] = btmap.max_combo
pippy_output["misses"] = misses
pippy_output["pp"] = pp.pp

print(pippy_output)