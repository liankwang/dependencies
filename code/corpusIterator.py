# from https://www.asc.ohio-state.edu/demarneffe.1/LING5050/material/structured.html
header = ["index", "word", "lemma", "posUni", "posFine", "morph", "head", "dep", "_", "_"]

from nltk.corpus import ptb
import os
path = os.getcwd() + '/../data/'

##### READING TREE FORMAT PTB #####
def addTrees(sec, trees):
    secNum = ("" if sec >= 10 else "0") + str(sec)

    # creates list of names of files in the given section folder ("wsj_0001.mrg" etc.)
    files = sorted(os.listdir(path + 'wsj/' + secNum))

    # for each filename in list of filenames
    for name in files:
        for tree in ptb.parsed_sents("wsj/" + secNum + "/" + name):
            # leaves = []
            # for x in tree.leaves():
            #     if "*-" not in x and (not x.startswith("*")) and x not in ["0", "*U*", "*?*"]:
            #         if x == "-LRB-":
            #             x = "("
            #         elif x == "-RRB-":
            #             x = ")"
            #         else:
            #             x.replace("\/", "/").replace("\*","*")
            #     leaves.append(x)
            # leaves = " ".join(leaves)
            # print("leaves: " + leaves)

            leaves = " ".join(
                [("(" if x == "-LRB-" else (")" if x == "-RRB-" else x.replace("\/", "/").replace("\*", "*"))) for x in
                 tree.leaves() if "*-" not in x and (not x.startswith("*")) and x not in ["0", "*U*", "*?*"]])
            if leaves not in deps:  # only applies to one sentence in the training partition
                #print(leaves)
                continue

            trees.append((tree, deps[leaves]))
        # deps is a dictionary of sentences read from the conllu format,
        # each sentence-item is a (key: value) pair that is (list of words: conllu dependency representation)
        # leaves is a list of all words. calling deps[leaves] gives its conllu dependency rep
        # therefore trees stores a tuple of (PTB format tree, conllu format dependency entry)


# reads sections of PTB into trees (with addTrees() defined above) according to partition (train, dev, valid, test)
def getPTB(partition):  # where partition indicates what sections of the data to use based on goal for use
    trees = []
    if partition == "train":
        sections = range(0, 19)  # (0, 19)
    elif partition in ["dev", "valid"]:
        sections = range(21, 22)  # 19, 20, 21
    elif partition == "test":
        sections = range(22, 23)  # 22, 23, 24
    for sec in sections:  ## MODIFIED FOR FIDDLING PURPOSES; RESTORE TO "for sec in sections:"
        addTrees(sec, trees)
    return trees


##### READING UD-CONVERTED DEPENDENCY FORMAT OF PTB #####
import os
import random
import sys

# reads the conllu-conversion of PTB into a list (deps) containing, for each sentence, a list of its words and its conllu format
with open(path + "ptb-ud2.conllu.txt", "r") as inFile:
    # store each double-line-break (corresponding to one sentence) in the conllu file into a list deps
    deps = inFile.read().strip().split("\n\n")

# for each unit in deps (i.e. sentence in ptb)
for i in range(len(deps)):
    words = []
    # for each word in sentence deps[i]
    for x in deps[i].split("\n"):
        # split x based on tabs (i.e. each column field for a word entry. field [1] is the word/form field
        words.append(x.split("\t")[1])
    words = " ".join(words)
    # words = " ".join([x.split("\t")[1] for x in deps[i].split("\n")])
    # update deps[i] to store a tuple containing the string of words and the original dependency-annotated fields of the sentence
    deps[i] = (words, deps[i])

# at this point, deps looks like: [(words[0], deps[0]), (words[1], deps[1]), ...)]
# convert deps into a dictionary where the key is the string of words in a sentence deps[i], and the value is the dependency representation (in conllu fields)
deps = dict(deps)
print(len(deps))  # length of this dictionary should == # of sentences in ptb.conllu file
print("Done reading deps")

##### COMBINED CORPUS ITERATOR #####
class CorpusIterator_PTB():
    def __init__(self, language, partition="train"):
        data = getPTB(
            partition)  # return type of getPTB() is the list trees(), comprised of tuples of (ptb tree, conllu representation)
        #      if shuffleData:
        #       if shuffleDataSeed is None:
        #         random.shuffle(data)
        #       else:
        #         random.Random(shuffleDataSeed).shuffle(data)

        self.data = data
        self.partition = partition
        self.language = language
        assert len(data) > 0, (language, partition)

    def permute(self):
        random.shuffle(self.data)

    def length(self):
        return len(self.data)

    def getSentence(self, index):
        result = self.processSentence(self.data[index])
        return result

    def iterator(self):
        for sentence in self.data:
            yield self.processSentence(
                sentence)  # yields the return value (tuple (tree, sentence i.e. list of dicts) ) for each sentence without exiting function

    # processes sentence in conllu format into usable data structure
    def processSentence(self, sentenceAndTree):
        tree, sentence = sentenceAndTree  # tree = ptb tree; sentence = conllu representation
        # prelims:
        # map(function, iterable) applies the function to every item of the iterable; returns list of results
        # lambda defines func(x) that is defined by x.split("\t")
        #
        # splits each conllu sentence by line, into word entries
        # for each word entry of the sentence, splits it by tab, into fields of that word entry
        # -> each word becomes a list of fields
        # -> sentence becomes a list of words (i.e. a list of lists of fields)
        sentence = list(map(lambda x: x.split("\t"), sentence.split("\n")))
        result = []

        # for each word in the sentence:
        for i in range(len(sentence)):
            # sentence[i][j] where [i] is the index of the word entry and [j] is the field in that word entry
            if sentence[i][0].startswith("#"):  # comment line
                continue  # continue moves on to the next i in range (rather than break, which exits the loop completely)
            if "-" in sentence[i][
                0]:  # if index is NUM-NUM (mostly for agglutinated morphology representing multiple forms)
                continue
            if "." in sentence[i][0]:  # for empty nodes in ellipsis in enhanced dependencies
                continue

            # enumerate returns a  list of (index of item, item), where index is generated by counting.
            # i.e. [(0, 'index'), (1, 'word'), ...]
            # convert each word item, sentence[i], to a dict with
            # (name of field (e.g. 'lemma') : value corresponding to that field in the word)
            sentence[i] = dict([(y, sentence[i][x]) for x, y in enumerate(header)])
            sentence[i]["head"] = int(sentence[i]["head"])
            sentence[i]["index"] = int(sentence[i]["index"])
            sentence[i]["word"] = sentence[i]["word"].lower()
            if self.language == "Thai-Adap":
                assert sentence[i]["lemma"] == "_"
                sentence[i]["lemma"] = sentence[i]["word"]
            if "ISWOC" in self.language or "TOROT" in self.language:
                if sentence[i]["head"] == 0:
                    sentence[i]["dep"] = "root"

            #           if self.splitLemmas:
            #             sentence[i]["lemmas"] = sentence[i]["lemma"].split("+")

            #         if self.storeMorph:
            #           sentence[i]["morph"] = sentence[i]["morph"].split("|")

            #       if self.splitWords:
            #         sentence[i]["words"] = sentence[i]["word"].split("_")

            sentence[i]["dep"] = sentence[i]["dep"].lower()

            result.append(sentence[i])  # result is the new list of word items in dict format
        #              print sentence[i]
        return (tree, result)
