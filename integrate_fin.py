import pandas as pd
from glob import glob
from tqdm import tqdm
import numpy as np
import re

theme_list = ["action","sf","bungaku","comedy","douwa","essay","highfantasy","history","horror","human","isekai","lowfantasy","mystery","other","panic","poem","real","space","vrgame"]
kata = []
line_info = []
mid = []
hira = []
line_info_n = []
line_info_k = []
line_info_n_k = []
karai = []

for theme in theme_list:
    #f_name = "./csv_pack_" + theme + "/"
    #kata.append(f_name + "kata.csv")
    #line_info.append(f_name + "line_info.csv")
    #mid.append(f_name + "mid.csv")
    #hira.append(f_name + "hira.csv")
    #line_info_n.append(f_name + "line_info_n.csv")
    #line_info_k.append(f_name + "line_info_k.csv")
    #line_info_n_k.append(f_name + "line_info_n_k.csv")
    karai.append("karai.csv")

li = []

from collections import defaultdict

import sys

ono_counter = defaultdict(list)

for csv_cat in tqdm(karai):
    df_temp = pd.read_csv(csv_cat)
    for key,value in df_temp.items():
        for sentence in value.tolist():
            if str(sentence) != "nan":
                ono_counter[key].append(sentence)
            else:
                pass

with open("all_karai.csv","a") as f:
    for ono in list(ono_counter.keys()):
        num = 0
        st = ""
        print(ono)
        st += ono
        st += ","
        for i in ono_counter[ono]:
            i = re.sub("\[","",i)
            i = re.sub("\]","",i)
            i = re.sub("'","",i)
            i = re.sub(r"\\u3000", "", i)
            i = re.sub(r"\\n", "", i)
            i = re.sub(r"\n", "", i)
            st += i
            st += ","
            #num += 1
        st += "\n"
        #st += str(num) + "\n"
        f.write(st)
