import glob
import shutil
from bs4 import BeautifulSoup
import requests

file_list = glob.glob("年間*")
print(file_list)

for i in file_list:
    for j in glob.glob(i+"/*"):
        if(glob.glob(j + "/*") == []):
            url = "https://ncode.syosetu.com/"
            ID = j.lstrip(i+"/*")
            print(ID)
            r = requests.get(url + ID + "/")
            soup = BeautifulSoup(r.content, "html.parser")
            with open(j + "/" + ID, "w") as f:
                f.write(soup.find(id="novel_honbun").text)