import pandas as pd
from glob import glob
from tqdm import tqdm

f_names = glob("./csv_pack*")
kata = []
mid = []
hira = []
line_info = []
line_info_n = []
line_info_k = []
line_info_n_k = []

for f_name in f_names:
    kata.extend(glob(f_name + "*kata.csv"))
    line_info.extend(glob(f_name + "*line_info.csv"))
    mid.extend(glob(f_name + "*mid.csv"))
    hira.extend(glob(f_name + "*[A-Z].csv"))
    line_info_n.extend(glob(f_name + "*line_info_n.csv"))
    line_info_k.extend(glob(f_name + "*line_info_k.csv"))
    line_info_n_k.extend(glob(f_name + "*line_info_n_k.csv"))

#To process other csv files change the "hira" in for loop
#to another csv_file typ　[kata,line_info,mid]
#["kata","line_info","mid"]
#for csv_cat,st in tqdm(zip([line_info_n],["line_info_n"])):

for csv_cat,st in tqdm(zip([hira,kata,mid,line_info,line_info_n,line_info_k,line_info_n_k],["hria","kata","mid","line_info","line_info_n","line_info_k","line_info_n_k"])):
    df = pd.DataFrame()
    for csv_file in tqdm(csv_cat):
        try:
            df_temp = pd.read_csv(csv_file)
            df_temp.index = [csv_file.lstrip(f_name).rstrip(".csv")]
            df = pd.concat([df,df_temp])
        except:
            pass
    df.to_csv(f_name + st +".csv")
