import collections
from collections import defaultdict
import numpy as np

class QueryHandler:
    """
    This class is used to handle the given string query.

    Attributes
    ----------

    """
    def __init__(self, stemmer):
        """
        Function Constructor
        """
        self.symbols = {}
        self.stemmer = stemmer

    def rotate(self, wildcard):
        """
        Function to rotate the string query. 

        Args
        ---- 
            wildcard    : query term input by user
        
        Returns
        -------

        """
        term = '$' + wildcard
        for i, l in enumerate(term, 1):
            if l == "*":
                return term[i:] + term[:i-1], True
        else:
            return wildcard, False    

    def union(self, p1, p2):
        """
        Method to find the OR of the two lists p1 and p2.

        Args
        ---- 
            p1  : First posting list
            p2  : Second posting list

        Returns
        ------- 
            res : list cotaining the OR of lists p1 and p2
        """
        res = set()
        res = (set(p1) | set(p2))
        return list(res)

    def inverse(self, p1, total):
        """
        Method to find the NOT of the given list p1.
        
        Args
        ---- 
            p1      : posting list to be inverted
            total   : the number of documents in corpus

        Returns
        -------

        """
        return [i for i in total if i not in p1]
    
    def intersection(self, p1, p2):
        """
        Method to find the AND of the two lists p1 and p2.

        Args
        ----
            p1  : First posting list
            p2  : Second posting list

        Returns
        -------
            res : List containing the AND of p1 and p2
        """
        res = set()
        res = (set(p1) & set(p2))
        return list(res)
    
    def and_not(self, p1, p2):
        """
        Method to find p1 AND NOT p2.

        Args
        ----
            p1  : First posting list
            p2  : Second posting list

        Returns
        -------
            res : list cotaining the result 'p1 AND NOT p2'
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
    
    def or_not(self, p1, p2, total):
        """
        Method to find p1 OR NOT p2.

        Args
        ---- 
            p1      : First posting list
            p2      : Second posting list
            total   : the number of documents in corpus

        Returns
        -------

        """    
        return self.union(p1, self.inverse(p2, total))
    
    def levenshtein_distance(self, word1, word2):
        """
        Method to calculate the edit distance between word1 and word2.

        Args
        ----
            word1   : First word
            word2   : Second word

        Returns
        -------

        """
        m = np.zeros((len(word1)+1, len(word2)+1))
        for j in range(len(word1)+1):
            m[0][j] = j
        for i in range(len(word2)+1):
            m[i][0] = i

        for i in range(1, len(word1)+1):
            for j in range(1, len(word2)+1):
                if word1[i-1] == word2[j-1]:
                    m[i, j] = m[i-1, j-1]
                else:
                    m[i, j] = 1 + min(m[i-1, j], min(m[i, j-1], m[i-1, j-1]))
        return m[len(word1), len(word2)]
    
    def spell_correct(self, misspelled, ii):
        """
        Method to get corrected spelling for a misspelled query word.

        Args
        ----
            misspelled  : string query term entered by user
            ii          : inverted index

        Returns
        -------

        """
        twograms = []
        for i in range(len(misspelled) - 1):
            twograms += ii.tgi[misspelled[i:i+2]]
        
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
                for w in ii.index[i]['words']: # for each word in that stem
                    if len(w)>=len(misspelled)-4 and len(w)<=len(misspelled)+4 : # if at most 4 chars away from misspelled word
                        d = self.levenshtein_distance(misspelled, w) # get distance
                        if d<=5: # if dist at most 5
                            ed[d].add(i) # add stem
        # print(ed)

        if not ed:
            return ""
        return max([(ii.index[x]['count'], x) for x in ed[min(list(ed.keys()))]])[1]
        
    
    def match(self, term, ii):
        """
        @Pranav Balaji
        """
        if term[0] == '@':
            return self.symbols[term]
        res = []
        rotated, is_wild = self.rotate(term)
        #print(rotated)
        if is_wild: # is a wildcard
            for i in ii.index.keys():
                for w in ii.index[i]['words']:
                    if len(w) >= len(term)-1:
                        for r in ii.windex[w]['rotations']:
                            if r[:len(rotated)] == rotated:
                                res = self.union(res, ii.windex[w]['postings'])
                                break
        else: # not a wildcard
            rotated = self.stemmer.stem(rotated)
            for i in ii.index.keys():
                if i == rotated:
                    for w in ii.index[i]['words']:
                        res = set(res)
                        res|= set(ii.windex[w]['postings'])
                    break
                    
        if not is_wild and not res: # misspelled word
            corrected = self.spell_correct(term, ii)
            # print(term + " is corrected to " + corrected)
            if corrected:
                return self.match(corrected, ii)
        
        return list(res)
    
    def evaluate_expr(self, expr, i, ii):
        """
        Method to evaluate boolean expression and output result of the query.

        Args
        ----
            expr    : given boolean expression to be evaluated
            i       : 
            ii      : inverted index 

        Returns
        -------

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
            self.symbols[new_symbol] = self.inverse(self.match(expr[1], ii), list(ii.id_to_file.keys()))
            return new_symbol

        else:
            if len(expr) == 1:
                self.symbols[new_symbol] = self.match(expr[0], ii)
                return new_symbol

            if expr[1] == 'and':
                if expr[2] == 'not':
                    self.symbols[new_symbol] = self.and_not(self.match(expr[0], ii), self.match(expr[3], ii))
                    return new_symbol

                else:
                    self.symbols[new_symbol] = self.intersection(self.match(expr[0], ii), self.match(expr[2], ii))
                    return new_symbol

            else:
                if expr[2] == 'not':
                    self.symbols[new_symbol] = self.or_not(self.match(expr[0], ii), self.match(expr[3], ii), list(ii.id_to_file.keys()))
                    return new_symbol

                else:
                    self.symbols[new_symbol] = self.union(self.match(expr[0], ii), self.match(expr[2], ii))
                    return new_symbol
            
    def compute(self, query, ii):
        """
        Method to evaluate precedence of brackets implemented using stacks.

        Args
        ----
            query   : input string query
            ii      : inverted index

        Returns
        -------

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
                        stack += list(self.evaluate_expr(expr[::-1], i, ii))
                        i += 1
                        break
        if stack:
            self.evaluate_expr("".join(stack), i, ii)
            i += 1
        return self.symbols['@' + str(i - 1)]