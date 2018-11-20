from glob import glob
import pandas as pd
import numpy as np
import re
from copy import deepcopy
import jaconv
from tqdm import tqdm
from copy import deepcopy

#Reference
#line_info => hiragana_line_info of combined
#line_info_n => hiragana line info of uncombined
#line_info_k => katakana line_info of combined
#line_info_n_k => katakana_line_info of uncombined

def line_info_n_func(self):
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
                    if f_name + story.lstrip(look_up_file) + "line_info_n.csv" in glob(f_name+"*.csv"):
                        pass
                    elif len(glob(story + "/*")) == 1:
                        with open(data, "r") as f:
                            for line in tqdm(f):
                                # convert katakana into hiragana
                                line = jaconv.kata2hira(line)
                                line = line.rstrip("\n")
                                for i in re.findall(ono_lis_st, line):
                                    ono_counter[i] .append(line)
                                    # ono_counter = {"pachipachi":1,...}
                                    # story = book_id
                    else:
                        if self.exclude_strings in data:
                           pass
                        else:
                            with open(data, "r") as f:
                                for line in f:
                                    # convert katakana into hiragana
                                    line = jaconv.kata2hira(line)
                                    for i in re.findall(ono_lis_st, line):
                                        ono_counter[i].append(line)
                                        # ono_counter = {"pachipachi":1,...}
                                        # story = book_id
                if f_name + story.lstrip(look_up_file) + "line_info_n.csv" in glob(f_name + "*.csv"):
                    print(f_name + story.lstrip(look_up_file) + "line_info_n.csv")
                    pass
                else:
                    df = pd.DataFrame([[i for i in ono_counter.values() if len(i) > 0]], index=[story],
                                          columns=[i for i in ono_counter.keys() if len(ono_counter[i]) > 0])
                    df.to_csv(f_name + story.lstrip(look_up_file) + "line_info_n.csv", index=False)