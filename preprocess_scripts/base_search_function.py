from tqdm import tqdm
import jaconv
import re

def search_inside_sentence(data,ono_lis_st,ono_counter,option,n):
    with open(data, "r") as f:
        for line in tqdm(f):
            if n == True:
                line = line.rstrip("\n")
            if option == "mid":
                # convert katakana into hiragana
                line = jaconv.kata2hira(line)
                for i in re.findall(ono_lis_st, line):
                    ono_counter[i] += 1
                    # ono_counter = {"pachipachi":1,...}
                    # story = book_id
            elif option == "line_info_n_k":
                # convert katakana into hiragana
                # line = jaconv.kata2hira(line)
                for i in re.findall(ono_lis_st, line):
                    ono_counter[i].append(line)
                    # ono_counter = {"pachipachi":1,...}
                    # story = book_id
            elif option == "line_info_n":
                # convert katakana into hiragana
                line = jaconv.kata2hira(line)
                for i in re.findall(ono_lis_st, line):
                    ono_counter[i].append(line)
                    # ono_counter = {"pachipachi":1,...}
                    # story = book_id
            elif option == "line_info_k":
                # convert katakana into hiragana
                # line = jaconv.kata2hira(line)
                for i in re.findall(ono_lis_st, line):
                    ono_counter[i].append(line)
                    # ono_counter = {"pachipachi":1,...}
                    # story = book_id
            elif option == "line_info":
                # convert katakana into hiragana
                line = jaconv.kata2hira(line)
                for i in re.findall(ono_lis_st, line):
                    ono_counter[i].append(line)
                    # ono_counter = {"pachipachi":1,...}
                    # story = book_id
            elif option == "find_ono_hira":
                # convert katakana into hiragana
                line = jaconv.kata2hira(line)
                for i in re.findall(ono_lis_st, line):
                    ono_counter[i] += 1
                    # ono_counter = {"pachipachi":1,...}
                    # story = book_id
            elif option == "find_ono_kata":
                # convert katakana into hiragana
                # line = jaconv.kata2hira(line)
                for i in re.findall(ono_lis_st, line):
                    ono_counter[i] += 1
                    # ono_counter = {"pachipachi":1,...}
                    # story = book_id
            else:
                raise Exception
    return ono_counter