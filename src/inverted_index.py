import os
import re
from collections import defaultdict
import numpy as np
from nltk.tokenize import sent_tokenize, word_tokenize

class InvertedIndex:
    def __init__(self, directory, stopwords, stemmer, save=True, name='ii'):
        self.directory = directory
        self.stopwords = stopwords
        self.stemmer = stemmer
        self.save = save
        self.name = name
        self.id_to_file = {}
        self.index = defaultdict(lambda: {'count': [], 'words': set()}) # stemmed index
        self.windex = defaultdict(lambda: {'count': [], 'postings': set(), 'rotations':set()}) # word index
        self.tgi = defaultdict(lambda: set())
        self.construct()
        self.construct_tgi()
        
    def produce_rotations(self, word):
        term = "$" + word
        res = [term]
        for i in range(len(word) - 1):
            term = term[-1] + term[:-1]
            res.append(term)
        return res
    
    def construct(self):
        for i, filename in enumerate(os.listdir(self.directory)):
            self.id_to_file[i] = filename
            with open(os.path.join(self.directory, filename), 'rt') as original:
                sents = sent_tokenize(original.read())
                for s in sents:
                    for w in word_tokenize(s):
                        if re.match("^[-'a-zA-Z]+$", w): # if it is a proper term
                            w = w.lower()
                            stemmed = self.stemmer.stem(w)
                            if stemmed not in self.stopwords:
                                    self.index[stemmed]['words'].add(w)
                                    self.windex[w]['postings'].add(i)
                            
        
        for t in self.index.keys():
            postings = set()

            for w in self.index[t]['words']:
                self.windex[w]['count'] = len(self.windex[w]['postings'])
                postings|=set(self.windex[w]['postings'])
                self.windex[w]['rotations'] = set(self.produce_rotations(w))
            self.index[t]['count'] = len(postings)

    def construct_tgi(self):
        for i in self.index.keys():
            for j in self.index[i]['words']:
                for k in range(len(j) - 1):
                    self.tgi[j[k:k+2]].add(i) # storing stems