f_name = "naka_result"

import os
os.system("ls")
with open(f_name + ".txt","r") as f:
    with open(f_name + "-mid.txt","w") as f2:
        temp = []
        for line in f:
            temp.append(line.rstrip("\n"))
        for i in range(len(temp)):
            for j in range(len(temp)):
                if temp[i][len(temp[i])//2:] != temp[j][len(temp[j])//2:]:
                    print(temp[i] + temp[j])
                    f2.write(temp[i] + temp[j] + "\n")
                else:
                    pass