import os
import sys
import dill
import numpy as np
from nltk.corpus import stopwords
import nltk
from nltk.stem import PorterStemmer

from inverted_index import InvertedIndex
from query_handler import QueryHandler

def main():
    # Instantiate the stemmer and download the relevant nltk modules
    ps = PorterStemmer()

    # nltk.download()

    # Check if the inverted index table already exists
    if os.path.exists(os.path.join(os.path.abspath(os.path.dirname(os.path.dirname( __file__ ))), 'Saved', 'ii.pkl')):
        with open(os.path.join(os.path.abspath(os.path.dirname(os.path.dirname( __file__ ))), 'Saved', 'ii.pkl'), 'rb') as inp:
            ii = dill.load(inp)

    # If not, build it
    else:
        print('Building inverted index...')
        ii = InvertedIndex(stemmer = ps.stem, directory = 'Datasets/Shakespeare', stopwords = stopwords.words('english'))
        with open(os.path.join('Saved', 'ii.pkl'), 'wb') as out:
            dill.dump(ii, out, dill.HIGHEST_PROTOCOL)

    # Instantiate the query handler
    qh = QueryHandler(stemmer = ps.stem, ii = ii)

    # Until user types exit, keep evaluating queries
    while(True):
        query = input("\nEnter query: ")

        if query == "EXIT":
            break

        result = [ii.id_to_file[i] for i in qh.compute(query)]
        print(str(len(result)) + "/" + str(len(ii.id_to_file)) + " matches:")
        print(result)

if __name__ == "__main__":
    main()