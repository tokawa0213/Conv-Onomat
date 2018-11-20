import pandas as pd

df = pd.read_csv("./PIC2n.csv")
print(df["P"].describe())

df2 = pd.read_csv("csv_pack_comedy/line_info.csv")
temp = df2["つーりん"]
temp = temp.dropna()

df3 = pd.read_csv("csv_pack_comedy/line_info_n.csv")
temp2 = df3["つーつー"]
temp3 = df3["りんりん"]
temp2 = temp2.dropna()
temp3 = temp3.dropna()

