import pandas as pd

df = pd.read_csv("PICS.csv")
li = []
with open("naka_jisho") as f:
    for line in f:
        if line.split("\t")[0] not in ["大","中","小"]:
            li.append(line.split("\t")[1])
df = df[li]

