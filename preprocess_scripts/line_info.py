from glob import glob
import pandas as pd
import numpy as np
import re
from copy import deepcopy
import jaconv
from tqdm import tqdm
from preprocess_scripts.base_search_function import search_inside_sentence

def line_info_func(self):
    for look_up_file,f_name in zip(self.look_up_files,self.f_names):
        ono_lis = []
        with open(self.b_name,"r") as f:
            for line in f:
                ono_lis.append(line.rstrip("\n"))
        ono_lis = list(set(ono_lis))
        ono_counter = {}
        ono_lis_st = "|".join(ono_lis)

        file_list = glob(look_up_file.rstrip("/"))
        ono = []
        print(file_list)

        for file in tqdm(file_list):
            story_list = file + "/*"
            for story in tqdm(glob(story_list)):
                for i in ono_lis:
                    ono_counter[i] = []
                for data in tqdm(glob(story + "/*")):
                    if f_name+ story.lstrip(look_up_file) + "line_info.csv" in glob(f_name+"*.csv"):
                        pass
                    elif len(glob(story + "/*")) == 1:
                        ono_counter = search_inside_sentence(data, ono_lis_st, ono_counter, "line_info", True)
                    else:
                        if self.exclude_strings in data:
                           pass
                        else:
                            ono_counter = search_inside_sentence(data, ono_lis_st, ono_counter, "line_info", False)
                if f_name + story.lstrip(look_up_file) + "line_info.csv" in glob(f_name + "*.csv"):
                    pass
                else:
                    df = pd.DataFrame([[i for i in ono_counter.values() if len(i) > 0]], index=[story],
                                          columns=[i for i in ono_counter.keys() if len(ono_counter[i]) > 0])
                    df.to_csv(f_name + story.lstrip(look_up_file) + "line_info.csv", index=False)
