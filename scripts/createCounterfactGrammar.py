from nltk.corpus import ptb
from nltk.tree import Tree

# Given tree position and index of moved item, find trace corresponding to item. Return tree position of trace


def searchTree(tree):
    # print(type(tree))
    # print("label: " + tree.label())

    # If the tree only has leaves as children, return
    if tree.height() == 2: return

    if tree.label().startswith("WH"):
        label = tree.label()
        word = tree[0] # stores the wh-word and pos tag

        # stores the index of the WH-phrase
        index = ""
        for char in label:
            if char.isDigit():
                index += char
        index = int(index)

        # search the whole tree from the root
        # if its entry contains '*T*-' plus the number ----- Q: are there any double-extracted WH words? i.e. do i need to further search

        ## MODIFY THE TREE ##
        # - replace the word entry with the wh-word
        # - replace the label with the WH label
        # - erase the branch prev containing the moved word

        ## MODIFY THE DEPENDENCY ENTRY ## Identify the corresponding sentence in dependency version
        # - identify where (after which index) in the tree the trace is located
        # - change the index of the wh-word to what it should be after moved
        # - for each word after wh, make sure its sorted. once reaching the index before the target, insert the entry

    for child in tree:
        searchTree(child)

