import math
import jaconv
import re
import pandas as pd
from tqdm import tqdm
import MeCab
import codecs
from gensim import models
from gensim.models.doc2vec import TaggedDocument
from gensim.models import word2vec
import logging
import sys
from copy import deepcopy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict
from onomatope_base_model import ono_naka

class ono_okawa(ono_naka):
    def __init__(self):
        super(ono_okawa,self).__init__()
        self.sem_dic = defaultdict(list)
        with open("naka_jisho") as f:
                    for line in f:
                        line = line.split("\t")
                        if line[0] == "大":
                            big = line[1].rstrip("\n")
                        elif line[0] == "中":
                            med = line[1].rstrip("\n")
                        elif line[0] == "小":
                            small = line[1].rstrip("\n")
                        else:
                            self.sem_dic[line[1].rstrip("\n")].append([big,med,small])
    def S(self,word):
        #semantic similarity
        #Might be similar with P ?
        if len(word)%2 == 0:
            word1 = word[:len(word)//2] + word[:len(word)//2]
            word2 = word[len(word)//2:] + word[len(word)//2:]
        else:
            word1 = word[:len(word)//2] + word[:len(word)//2]
            word2 = word[len(word)//2:] + word[len(word)//2:]
            if(word1 in self.df_line_info_n.keys() or word2 in self.df_line_info_n.keys()):
                pass
            else:
                word1 = word[:len(word)//2+1] + word[:len(word)//2+1]
                word2 = word[len(word)//2+1:] + word[len(word)//2+1:]
        if word1 not in self.sem_dic.keys() or word2 not in self.sem_dic.keys():
            return 0
        s_score = 0
        dis_max = 3
        for cat1 in self.sem_dic[word1]:
            for cat2 in self.sem_dic[word2]:
                temp = 0
                for c in range(dis_max):
                    temp += sum([cat1[c] == cat2[c]])
                s_score = max(temp,s_score)
        return s_score/float(dis_max)

    def M(self,word):
        #ABCAB ? Is this OK ?
        if len(word)%2 == 0:
            return 0.0
        else:
            if word[:len(word)//2] == word[len(word)//2+1:]:
                return -0.5
            else:
                return 0.0
    def calculate_all(word):
        m = 0.773041177880463
        P = ono_okawa.P(word)/m
        C = ono_okawa.C(word)
        S = ono_okawa.S(word)
        df = pd.DataFrame(index=[],columns=["Word","C","I","P","CI","CP","IP","CIP","S","CIPS"])
        if len(word)%2 == 0:
            I = Ono1.I(word[:len(word)//2]+word[:len(word)//2]+word[len(word)//2:]+word[len(word)//2:])
        else:
            I1 = Ono1.I(word[:len(word)//2]+word[:len(word)//2]+word[len(word)//2:]+word[len(word)//2:])
            I2 = Ono1.I(word[:len(word)//2+1]+word[:len(word)//2+1]+word[len(word)//2+1:]+word[len(word)//2+1:])
            if I1 >= I2:
                I = I1
            else:
                I = I2
        if sum([C,I,P,S]) == 0:
            pass
        else:
            series = pd.Series([word,C,I,P,C+I,C+P,I+P,C+I+P,S,S+I+C+P],index=["Word","C","I","P","CI","CP","IP","CIP","S","CIPS"])
            df = df.append(series, ignore_index=True)
            df.to_csv("./PICS.csv")

if __name__  == "__main__":
    Ono1 = ono_okawa()
    word_list = Ono1.df_hira.keys()
    for word in tqdm(word_list):
        Ono1.calculate_all(word)
    #TODO: The value P has to be normalized
