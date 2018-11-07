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

class Ono():
    def __init__(self):
        self.col_names = [str(i) for i in range(1000)]
        self.Pvalue = 0
        self.Ivalue = 0
        self.Cvalue = 0
        self.df_mid = {}
        with open("./all_mid.csv") as f:
            for line in f:
                info = line.split(",")
                self.df_mid[info[0]] = info[1]
        self.df_hira = {}
        with open("./all_hira.csv") as f:
            for line in f:
                info = line.split(",")
                self.df_hira[info[0]] = info[1]
        self.df_kata = {}
        with open("./all_kata.csv") as f:
            for line in f:
                info = line.split(",")
                self.df_kata[info[0]] = info[1]
        self.df_line_info = {}
        with open("./all_line_info.csv") as f:
            for line in f:
                info = line.split(",")
                self.df_line_info[info[0]] = info[1:]
        self.df_line_info_n = {}
        with open("./all_line_info_n.csv") as f:
            for line in f:
                info = line.split(",")
                self.df_line_info_n[info[0]] = info[1:]
        self.df_line_info_k = {}
        with open("./all_line_info_k.csv") as f:
            for line in f:
                info = line.split(",")
                self.df_line_info_k[info[0]] = info[1:]

        self.df_line_info_n_k = {}
        with open("./all_line_info_n_k.csv") as f:
            for line in f:
                info = line.split(",")
                self.df_line_info_n_k[info[0]] = info[1:]

        self.tagger = MeCab.Tagger("-Owakati")
        vectorizer = TfidfVectorizer()
        #define the tf-idf vector here?
        self.all_vocab = []
        self.ono_map_dict = {}
        count = 0
        for word,sentences in self.df_line_info_k.items():
            self.ono_map_dict[word] = count
            temp = []
            for sentence in sentences:
                sentence = re.sub(r"\\n", "", sentence)
                sentence = re.sub(r"\n", "", sentence)
                sentence = re.sub(r"\\u3000", "", sentence)
                sentence = self.tagger.parse(sentence)
                #exclude stop words ?
                if sentence.split() != []:
                    temp.extend(sentence.split())
            count += 1
            self.all_vocab.append(" ".join(temp))

        for word,sentences in self.df_line_info_n_k.items():
            self.ono_map_dict[word] = count
            temp = []
            for sentence in sentences:
                sentence = re.sub(r"\\n", "", sentence)
                sentence = re.sub(r"\n", "", sentence)
                sentence = re.sub(r"\\u3000", "", sentence)
                sentence = self.tagger.parse(sentence)
                #exclude stop words ?
                if sentence.split() != []:
                    temp.extend(sentence.split())
            count += 1
            self.all_vocab.append(" ".join(temp))

        self.term_doc = vectorizer.fit_transform(self.all_vocab)
        #print(cosine_similarity(self.term_doc[1:1+1], self.term_doc))
