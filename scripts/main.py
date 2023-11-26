from corpusIterator import CorpusIterator_PTB
corpus_cached = {} #initializes dictionary
corpus_cached["train"] = CorpusIterator_PTB("PTB", "train")
corpus_cached["dev"] = CorpusIterator_PTB("PTB", "dev")

train_data = []
dev_data = []

## THINK MORE ABOUT WHAT WE WANT TO TRAIN CORPUS ON (e.g. incl punctuation? sentence breaks? new doc?)

for tree, sentence_with_dependencies in corpus_cached["train"].iterator():
    train_data.append('SOS')
    for word in sentence_with_dependencies:
        train_data.append(word['word'])
    train_data.append('PAD')

for tree, sentence_with_dependencies in corpus_cached["dev"].iterator():
    dev_data.append('SOS')
    for word in sentence_with_dependencies:
        dev_data.append(word['word'])
    dev_data.append('PAD')


print(counter)
import random
from estimateTradeoffHeldout import calculateMemorySurprisalTradeoff

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--language", dest="language", type=str)
parser.add_argument("--instance", dest="instance", type=str, default="")
parser.add_argument("--group", dest="group", type=str, default="RANDOM")
parser.add_argument("--model", dest="model", type=str, default=str(random.randint(1000, 10000000)))
parser.add_argument("--alpha", dest="alpha", type=float, default=1.0)
parser.add_argument("--gamma", dest="gamma", type=int, default=1)
parser.add_argument("--delta", dest="delta", type=float, default=1.0)
parser.add_argument("--cutoff", dest="cutoff", type=int, default=2)
parser.add_argument("--idForProcess", dest="idForProcess", type=int, default=random.randint(0,10000000))

args=parser.parse_args()

auc, devSurprisalTable = calculateMemorySurprisalTradeoff(train_data, dev_data, args) # (also prints mis, the difference between surprisals calculated with N = i vs. N = i + 1)
print(auc)
print(devSurprisalTable)

# CODE TO CALCULATE AVERAGE DEPENDENCY LENGTH
from estimateDepLength import calculateSentenceDepLength

sum = 0
counter = 0
for tree, sentence_with_dependencies in corpus_cached["dev"].iterator():
    sum += calculateSentenceDepLength(sentence_with_dependencies)
    counter += 1
average = sum / counter
print(average)


# # small batch testing
# exSum = 0
# exCounter = 0
# for i in range(0, 10):
#     sentence = corpus_cached['dev'].getSentence(i)
#     depLength = calculateSentenceDepLength(sentence[1])
#     exSum += depLength
#     exCounter += 1
#
#     print("dep length:" + str(depLength))
#     print("sum so far: " + str(exSum))
#     print("total # of sentences so far: " + str(exCounter))
# average = exSum / exCounter
# print("AVE. DEP. LENGTH: " + str(average))



