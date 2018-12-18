#The order is important DO NOT USE glob

from glob import glob
import pandas as pd
import numpy as np
import re
from copy import deepcopy
import jaconv
from tqdm import tqdm

from preprocess_scripts.mid import mid_func
from preprocess_scripts.line_info_n_k import line_info_n_k_func
from preprocess_scripts.find_ono_kata import find_ono_kata_func
from preprocess_scripts.line_info import line_info_func
from preprocess_scripts.find_ono_hira import find_ono_hira_func
from preprocess_scripts.line_info_k import line_info_k_func
from preprocess_scripts.line_info_n import line_info_n_func
from preprocess_scripts.integrate import integrate
from preprocess_scripts.integrate_fin import integrate_fin

class Base_Lookup():
    def __init__(self,option=None,d="naka"):
        self.d = d
        self.theme_list = ["action","sf","bungaku","comedy","douwa","essay","highfantasy","history","horror","human","isekai","lowfantasy","mystery","other","panic","poem","real","space","vrgame"]
        self.look_up_files = ['../narou_books/年間アクション〔文芸〕/',
         '../narou_books/年間ホラー〔文芸〕/',
         '../narou_books/年間ヒューマンドラマ〔文芸〕/',
         '../narou_books/年間パニック〔SF〕/',
         '../narou_books/年間VRゲーム〔SF〕/',
         '../narou_books/年間童話〔その他〕/',
         '../narou_books/年間宇宙〔SF〕/',
         '../narou_books/年間ハイファンタジー〔ファンタジー〕/',
         '../narou_books/年間詩〔その他〕/',
         '../narou_books/年間エッセイ〔その他〕/',
         '../narou_books/年間推理〔文芸〕/',
         '../narou_books/年間空想科学〔SF〕/',
         '../narou_books/年間純文学〔文芸〕/',
         '../narou_books/年間異世界〔恋愛〕/',
         '../narou_books/年間その他〔その他〕/',
         '../narou_books/年間現実世界〔恋愛〕/',
         '../narou_books/年間ローファンタジー〔ファンタジー〕/',
         '../narou_books/年間歴史〔文芸〕/',
        '../narou_books/年間コメディー〔文芸〕/',]
        self.f_names = ['../preprocessed_data/csv_pack_action/',
         '../preprocessed_data/csv_pack_horror/',
         '../preprocessed_data/csv_pack_human/',
         '../preprocessed_data/csv_pack_panic/',
         '../preprocessed_data/csv_pack_vrgame/',
         '../preprocessed_data/csv_pack_douwa/',
         '../preprocessed_data/csv_pack_space/',
         '../preprocessed_data/csv_pack_highfantasy/',
         '../preprocessed_data/csv_pack_poem/',
         '../preprocessed_data/csv_pack_essay/',
         '../preprocessed_data/csv_pack_mystery/',
         '../preprocessed_data/csv_pack_sf/',
         '../preprocessed_data/csv_pack_bungaku/',
         '../preprocessed_data/csv_pack_isekai/',
        '../preprocessed_data/csv_pack_other/',
        '../preprocessed_data/csv_pack_real/',
         '../preprocessed_data/csv_pack_lowfantasy/',
         '../preprocessed_data/csv_pack_history/',
        '../preprocessed_data/csv_pack_comedy/']

        self.exclude_strings = "表紙"

        #The script above is data driven

        self.f_names = [i + self.d + "/" for i in self.f_names]

        self.option = option
        if option == "mid":
            self.b_name = "../dictionary_resource/" + self.d + "/" + self.d + "_result-mid.txt"
        elif option == "line_info_n_k" or option == "line_info_n":
            self.b_name = "../dictionary_resource/" + self.d + "/" + self.d + "_result.txt"
        elif option == "find_ono_hira" or option == "find_ono_kata" or option == "line_info" or option == "line_info_k":
            self.b_name = "../dictionary_resource/" + self.d + "/" + self.d + "_result-mix.txt"
        else:
            pass
    def count(self):
        if self.option == "mid":mid_func(self)
        elif self.option == "line_info_n_k":line_info_n_k_func(self)
        elif self.option == "line_info_n":line_info_n_func(self)
        elif self.option == "find_ono_hira":find_ono_hira_func(self)
        elif self.option == "find_ono_kata":find_ono_kata_func(self)
        elif self.option == "line_info":line_info_func(self)
        elif self.option == "line_info_k":line_info_k_func(self)
        elif self.option == "all":
            self.b_name = "../dictionary_resource/" + self.d + "/" + self.d + "_result-mid.txt"
            mid_func(self)
            self.b_name = "../dictionary_resource/" + self.d + "/" + self.d + "_result.txt"
            line_info_n_k_func(self)
            line_info_n_func(self)
            self.b_name = "../dictionary_resource/" + self.d + "/" + self.d + "_result-mix.txt"
            find_ono_hira_func(self)
            find_ono_kata_func(self)
            line_info_func(self)
            line_info_k_func(self)
        else:raise Exception
    def all(self):
        integrate(self)
    def all2(self):
        integrate_fin(self)

if __name__ == "__main__":
    b = Base_Lookup("all")
    b.count()
    b.all()
    b.all2()