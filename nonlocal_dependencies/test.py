list = ["a", "b", "c", "d", "e", "f"]

# goal: list = ["a", "c", "d", "b", "e", "f"]
list.insert(3, list.pop(1))
print(list)

# goal: list = ["a", "c", "e", "d", "b", "f"]
list.insert(2, list.pop(4))
print(list)

list2 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
list2.insert(19, list2.pop(12))
print(list2)

#########################################################

from corpusIterator import CorpusIterator_PTB
corpus_cached = {} #initializes dictionary
corpus_cached["train"] = CorpusIterator_PTB("PTB", "train")
corpus_cached["dev"] = CorpusIterator_PTB("PTB", "dev")

# # there are 1671 total sentences in section 21
# for i in range(380, 500):
#     sentence = corpus_cached['dev'].getSentence(i)
#     print(sentence)

# the sentence containing "... when the shah died"
wh_sentence = corpus_cached['dev'].getSentence(385)
print(wh_sentence)

from createCounterfactGrammar import searchTree
searchTree(wh_sentence[0])