# given one sentence in conllu format (list of dicts), calculate the sentence's dependency length
# input: conllu-parsed sentence, as a list of dicts
# return: dependency length of the sentence (int)
def calculateSentenceDepLength(sentence):
    sum = 0
    for word in sentence:
        if word['head'] == 0:
            continue
        sum += abs(word['index'] - word['head'])
        # print("from " + word['word'] + " to " + sentence[word['head'] - 1]['word'] + ": " + str(abs(word['index'] - word['head'])))
    return sum


## NOT USED
# given data comprising of (tree, dependency parsed sentence), calculate average dependency length of a sentence
# input: iterable of tuples containing tree and dependency-parsed sentence
# return: average dependency length of a sentence (int)
def calculateAveDepLength(sentences):
    sum = 0
    for sentence in sentences:
        sum += calculateSentenceDepLength(sentence[1])
    average = sum / len(sentences)
    return average