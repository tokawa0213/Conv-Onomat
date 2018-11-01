from bs4 import BeautifulSoup
import requests
import re
import os
import glob
import shutil

# time_span = input("Choose from [] :")
# genre = input("Choose from [] :")

"""
nコード
nXXXXYY
XXXX:
・数値部:0000〜9999
YY:
・文字部:a〜z
a=0, b=1 ... z=25
桁数は右から1,2...と数える

・文字部一桁を数値に変換
9999*26^現在の桁数-1*文字部一桁

例:n1000cb
・数値部:1000
・文字部:cb
1桁目:b
2桁目:c
"""

time_span = "年間"
#genre = "ヒューマンドラマ〔文芸〕"
#exclude: "童話〔その他〕""推理〔文芸〕""純文学〔文芸〕""ホラー〔文芸〕""ヒューマンドラマ〔文芸〕"
genre_list = ["宇宙〔SF〕"]
for genre in genre_list:
    URL = "https://yomou.syosetu.com/rank/genretop/"
    URL2 = "https://yomou.syosetu.com/rank/genrelist/"
    r = requests.get(URL)
    soup = BeautifulSoup(r.content, "html.parser")
    h = soup.find_all(class_="genreranking_ll")
    for i in h:
        m = re.match('<a href="/([^"]+)">' + time_span + genre + "ランキングを見る</a>", str(i.a))
        if (m != None):
            URL2 += m.groups()[0]
    r = requests.get(URL2)
    soup = BeautifulSoup(r.content, "html.parser")

    if os.path.exists(time_span+genre) == False:
        os.mkdir(time_span+genre)

    for i in range(1, 101):
        best1 = soup.find(id="best" + str(i)).get("href")
        best1 = best1.lstrip("https://ncode.syosetu").rstrip("/")
        os.system("python3 ./narouTo3.py " + best1[2:] + " --aozora")

    file_list = glob.glob("narouTo3/*")
    print(file_list)

    for i in file_list:
        if glob.glob(i) == []:
            shutil.move(i, time_span + genre)
        else:
            try:
                url = "https://ncode.syosetu.com/"
                ID = i.lstrip("narouTo3/")
                print("Refilled " + ID)
                r = requests.get(url + ID + "/")
                soup = BeautifulSoup(r.content, "html.parser")
                with open("narouTo3/" + ID + "/" + ID, "w") as f:
                    f.write(soup.find(id="novel_honbun").text)
                shutil.move(i, time_span + genre)
            except:
                shutil.move(i, time_span + genre)