import pandas as pd
from glob import glob
from tqdm import tqdm

f_name = "./csv_pack_vrgame/"
kata = glob(f_name + "*kata.csv")
line_info = glob(f_name + "*line_info.csv")
mid = glob(f_name + "*mid.csv")
hira = glob(f_name + "*[A-Z].csv")
line_info_n = glob(f_name + "*line_info_n.csv")

line_info_k = glob(f_name + "*line_info_k.csv")
line_info_n_k = glob(f_name + "*line_info_n_k.csv")

#To process other csv files change the "hira" in for loop
#to another csv_file typ　[kata,line_info,mid]
#["kata","line_info","mid"]
#for csv_cat,st in tqdm(zip([line_info_n],["line_info_n"])):

for csv_cat,st in tqdm(zip([hira],["hria"])):
    df = pd.DataFrame()
    for csv_file in tqdm(csv_cat):
        try:
            df_temp = pd.read_csv(csv_file)
            df_temp.index = [csv_file.lstrip(f_name).rstrip(".csv")]
            df = pd.concat([df,df_temp])
        except:
            pass
    df.to_csv(f_name + st +".csv")