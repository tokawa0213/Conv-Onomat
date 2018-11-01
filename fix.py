import os
import shutil
from glob import glob
import re

name = "sf"

for i in glob("csv_pack_" + name + "*"):
    shutil.move(i,"csv_pack_"+name + "/")

for i in glob("csv_pack_" + name + "/*"):
    os.rename(i,"csv_pack_" + name + "/" + i.lstrip("csv_pack_" + name + "/csv_pack_" + name))