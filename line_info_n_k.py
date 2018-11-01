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

b_name = "naka_result.txt"
d = "naka/"

look_up_files = ['narou_books/年間アクション〔文芸〕/',
 'narou_books/年間ホラー〔文芸〕/',
 'narou_books/年間ヒューマンドラマ〔文芸〕/',
 'narou_books/年間パニック〔SF〕/',
 'narou_books/年間VRゲーム〔SF〕/',
 'narou_books/年間童話〔その他〕/',
 'narou_books/年間宇宙〔SF〕/',
 'narou_books/年間ハイファンタジー〔ファンタジー〕/',
 'narou_books/年間詩〔その他〕/',
 'narou_books/年間エッセイ〔その他〕/',
 'narou_books/年間推理〔文芸〕/',
 'narou_books/年間空想科学〔SF〕/',
 'narou_books/年間純文学〔文芸〕/',
 'narou_books/年間異世界〔恋愛〕/',
 'narou_books/年間その他〔その他〕/',
 'narou_books/年間現実世界〔恋愛〕/',
 'narou_books/年間ローファンタジー〔ファンタジー〕/',
 'narou_books/年間歴史〔文芸〕/',
'narou_books/年間コメディー〔文芸〕/',]
f_names = ['./csv_pack_action/',
 './csv_pack_horror/',
 './csv_pack_human/',
 './csv_pack_panic/',
 './csv_pack_vrgame/',
 './csv_pack_douwa/',
 './csv_pack_space/',
 './csv_pack_highfantasy/',
 './csv_pack_poem/',
 './csv_pack_essay/',
 './csv_pack_mystery/',
 './csv_pack_sf/',
 './csv_pack_bungaku/',
 './csv_pack_isekai/',
'./csv_pack_other/',
'./csv_pack_real/',
 './csv_pack_lowfantasy/',
 './csv_pack_history/',
'./csv_pack_comedy/']


f_names = [i + d for i in f_names]

for look_up_file,f_name in zip(look_up_files,f_names):
    ono_lis = []
    with open(b_name,"r") as f:
        for line in f:
            ono_lis.append(line.rstrip("\n"))
    ono_lis = list(set(ono_lis))
    ono_lis = [jaconv.hira2kata(i) for i in ono_lis]
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
                if f_name + story.lstrip(look_up_file) + "line_info_n_k.csv" in glob(f_name+"*.csv"):
                    pass
                elif len(glob(story + "/*")) == 1:
                    with open(data, "r") as f:
                        for line in tqdm(f):
                            # convert katakana into hiragana
                            #line = jaconv.kata2hira(line)
                            line = line.rstrip("\n")
                            for i in re.findall(ono_lis_st, line):
                                ono_counter[i] .append(line)
                                # ono_counter = {"pachipachi":1,...}
                                # story = book_id
                else:
                    if "表紙" in data:
                       pass
                    else:
                        with open(data, "r") as f:
                            for line in f:
                                # convert katakana into hiragana
                                #line = jaconv.kata2hira(line)
                                for i in re.findall(ono_lis_st, line):
                                    ono_counter[i].append(line)
                                    # ono_counter = {"pachipachi":1,...}
                                    # story = book_id
            if f_name + story.lstrip(look_up_file) + "line_info_n_k.csv" in glob(f_name + "*.csv"):
                print(f_name + story.lstrip(look_up_file) + "line_info_n_k.csv")
                pass
            else:
                df = pd.DataFrame([[i for i in ono_counter.values() if len(i) > 0]], index=[story],
                                      columns=[i for i in ono_counter.keys() if len(ono_counter[i]) > 0])
                df.to_csv(f_name + story.lstrip(look_up_file) + "line_info_n_k.csv", index=False)