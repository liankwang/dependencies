from nltk.corpus import ptb
from nltk.tree import Tree
import nltk.tree
import os
from corpusIterator import CorpusIterator_PTB

# for smaller batch testing:
# path = os.getcwd() + '/data/wsj/00/wsj_0003.mrg'
# trees = []
# for tree in ptb.parsed_sents(path):
#     leaves = " ".join(
#         [("(" if x == "-LRB-" else (")" if x == "-RRB-" else x.replace("\/", "/").replace("\*", "*"))) for x in
#     tree.leaves() if "*-" not in x and (not x.startswith("*")) and x not in ["0", "*U*", "*?*"]])
#     trees.append(tree)

def restoreTrace(tree, sent, quest_count):
    '''
    Takes a question and restores the wh-words to their trace position
    Params:
        - sentence in PTB tree format
        - sentence in conllu format
    Returns:
        nothing
    '''
    # If the tree only has leaves as children, return
    if tree.height() in [0, 1, 2]: return
    # if 'taxpayers' in tree.leaves():
    #     print(tree)

    # if tree.label() == 'SBAR' and tree[0].label().startswith('WH') and tree[1].label() == 'SQ':
    #     print(tree)

    #print(tree)
    if not len(tree) < 2:
        if tree.label() == 'SBARQ' or (tree.label() == 'SBAR' and tree[0].label().startswith('WH') and tree[1].label() == 'SQ'):
            for i in range(0, len(tree)):
                if 'WH' in tree[i].label():
                    break
            label = tree[i].label()

            # Stores index of wh-phrase
            if 'WH' in label:
                quest_count += 1

                # keep track of trace index
                index = ""
                for char in label:
                    if char.isdigit():
                        index += str(char)
                #if index == "":
                    # this wh-phrase doesnt have a trace, so we should skip over it

                # Goes through the leaves in this tree to find and edit the trace
                for idx, leaf in enumerate(tree.leaves()):
                    if isinstance(leaf, str) and leaf == "*T*"+"-"+index:
                        # print('og')
                        # print(tree)
                        loc = tree.leaf_treeposition(idx)[:-2]
                        tree[loc] = tree[i]
                        #tree[loc].label = label
                        del tree[i]
                        # print('new')
                        # print(tree)
                        break

            # Note that this will only change 1) matrix wh-questions, and 2) embedded questions
            # - multiple questions in English are wh-in-situ except the first wh-element
            # - im ignoring relative clauses, as it seems weird to restore 'The child who Mary liked t', but thats perhaps part of why wh-in-situ have special RCs 

            # 11/26/23: to map indices from tree to ud, i can see which characters are ignored
            #  in the expression in corpusIterator where i get leaves

    for child in tree:
        restoreTrace(child, sent, quest_count)

    return quest_count, tree

def restoreUD(tree, sent, multi_exclude_counter):
    '''
    Given a restored tree, modify the conllu dependencies to reflect the new ordering. 
        - updates sent in corpus by new dependency representation reflecting new ordering
        - updates multi_exclude_counter if the sentence is excluded due to repeated wh-words 
            and updates that sent to be None type (these sentences will be accomodated in a later iteration)
    
    Params:
        - sentence in PTB tree format with restored wh-words to traces (type: nltk tree)
        - corresponding original sentence in conllu format (type: list of dicts)
    Returns:
        - 0 if the two sentences do not comprise the same words (shouldn't apply to anything in the corpus, since this is checked in corpusIterator)
        - 1 if the sentence was successfully updated
    
    NOTE: Currently the way this function handles repeated words is not optimal. There is room for error in restoration for non-questions, and it loses question data
          One problem with losing data is then this corpus does not form a minimal pair with the unrestored corpus... So perhaps instead of doing None type, 
          we should just use the original tree and sentence (i.e. check for multiple items in the restoreTrace step)
    '''
    
    # Collect list of words in restored tree and in conllu original sentence (order matters)
    words = []
    leaves = [("(" if x == "-LRB-" else (")" if x == "-RRB-" else x.replace("\/", "/").replace("\*", "*").lower())) for x in
                tree.leaves() if "*-" not in x and (not x.startswith("*")) and x not in ["0", "*U*", "*?*"]]
    for item in sent:
        words.append(item['word'])

    # Update current sent with new dependency representation
    if sorted(leaves) != sorted(words):
        print('mismatched words!')
        return 0
    elif leaves != words: # ordering is different, i.e. it's a tree with question we've modified  
        new_dependency = []
        for ind, word in enumerate(leaves): # for each word in the new ordering of leaves
            new_index = ind + 1
            ident_items = [] # to store identical words (implementation need)
            for item in sent:
                if item['word'] == word:
                    ident_items.append(item)

            # To add our new word to the dependency representation
            if len(ident_items) == 1: # if there are no repeats, then we safely add our item
                new_item = item
                new_item['index'] = new_index
                new_dependency.append(new_item)
            else: #
                # if the repeated item is not a question word, we add the one closest in index
                if ident_items[0]['word'] not in ['what', 'who', 'how', 'which', 'why', 'where']:
                    # we add the one closest in index
                    dist = 1000
                    for item in ident_items:
                        cur_dist = abs(item['index'] - ind)
                        if cur_dist < dist:
                            winner = item
                            dist = cur_dist
                    new_dependency.append(winner)
                else:
                    new_dependency = None
                    break

        # check if we got the same ordering now
        if new_dependency == None:
            multi_exclude_counter += 1
        
        sent = new_dependency
    return multi_exclude_counter, sent

def createCounterfactGrammar(partition):
    '''
    NEXT STEP: Make this return a new CorpusIterator class that uses the counterfactual corpus. The only change
    should be to instead of using getPTB to load a list of (tree, sentence_with_dependencies), use a list constructed
    in this code

    also do the same with dev and test sets
    '''
    corpus = CorpusIterator_PTB("PTB", partition)
    multi_exclude_counter = 0
    quest_count = 0
    cf_corpus = []
    for tree, sentence_with_dependencies in corpus.iterator():
        #nltk.draw.tree.draw_trees(tree)
        quest_count, new_tree = restoreTrace(tree, sentence_with_dependencies, quest_count)
        multi_exclude_counter, new_dependency = restoreUD(new_tree, sentence_with_dependencies, multi_exclude_counter)
        if new_dependency is not None:
            cf_corpus.append((new_tree, new_dependency))
        # if tree.label() == 'SBARQ':
        #    print(tree.leaves())
    print('number of questions restored in corpus: ', quest_count) 
    print('number of multiple questions excluded: ', multi_exclude_counter)
    
    return cf_corpus

# Mostly copied from CorpusIterator_PTB
class CorpusIterator_Counterfact():
    def __init__(self, language, partition="train"):
        data = createCounterfactGrammar(partition)
        self.data = data
        self.partition = partition
        self.language = language
        assert len(data) > 0, (language, partition)

    def permute(self):
        random.shuffle(self.data)

    def length(self):
        return len(self.data)

    def getSentence(self, index):
        #result = self.processSentence(self.data[index])
        result = self.data[index]
        return result

    def iterator(self):
        for sentence in self.data:
            #yield self.processSentence(sentence)  # yields the return value (tuple (tree, sentence i.e. list of dicts) ) for each sentence without exiting function
            yield sentence

    # no need for processSentence()