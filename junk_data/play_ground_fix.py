# df : hiragana convertion -- valid, information -- line base --combined (line_info)
# df2 : hiragana convertion -- invalid, information -- line base --combined (line_info_k)
# df3 : hiragana convertion -- invalid, information -- word base --combined (kata)
# df4 : hiragana convertion -- valid, information -- word base --combined (hira)
# df5 : hiragana convertion -- invalid, information -- line base --uncombined ()
# df6 : hiragana convertion -- valid, information -- word base --uncombined
# df7 : hiragana convertion -- valid, information -- line base --combined

import pandas as pd
import MeCab

m = MeCab.Tagger("-Owakati")
df = pd.read_csv("./df.csv")
temp = []
for i in list(df.keys()):
    sentences = df[i].tolist()[0].split()
    for sentence in sentences:
        sentence = sentence.lstrip("['").rstrip("']")
        sentence = m.parse(sentence)
        wakati = sentence.split()
        if i in wakati:
            temp.append((i,sentence,1))
        else:
            temp.append((i,sentence,0))
new_df = pd.DataFrame({"word":[i[0] for i in temp],"sentence":[i[1] for i in temp],"wakati":[i[2] for i in temp]})
new_df.to_csv("new_df.csv",index=False)