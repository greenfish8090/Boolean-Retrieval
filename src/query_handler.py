import collections
from collections import defaultdict
from typing import Callable
import numpy as np

class QueryHandler:
    """
    This class is used to handle the given string query.

    Attributes
    ----------
        stemmer     : stemming function
        ii          : inverted index

    """
    def __init__(self, stemmer: Callable, ii) -> None:
        """
        Function Constructor
        """
        self.symbols = {}
        self.stemmer = stemmer
        self.ii = ii
    
    def rotate(self, wildcard: str) -> tuple[str, bool]:
        """
        Function to rotate the string containing the wildcard until the '*' is at the end. If the input has no wildcard, it is returned
        as it is. A flag has_wild is also returned, which tells if the input had a wildcard.

        Args
        ---- 
            wildcard    : query term input by user
        
        Returns
        -------
           The rotated wildcard with the '*' at the end and the flag
        """
        term = '$' + wildcard
        for i, l in enumerate(term, 1):
            if l == "*":
                return term[i:] + term[:i-1], True
        else:
            return wildcard, False
        
    def union(self, p1: list, p2: list) -> list:
        """
        Method to find the OR of the two lists p1 and p2.

        Args
        ---- 
            p1  : First posting list
            p2  : Second posting list

        Returns
        ------- 
            List cotaining the OR of lists p1 and p2
        """
        res = set()
        res = (set(p1) | set(p2))
        return list(res)

    def inverse(self, p1:list) -> list:
        """
        Method to find the NOT of the given list p1.
        
        Args
        ---- 
            p1      : posting list to be inverted

        Returns
        -------
            Inverse of p1 with global set being the set of all documents
        """
        return [i for i in list(self.ii.id_to_file.keys()) if i not in p1]
    
    def intersection(self, p1: list, p2: list) -> list:
        """
        Method to find the AND of the two lists p1 and p2.

        Args
        ----
            p1  : First posting list
            p2  : Second posting list

        Returns
        -------
            List containing the AND of p1 and p2
        """
        res = set()
        res = (set(p1) & set(p2))
        return list(res)
    
    def and_not(self, p1: list, p2: list) -> list:
        """
        Method to find p1 AND NOT p2.

        Args
        ----
            p1  : First posting list
            p2  : Second posting list

        Returns
        -------
            List containing the result 'p1 AND NOT p2'
        """
        i = j = 0
        res = []

        while i < len(p1) and j < len(p2):
            if p1[i] == p2[j]:
                i += 1
                j += 1
            elif p1[i] < p2[j]:
                res.append(p1[i])
                i += 1
            elif p1[i] > p2[j]:
                j += 1
        if i < len(p1):
            res += p1[i:]

        return res
    
    def or_not(self, p1: list, p2: list) -> list:
        """
        Method to find p1 OR NOT p2.

        Args
        ---- 
            p1      : First posting list
            p2      : Second posting list

        Returns
        -------
            list containing the result 'p1 OR NOT p2'
        """    
        return self.union(p1, self.inverse(p2))
    
    def levenshtein_distance(self, word1: str, word2: str) -> int:
        """
        Method to calculate the edit distance between word1 and word2.

        Args
        ----
            word1   : First word
            word2   : Second word

        Returns
        -------
            Levenshtein distance between the two words
        """
        m = np.zeros((len(word1)+1, len(word2)+1))
        for j in range(len(word2)+1):
            m[0][j] = j
        for i in range(len(word1)+1):
            m[i][0] = i

        for i in range(1, len(word1)+1):
            for j in range(1, len(word2)+1):
                if word1[i-1] == word2[j-1]:
                    m[i, j] = m[i-1, j-1]
                else:
                    m[i, j] = 1 + min(m[i-1, j], min(m[i, j-1], m[i-1, j-1]))
        return int(m[len(word1), len(word2)])
    
    def spell_correct(self, misspelled: str) -> str:
        """
        Method to get corrected spelling for a misspelled query word.

        Args
        ----
            misspelled  : string query term entered by user

        Returns
        -------
            The most probable correct spelling
        """
        twograms = []
        for i in range(len(misspelled) - 1):
            twograms += self.ii.tgi[misspelled[i:i+2]]
        
        freqs = dict(collections.Counter(twograms)) # stem : no. of matching two-grams
        freqs = {k: v for k, v in reversed(sorted(freqs.items(), key=lambda item: item[1]))}
        # print(freqs)
        
        ff = defaultdict(lambda: []) # no.of matching two-grams: stem
        
        for k, v in freqs.items():
            ff[v].append(k)
        # print(ff)
            
        ed = defaultdict(lambda: set())
        
        for f in list(ff.keys())[:1]: # top two-gram matching word
            for i in ff[f]: # for each stem with frequency f
                for w in self.ii.index[i]['words']: # for each word in that stem
                    if len(w)>=len(misspelled)-4 and len(w)<=len(misspelled)+4 : # if at most 4 chars away from misspelled word
                        d = self.levenshtein_distance(misspelled, w) # get distance
                        if d<=5: # if dist at most 5
                            ed[d].add(i) # add stem
        # print(ed)

        if not ed:
            return ""
        return max([(self.ii.index[x]['count'], x) for x in ed[min(list(ed.keys()))]])[1]
        
    
    def match(self, term: str) -> list:
        """
        Gets the list of documents which have a particular term

        Args
        ----
            term  : the term optionally containing wildcard

        Returns
        -------
            The matching list of documents
        """
        if term[0] == '@':
            return self.symbols[term]
        res = []
        rotated, is_wild = self.rotate(term)
        #print(rotated)
        if is_wild: # is a wildcard
            matches = set()
            for i in self.ii.index.keys():
                for w in self.ii.index[i]['words']:
                    if len(w) >= len(term)-1:
                        for r in self.ii.windex[w]['rotations']:
                            if r[:len(rotated)] == rotated:
                                res = self.union(res, self.ii.windex[w]['postings'])
                                matches.add(w)
                                break
            print(term + " has been matched to " + ", ".join(matches))
        else: # not a wildcard
            rotated = self.stemmer(rotated)
            for i in self.ii.index.keys():
                if i == rotated:
                    for w in self.ii.index[i]['words']:
                        res = set(res)
                        res|= set(self.ii.windex[w]['postings'])
                    break
                    
        if not is_wild and not res: # misspelled word
            corrected = self.spell_correct(term)
            print(term + " is corrected to " + corrected)
            if corrected:
                return self.match(corrected)
        
        return list(res)
    
    def evaluate_expr(self, expr: str, i: int) -> str:
        """
        Method to evaluate boolean expression and store the output in a new index of the symbol table

        Args
        ----
            expr    : given elementary boolean expression to be evaluated
            i       : the new index for the symbol table

        Returns
        -------
            The index in the symbol table which has the result of the expression
        """
        # print("evaluating " + expr + " and storing as @" + str(i))
        # Possibilities are:
        # var or not var
        # var or var
        # var and not var
        # var and var
        # var
        # not var

        keywords = ["and", "or", "not"]
        expr = expr.split(" ")
        new_symbol = '@' + str(i)

        if expr[0] == "not":
            self.symbols[new_symbol] = self.inverse(self.match(expr[1]))
            return new_symbol

        else:
            if len(expr) == 1:
                self.symbols[new_symbol] = self.match(expr[0])
                return new_symbol

            if expr[1] == 'and':
                if expr[2] == 'not':
                    self.symbols[new_symbol] = self.and_not(self.match(expr[0]), self.match(expr[3]))
                    return new_symbol

                else:
                    self.symbols[new_symbol] = self.intersection(self.match(expr[0]), self.match(expr[2]))
                    return new_symbol

            else:
                if expr[2] == 'not':
                    self.symbols[new_symbol] = self.or_not(self.match(expr[0]), self.match(expr[3]))
                    return new_symbol

                else:
                    self.symbols[new_symbol] = self.union(self.match(expr[0]), self.match(expr[2]))
                    return new_symbol
            
    def compute(self, query: str) -> list:
        """
        Method to evaluate an entire query using a stack

        Args
        ----
            query   : input string query

        Returns
        -------
            List of matching documents
        """
        stack = []
        self.symbols = {}
        i = 0
        for c in query:
            if c != ')':
                stack.append(c)
            else:
                expr = ""
                while stack:
                    char = stack.pop()
                    if char != '(':
                        expr += char
                    else:
                        stack += list(self.evaluate_expr(expr[::-1], i))
                        i += 1
                        break
        if stack:
            self.evaluate_expr("".join(stack), i)
            i += 1
        return self.symbols['@' + str(i - 1)]
