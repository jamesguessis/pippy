import io

import diff_calc
import requests
import pp_calc
from pp_calc import Mods
import sys
import argparse
import btmap_info
import configparser
from beatmap import Beatmap

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
parser.add_argument('-key', help='Your osu! api key', metavar='KEY',
                    default='')

args = parser.parse_args()
c100 = int(args.c100)
c50 = int(args.c50)
misses = int(args.misses)
combo = int(args.combo)
acc = float(args.acc)
score_ver = int(args.score_ver)
mod_s = args.mods
feature = args.link
file_name = ""
if not args.key:
    try:
        f = open('keys.cfg')
        config = configparser.ConfigParser()
        config.readfp(f)
        key = config._sections["osu"]['api_key']
    except:
        raise Exception("Invalid config")
else:
    key = args.key
    file_name = args.file
if feature:
    if not key:
        raise ValueError("Please enter an API key to use this feature.")
    url = btmap_info.main(file_name, key)
    data = requests.get(btmap_info.main(file_name, key)).content.decode('utf-8')
else:
    data = open(file_name, 'r').readlines()
btmap = Beatmap(data)
btmap.parse()

if not combo or combo > btmap.max_combo:
    combo = btmap.max_combo


def mod_str(mod):
    string = ""
    if mod.nf:
        string += "NF"
    if mod.ez:
        string += "EZ"
    if mod.hd:
        string += "HD"
    if mod.hr:
        string += "HR"
    if mod.dt:
        string += "DT"
    if mod.ht:
        string += "HT"
    if mod.nc:
        string += "NC"
    if mod.fl:
        string += "FL"
    if mod.so:
        string += "SO"
    return string


mods = Mods()


def set_mods(mods_obj, mod_name):
    if mod_name == "NF":
        mods_obj.nf = 1
    if mod_name == "EZ":
        mods_obj.ez = 1
    if mod_name == "HD":
        mods_obj.hd = 1
    if mod_name == "HR":
        mods_obj.hr = 1
    if mod_name == "DT":
        mods_obj.dt = 1
    if mod_name == "HT":
        mods_obj.ht = 1
    if mod_name == "NC":
        mods_obj.nc = 1
    if mod_name == "FL":
        mods_obj.fl = 1
    if mod_name == "SO":
        mods_obj.so = 1


if mod_s:
    mods.from_str(mod_s)

mod_string = mod_str(mods)
btmap.apply_mods(mods)
diff = diff_calc.main(btmap)
if not acc:
    pp = pp_calc.calculate_pp(diff[0], diff[1], diff[3], misses, c100, c50, mods, combo, score_ver)
else:
    pp = pp_calc.calculate_pp_by_acc(diff[0], diff[1], diff[3], acc, mods, combo, misses, score_ver)

title = "{artist} - {title} [{version}] +{mods} ({creator})".format(
    artist=btmap.artist, title=btmap.title, version=btmap.version,
    mods=mod_string, creator=btmap.creator
)

print("Map: " + title)
print("Stars: " + str(round(diff[2], 2)))
print("Acc: ", round(pp.acc_percent, 2), "%")
combo_s = "Combo : {comb}/{max_comb} with {miss} misses".format(
    comb=combo, max_comb=btmap.max_combo, miss=misses)
print(combo_s)
print("Performance: ", pp.pp, "PP")
