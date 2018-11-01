with open("hiragana_list.txt","r") as f:
    with open("hanpuku.txt","w") as f2:
        for line in f:
            line = line.rstrip("\n")
            temp = len(line)
            if temp == 4 or temp == 6 or temp == 8:
                if line[:(temp//2)] == line[(temp//2):]:
                    line = line[:(temp//2)] + line[(temp//2):] + "\n"
                    f2.write(line)