import pandas as pd
from glob import glob
from tqdm import tqdm
import numpy as np
import re
from collections import defaultdict
import sys

def integrate_fin(self,opt):
    kata = []
    line_info = []
    mid = []
    hira = []
    line_info_n = []
    line_info_k = []
    line_info_n_k = []

    for theme in self.theme_list:
        f_name = "../preprocessed_data/csv_pack_" + theme + "/"
        kata.append(f_name + "kata.csv")
        line_info.append(f_name + "line_info.csv")
        mid.append(f_name + "mid.csv")
        hira.append(f_name + "hira.csv")
        line_info_n.append(f_name + "line_info_n.csv")
        line_info_k.append(f_name + "line_info_k.csv")
        line_info_n_k.append(f_name + "line_info_n_k.csv")

    ono_counter = defaultdict(list)

    opt_d_in = {"find_ono_hira":hira,"find_ono_kata":kata,"line_info":line_info,"mid":mid,
             "line_info_n":line_info_n,"line_info_k":line_info_k,"line_info_n_k":line_info_n_k}
    opt_d = {"find_ono_hira":"hira","find_ono_kata":"kata","line_info":"line_info","mid":"mid",
             "line_info_n":"line_info_n","line_info_k":"line_info_k","line_info_n_k":"line_info_n_k"}

    for csv_cat in tqdm(opt_d_in[opt]):
        df_temp = pd.read_csv(csv_cat)
        for key,value in df_temp.items():
            for sentence in value.tolist():
                if str(sentence) != "nan":
                    ono_counter[key].append(sentence)
                else:
                    pass
    if opt == "find_ono_hira" or opt == "find_ono_kata" or opt == "mid":
        with open("all_" + opt_d[opt] + ".csv","a") as f:
            for ono in list(ono_counter.keys()):
                num = 0
                st = ""
                print(ono)
                st += ono
                st += ","
                for i in ono_counter[ono]:
                    num += 1
                st += str(num) + "\n"
                f.write(st)
    else:
        with open("all_" + opt_d[opt] + ".csv","a") as f:
            for ono in list(ono_counter.keys()):
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
                st += "\n"
                f.write(st)