class ono_naka(Ono):
    def __init__(self):
        super(ono_naka,self).__init__()
    def P(self,word):
        word = jaconv.hira2kata(word)
        try:
            self.df_line_info_k[word]
        except:
            return 0
        if len(word)%2 == 0:
            word1 = word[:len(word)//2] + word[:len(word)//2]
            word2 = word[len(word)//2:] + word[len(word)//2:]
        else:
            word1 = word[:len(word)//2] + word[:len(word)//2]
            word2 = word[len(word)//2:] + word[len(word)//2:]
            if(word1 in self.df_kata.keys() or word2 in self.df_kata.keys()):
                pass
            else:
                word1 = word[:len(word)//2+1] + word[:len(word)//2+1]
                word2 = word[len(word)//2+1:] + word[len(word)//2+1:]
        id1,id2 =None,None
        try:
            id1 = self.ono_map_dict[word1]
        except:
            pass
        try:
            id2 = self.ono_map_dict[word2]
        except:
            pass
        temp_array = cosine_similarity(self.term_doc[self.ono_map_dict[word]:self.ono_map_dict[word]+1], self.term_doc)[0]
        if id1 != None and id2 != None:
            return (temp_array[id1] + temp_array[id2])/2
        elif id1 == None and id2 != None:
            return temp_array[id2]
        elif id1 != None and id2 == None:
            return temp_array[id1]
        else:
            return 0

            #result contains combined ono
            #result2 and result3 contains pure ono
    def I(self,word):
        m=0.05 #tuning parameter
        try:
            A = float(self.df_mid[word])
        except:
            A = 0.0
        #A= self.Idict[word] # frequency of intermediate state
        self.Ivalue = 2/(1+math.exp(-m*A))-1
        return self.Ivalue

    def C(self,word):
        try:
            H = float(self.df_hira[word])
        except KeyError:
            H = 0.0
        try:
            K = float(self.df_kata[jaconv.hira2kata(word)])
        except KeyError:
            K = 0.0
        n = 10 #tuning parameter
        self.Cvalue = 2/(1+math.exp(-n*K/(H+1))) -1
        return self.Cvalue

class ono_okawa(ono_naka):
    def __init__(self):
        super(ono_okawa,self).__init__()
    def S(self,word):
        try:
            self.df_line_info_n[word]
        except:
            return 0
        if len(word)%2 == 0:
            word1 = word[:len(word)//2] + word[:len(word)//2]
            word2 = word[len(word)//2:] + word[len(word)//2:]
        else:
            word1 = word[:len(word)//2] + word[:len(word)//2]
            word2 = word[len(word)//2:] + word[len(word)//2:]
            if(word1 in self.df_kata.keys() or word2 in self.df_kata.keys()):
                pass
            else:
                word1 = word[:len(word)//2+1] + word[:len(word)//2+1]
                word2 = word[len(word)//2+1:] + word[len(word)//2+1:]
        big = ""
        med = ""
        small = ""
        sem_dic = defaultdict(list)
        with open("naka_jisho") as f:
            for line in f:
                line = line.split("\t")
                if line[0] == "大":
                    big = line[1]
                elif line[0] == "中":
                    med = line[1]
                elif line[0] == "小":
                    small = line[1]
                else:
                    sem_dic[line[1]].append([big,med,small])
        #split words
        s_score = 0
        dis_max = 3
        try:
            s_score = sum([sem_dic[word1][i] == sem_dic[word2][i] for i in range(dis_max)])
        except:
            pass
        return s_score/float(dis_max)

if __name__  == "__main__":
    Ono1 = ono_okawa()
    word_list = Ono1.df_hira.keys()
    df = pd.DataFrame(index=[],columns=["Word","C","I","P","CI","CP","IP","CIP","S","CIPS"])

    for word in tqdm(word_list):
        if len(word)%2 == 0:
            P = Ono1.P(word)/0.773041177880463
            I = Ono1.I(word[:len(word)//2]+word[:len(word)//2]+word[len(word)//2:]+word[len(word)//2:])
            C = Ono1.C(word)
            S = Ono1.S(word)
            if [C,I,P,C+I,C+P,I+P,C+I+P,S,S+C+I+P] == [0,0,0,0,0,0,0,0,0]:
                pass
            else:
                series = pd.Series([word,C,I,P,C+I,C+P,I+P,C+I+P,S,S+C+I+P],index=["Word","C","I","P","CI","CP","IP","CIP","S","CIPS"])
                df = df.append(series,ignore_index=True)
        else:
            P = Ono1.P(word)/0.773041177880463
            I1 = Ono1.I(word[:len(word)//2]+word[:len(word)//2]+word[len(word)//2:]+word[len(word)//2:])
            I2 = Ono1.I(word[:len(word)//2+1]+word[:len(word)//2+1]+word[len(word)//2+1:]+word[len(word)//2+1:])
            if I1 >= I2:
                I = I1
            else:
                I = I2
            C = Ono1.C(word)
            S = Ono1.S(word)
            if [C,I,P,C+I,C+P,I+P,C+I+P,S,C+I+P+S] == [0,0,0,0,0,0,0,0,0]:
                pass
            else:
                series = pd.Series([word,C,I,P,C+I,C+P,I+P,C+I+P,S,S+I+C+P],index=["Word","C","I","P","CI","CP","IP","CIP","S","CIPS"])
                df = df.append(series, ignore_index=True)
    df.to_csv("./PICS.csv")
    #TODO: The value P has to be normalized
