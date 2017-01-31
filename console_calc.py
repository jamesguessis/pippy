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

title = "{artist} - {title} [{version}] +{mods} ({creator})".format(
    artist=btmap.artist, title=btmap.title, version=btmap.version,
    mods=mod_s, creator=btmap.creator
)

print("Map:", title)
print("Stars:", round(stars, 2))
print("Acc:", round(pp.acc_percent, 2), "%")
combo_s = "Combo: {comb}/{max_comb} with {miss} misses".format(
    comb=combo, max_comb=btmap.max_combo, miss=misses)
print(combo_s)
print("Performance:", pp.pp, "PP")
