import nltk.tree
import random
from corpusIterator import CorpusIterator_PTB
from createCounterfactGrammar import createCounterfactGrammar
from estimateTradeoffHeldout import calculateMemorySurprisalTradeoff
from estimateDepLength import calculateSentenceDepLength

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

def loadCorpus(CorpusIterator):
    corpus_cached = {}
    print(type(CorpusIterator))
    corpus_cached["train"] = CorpusIterator("PTB", "train")
    corpus_cached["dev"] = CorpusIterator("PTB", "dev")

    train_data = []
    dev_data = []

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
    return train_data, dev_data, corpus_cached


def calcILDL(train_data, dev_data, corpus_cached, args):
    '''
    Calculates measures of IL and DL from given corpus
    '''
    # IL is measured as the area under memory-surprisal curve (AUC)
    auc, devSurprisalTable = calculateMemorySurprisalTradeoff(train_data, dev_data, args) # (also prints mis, the difference between surprisals calculated with N = i vs. N = i + 1)
    #print('AUC:', auc)
    #print('average surprisals in dev set:', devSurprisalTable)

    # Calculate DL
    sum = 0
    counter = 0
    for tree, sentence_with_dependencies in corpus_cached["dev"].iterator():
        sum += calculateSentenceDepLength(sentence_with_dependencies)
        counter += 1
    average_dep = sum / counter
    #print('average dep length:', average_dep) # prints average dependency length for a sentence in the dev set

    return auc, average_dep, surp_table

def compareCorpora():
    og_train_data, og_dev_data, og_corpus_cached = loadCorpus(CorpusIterator_PTB)
    createCounterfactGrammar()
    cf_train_data, cf_dev_data, cf_corpus_cached = loadCorpus(CorpusIterator_PTB)
    # Counterfact_CorpusIterator = createCounterfactGrammar()
    # cf_train_data, cf_dev_data = loadCorpus(Counterfact_CorpusIterator)

    og_auc, og_dep, og_surp_table = calcILDL(og_train_data, og_train_data, og_corpus_cached, args)
    cf_auc, cf_dep, cf_surp_table = calcILDL(cf_train_data, cf_dev_data, cf_corpus_cached, args)
    print('og: ', og_auc, og_dep)
    print('cf: ', cf_auc, cf_dep)

compareCorpora()