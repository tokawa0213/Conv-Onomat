all = []
with open("review_data/all_reviews_Toyoko.txt") as f:
    for line in f:
        for p in line.split("。"):
            all.append(p)
with open("review_data/all_reviews_NewOtani.txt") as f:
    for line in f:
        for p in line.split("。"):
            all.append(p)
with open("review_data/all_reviews_Okura.txt") as f:
    for line in f:
        for p in line.split("。"):
            all.append(p)
with open("review_data/all_reviews_Apa.txt") as f:
    for line in f:
        for p in line.split("。"):
            all.append(p)

import jaconv
import re
import pandas as pd
from collections import defaultdict
from tqdm import tqdm

ono_lis = []
with open("hanpuku.txt","r") as f:
    for line in f:
        ono_lis.append(line.rstrip("\n"))
ono_lis = list(set(ono_lis))
ono_lis_st = "|".join(ono_lis)
"""
ono_counter = defaultdict(list)

for line in tqdm(all):
    # convert katakana into hiragana
    line = jaconv.kata2hira(line)
    line = line.rstrip("\n")
    for i in set(re.findall(ono_lis_st, line)):
        print(i,line)
        ono_counter[i].append(line)
        # ono_counter = {"pachipachi":1,...}
        # story = book_id

df = pd.DataFrame([[i for i in ono_counter.values() if len(i) > 0]], columns=[i for i in ono_counter.keys() if len(ono_counter[i]) > 0])
df.to_csv("df.csv", index=False)

ono_counter = defaultdict(list)

for line in tqdm(all):
    # convert katakana into hiragana
    #line = jaconv.kata2hira(line)
    line = line.rstrip("\n")
    for i in re.findall(ono_lis_st, line):
        ono_counter[i].append(line)
        # ono_counter = {"pachipachi":1,...}
        # story = book_id

df = pd.DataFrame([[i for i in ono_counter.values() if len(i) > 0]], columns=[i for i in ono_counter.keys() if len(ono_counter[i]) > 0])
df.to_csv("df2.csv", index=False)
"""

"""
ono_counter = defaultdict(int)

for line in tqdm(all):
    # convert katakana into hiragana
    # line = jaconv.kata2hira(line)
    line = line.rstrip("\n")
    for i in re.findall(ono_lis_st, line):
        ono_counter[i] += 1
        # ono_counter = {"pachipachi":1,...}
        # story = book_id

df = pd.DataFrame([[i for i in ono_counter.values() if i > 0]], columns=[i for i in ono_counter.keys() if ono_counter[i] > 0])
df.to_csv("df3.csv", index=False)
"""

"""

ono_counter = defaultdict(int)

for line in tqdm(all):
    # convert katakana into hiragana
    line = jaconv.kata2hira(line)
    line = line.rstrip("\n")
    for i in re.findall(ono_lis_st, line):
        ono_counter[i] += 1
        # ono_counter = {"pachipachi":1,...}
        # story = book_id

df = pd.DataFrame([[i for i in ono_counter.values() if i > 0]], columns=[i for i in ono_counter.keys() if ono_counter[i] > 0])
df.to_csv("df4.csv", index=False)
"""

"""
ono_lis = []
with open("hanpuku-mix.txt","r") as f:
    for line in f:
        ono_lis.append(line.rstrip("\n"))
ono_lis = list(set(ono_lis))
ono_counter = {}
ono_lis_st = "|".join(ono_lis)

ono_counter = defaultdict(list)

for line in tqdm(all):
    # convert katakana into hiragana
    #line = jaconv.kata2hira(line)
    line = line.rstrip("\n")
    for i in re.findall(ono_lis_st, line):
        ono_counter[i].append(line)
        # ono_counter = {"pachipachi":1,...}
        # story = book_id

df = pd.DataFrame([[i for i in ono_counter.values() if len(i) > 0]], columns=[i for i in ono_counter.keys() if len(ono_counter[i]) > 0])
df.to_csv("df5.csv", index=False)
"""


ono_counter = defaultdict(list)

for line in tqdm(all):
    # convert katakana into hiragana
    line = jaconv.kata2hira(line)
    line = line.rstrip("\n")
    for i in re.findall(ono_lis_st, line):
        ono_counter[i].append(line)
        # ono_counter = {"pachipachi":1,...}
        # story = book_id

df = pd.DataFrame([[i for i in ono_counter.values() if len(i) > 0]], columns=[i for i in ono_counter.keys() if len(ono_counter[i]) > 0])
df.to_csv("df6.csv", index=False)

with open("hanpuku-mid.txt", "r") as f:
    for line in f:
        ono_lis.append(line.rstrip("\n"))
"""
ono_counter = defaultdict(int)

for line in tqdm(all):
    # convert katakana into hiragana
    line = jaconv.kata2hira(line)
    line = line.rstrip("\n")
    for i in re.findall(ono_lis_st, line):
        ono_counter[i] += 1
        # ono_counter = {"pachipachi":1,...}
        # story = book_id

df = pd.DataFrame([[i for i in ono_counter.values() if i > 0]], columns=[i for i in ono_counter.keys() if ono_counter[i] > 0])
df.to_csv("df7.csv", index=False)
"""
