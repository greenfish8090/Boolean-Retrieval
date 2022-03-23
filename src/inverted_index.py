import os
import re
from typing import Callable
from collections import defaultdict
import numpy as np
from nltk.tokenize import sent_tokenize, word_tokenize

class InvertedIndex:
    """A class to make the inverted index.
    
    Attributes
    ----------
        directory   : path to the dataset directory
        stopwords   : set of stopwords
        stemmer     : stemming function

    """

        def __init__(self, directory: str, stopwords: list, stemmer: Callable, save: bool = True, name: str = 'ii') -> None:
        """Class constructor.

        Args
        ----
            directory   : path to the dataset directory
            stopwords   : set of stopwords
            stemmer     : stemming function

        """

        self.directory = directory
        self.stopwords = stopwords
        self.stemmer = stemmer
        self.id_to_file = {}
        self.index = defaultdict(lambda: {'count': 0, 'words': set()}) # stemmed index
        self.windex = defaultdict(lambda: {'count': 0, 'postings': set(), 'rotations':set()}) # word index
        self.tgi = defaultdict(lambda: set())
        self.construct()
        self.construct_tgi()
        
    def produce_rotations(self, word: str) -> list:
        """Method to generate all rotations of a word.

        Args
        ----
            word    : word to make generate rotations for

        Returns
        -------
            res     : a list of all word rotations

        """

        term = "$" + word
        res = [term]
        for i in range(len(word) - 1):
            term = term[-1] + term[:-1]
            res.append(term)
        return res
    
    def construct(self) -> None:
        """
        Method to construct the inverted index.

        """

        for i, filename in enumerate(os.listdir(self.directory)):
            self.id_to_file[i] = filename
            with open(os.path.join(self.directory, filename), 'rt') as original:
                sents = sent_tokenize(original.read())
                for s in sents:
                    for w in word_tokenize(s):
                        if re.match("^[-'a-zA-Z]+$", w): # if it is a proper term
                            w = w.lower()
                            stemmed = self.stemmer(w)
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

    def construct_tgi(self) -> None:
        """
        Method to construct two-gram index.

        """
        
        for i in self.index.keys():
            for j in self.index[i]['words']:
                for k in range(len(j) - 1):
                    self.tgi[j[k:k+2]].add(i) # storing stems
