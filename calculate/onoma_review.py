import math
import jaconv
import re
import pandas as pd
from tqdm import tqdm
import MeCab
from gensim import models
from gensim.models.doc2vec import TaggedDocument
from gensim.models import word2vec
import logging
import sys
from copy import deepcopy
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict

class Ono():
    def __init__(self):
        self.Pvalue = 0
        self.Ivalue = 0
        self.Cvalue = 0

        self.df_mid = pd.read_csv("./df7.csv")
        self.df_mid.fillna(value=0, inplace=True)

        self.df_hira = pd.read_csv("./df3.csv")
        self.df_hira.fillna(value=0, inplace=True)

        self.df_kata = pd.read_csv("./df4.csv")
        self.df_kata.fillna(value=0, inplace=True)

        self.df_line_info = pd.read_csv("./new_df.csv")
        self.df_line_info.fillna(value="", inplace=True)

        self.df_line_info_n = pd.read_csv("./new_df5.csv")
        self.df_line_info_n.fillna(value="", inplace=True)

        self.df_line_info_k = defaultdict(list)
        with open("./new_df2.csv") as f:
            for line in f:
                info = line.split(",")
                self.df_line_info_k[info[0]].append(info[1].lstrip('"').rstrip("'"))

        self.df_line_info_n_k = defaultdict(list)
        with open("./new_df6.csv") as f:
            for line in f:
                info = line.split(",")
                self.df_line_info_n_k[info[0]].append(info[1].lstrip('"').rstrip("'"))

        self.tagger = MeCab.Tagger("-Owakati")
        print()
        vectorizer = TfidfVectorizer()
        # define the tf-idf vector here?
        self.all_vocab = []
        self.ono_map_dict = {}
        count = 0
        for word, sentences in self.df_line_info_k.items():
            self.ono_map_dict[word] = count
            temp = []
            for sentence in sentences:
                if sentence.split() != []:
                    temp.extend(sentence.split())
            count += 1
            self.all_vocab.append(" ".join(temp))

        for word, sentences in self.df_line_info_n_k.items():
            self.ono_map_dict[word] = count
            temp = []
            for sentence in sentences:
                if sentence.split() != []:
                    temp.extend(sentence.split())
            count += 1
            self.all_vocab.append(" ".join(temp))

        self.term_doc = vectorizer.fit_transform(self.all_vocab)
        #print(cosine_similarity(self.term_doc[1:1+1], self.term_doc))

    def P(self, word):
        try:
            self.df_line_info_k[word]
        except:
            return 0
        if len(word) % 2 == 0:
            word1 = word[:len(word) // 2] + word[:len(word) // 2]
            word2 = word[len(word) // 2:] + word[len(word) // 2:]
        else:
            word1 = word[:len(word) // 2] + word[:len(word) // 2]
            word2 = word[len(word) // 2:] + word[len(word) // 2:]
            if (word1 in list(self.df_kata.columns) or word2 in list(self.df_kata.columns)):
                pass
            else:
                word1 = word[:len(word) // 2 + 1] + word[:len(word) // 2 + 1]
                word2 = word[len(word) // 2 + 1:] + word[len(word) // 2 + 1:]
        id1, id2 = None, None
        try:
            id1 = self.ono_map_dict[word1]
        except:
            pass
        try:
            id2 = self.ono_map_dict[word2]
        except:
            pass
        try:
            temp_array = cosine_similarity(self.term_doc[self.ono_map_dict[word]:self.ono_map_dict[word] + 1], self.term_doc)[0]
        except:
            print(word)
            return 0
        if id1 != None and id2 != None:
            return (temp_array[id1] + temp_array[id2]) / 2
        elif id1 == None and id2 != None:
            return temp_array[id2]
        elif id1 != None and id2 == None:
            return temp_array[id1]
        else:
            return 0

    def I(self, word):
        m = 0.05  # tuning parameter
        try:
            A = self.df_mid.at[0,word]
        except:
            A = 0.0
        # A= self.Idict[word] # frequency of intermediate state
        self.Ivalue = 2 / (1 + math.exp(-m * A)) - 1
        return self.Ivalue

    def C(self, word):
        try:
            #print(self.df_hira.at[0, word])
            H = self.df_hira.at[0,word]
        except KeyError:
            H = 0.0
        try:
            K = self.df_kata.at[0,word]
        except KeyError:
            K = 0.0
        n = 10  # tuning parameter
        self.Cvalue = 2 / (1 + math.exp(-n * K / ((H - K) + 1))) - 1
        return self.Cvalue

    def get_final_value(self):
        pass


Ono1 = Ono()
word_list = Ono1.df_hira.columns.values[1:]
df = pd.DataFrame(index=[], columns=["Word", "C", "I", "P", "CI", "CP", "IP", "CIP"])

for word in tqdm(word_list):
    if len(word) % 2 == 0:
        P = Ono1.P(word)/0.5274717184006164
        I = Ono1.I(word[:len(word) // 2] + word[:len(word) // 2] + word[len(word) // 2:] + word[len(word) // 2:])
        C = Ono1.C(word)
        if [C, I, P, C + I, C + P, I + P, C + I + P] == [0, 0, 0, 0, 0, 0, 0]:
            pass
        else:
            series = pd.Series([word, C, I, P, C + I, C + P, I + P, C + I + P],
                               index=["Word", "C", "I", "P", "CI", "CP", "IP", "CIP"])
            df = df.append(series, ignore_index=True)
    else:
        P = Ono1.P(word)
        I1 = Ono1.I(word[:len(word) // 2] + word[:len(word) // 2] + word[len(word) // 2:] + word[len(word) // 2:])
        I2 = Ono1.I(word[:len(word) // 2 + 1] + word[:len(word) // 2 + 1] + word[len(word) // 2 + 1:] + word[len(
            word) // 2 + 1:])
        if I1 >= I2:
            I = I1
        else:
            I = I2
        C = Ono1.C(word)
        if [C, I, P, C + I, C + P, I + P, C + I + P] == [0, 0, 0, 0, 0, 0, 0]:
            pass
        else:
            series = pd.Series([word, C, I, P, C + I, C + P, I + P, C + I + P],
                               index=["Word", "C", "I", "P", "CI", "CP", "IP", "CIP"])
            df = df.append(series, ignore_index=True)
df.to_csv("./PICrev.csv")
# TODO: The value P has to be normalized