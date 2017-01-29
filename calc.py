import diff_calc
import requests
import pp_calc
import sys
import argparse
import b_info
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
try:
    file_name = args.file
    if feature:
        if not key:
            raise ValueError("Please enter an API key to use this feature.")
        print("lol")
        url = b_info.main(file_name, key)
        print(url)
        file = requests.get(b_info.main(file_name, key)).raw
        print(file)
    else:
        file = open(file_name)
except Exception as ex:
    print("ERROR: " + file_name + " not a valid beatmap or API key is incorrect")
    sys.exit(1)
btmap = Beatmap(file)
btmap.parse()
if combo == 0 or combo > btmap.max_combo:
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


class Mods:
    def __init__(self):
        self.nomod = 0,
        self.nf = 0
        self.ez = 0
        self.hd = 0
        self.hr = 0
        self.dt = 0
        self.ht = 0
        self.nc = 0
        self.fl = 0
        self.so = 0
        self.speed_changing = self.dt | self.ht | self.nc
        self.map_changing = self.hr | self.ez | self.speed_changing

    def update(self):
        self.speed_changing = self.dt | self.ht | self.nc
        self.map_changing = self.hr | self.ez | self.speed_changing


mod = Mods()


def set_mods(mod, mod_name):
    if m == "NF":
        mod.nf = 1
    if m == "EZ":
        mod.ez = 1
    if m == "HD":
        mod.hd = 1
    if m == "HR":
        mod.hr = 1
    if m == "DT":
        mod.dt = 1
    if m == "HT":
        mod.ht = 1
    if m == "NC":
        mod.nc = 1
    if m == "FL":
        mod.fl = 1
    if m == "SO":
        mod.so = 1


if mod_s:
    mod_s = [mod_s[i:i + 2] for i in range(0, len(mod_s), 2)]
    print(mod_s)
    for m in mod_s:
        set_mods(mod, m)
        mod.update()

mod_string = mod_str(mod)
btmap.apply_mods(mod)
diff = diff_calc.main(map)
if not acc:
    pp = pp_calc.pp_calc(diff[0], diff[1], diff[3], misses, c100, c50, mod, combo, score_ver)
else:
    pp = pp_calc.pp_calc_acc(diff[0], diff[1], diff[3], acc, mod, combo, misses, score_ver)


title = f"{btmap.artist} - {btmap.title} [{btmap.version}] +{mod_string} ({btmap.creator})"

print("Map: " + title)
print("Stars: " + str(round(diff[2], 2)))
print("Acc: ", round(pp.acc_percent, 2), "%")
comb_s = "Combo: " + str(combo) + "/" + str(int(btmap.max_combo))
if misses:
    comb_s += " with " + str(misses) + " misses"
print(comb_s)
print("Performance: " + str(round(pp.pp, 2)) + "PP")
