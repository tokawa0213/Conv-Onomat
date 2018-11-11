import MeCab

m = MeCab.Tagger()

with open("naka_result.txt") as f:
	with open("hanpuku.txt") as f2:
		li = []
		li2 = []
		for line in f:
			li.append(line.rstrip("\n"))
		for line in f2:
			li2.append(line.rstrip("\n"))
		print("NAKA: ",len(li)," MINE: ",len(li2))
		li = set(li)
		li2 = set(li2)
		print(li & li2)
		print(len(li&li2))

word = input("search collocating words : ")

with open("all_karai.csv") as f:
	l_s = []
	for line in f:
		l_word = []
		if(line.split(",")[0] == word):
			for s in line.split(","):
				res = m.parseToNode(s)
				while res:
					pos = res.feature.split(",")[0]
					base_word = res.feature.split(",")[6]
					if base_word != "*":
						l_word.append((base_word,pos))
					res = res.next
		if(l_word != []):
			l_s.append(l_word)

l_s_new = [item for sub in l_s for item in sub]
l_s_new_verb = [i[0] for i in l_s_new if i[1] == "動詞" or i[0] == word]
l_s_new_noun = [i[0] for i in l_s_new if i[1] == "名詞" or i [0] == word]
l_s_new_adj = [i[0] for i in l_s_new if i[1] =="形容詞" or i[0] == word]
l_s_new_adv = [i[0] for i in l_s_new if i[1] == "副詞" or i[0] == word]
l_s_new = [i[0] for i in l_s_new if i[1] == "副詞" or i[1] == "名詞"or i[1] == "動詞" or i[1] =="形容詞" or i[0] == word]

import nltk
for obj,str in zip([l_s_new,l_s_new_verb,l_s_new_noun,l_s_new_adj,l_s_new_adv],["ALL WORDS","ALL VERB","ALL NOUN","ALL ADJ","ALL ADV"]):
	print("-----",str,"-----")
	corpus = nltk.Text(obj)
	bigrams = nltk.bigrams(corpus)
	cfd = nltk.ConditionalFreqDist(bigrams)
	for key,value in sorted(dict(cfd[word]).items(),key = lambda x:x[1],reverse=True):
		if value != 1 and key !=word:
			print(key,value)
