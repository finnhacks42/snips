import numpy as np
import json
from collections import Counter
from itertools import filterfalse, pairwise

from gensim.models.phrases import Phrases, ENGLISH_CONNECTOR_WORDS, npmi_scorer

class Bigram:
    """
    An alternative to Phrases for finding bigrams, trigrams etc.
    
    This is a temporary fix for https://github.com/RaRe-Technologies/gensim/issues/3326
    
    Example usage
    ------------
    articles = [
        ['high', 'risk', 'of', 'default', 'raises', 'concern', 'at', 'the', 'central', 'bank', 'of', 'brazil'],
        ['high', 'school', 'students', 'demand', 'raises', 'in', 'pay', 'outside', 'the', 'central', 'bank', 'of', 'brazil'],
        ['concern', 'about', 'rising', 'prices', 'reducing', 'investment'],
        ['the', 'school', 'is', 'at', 'high', 'risk'],
        ['simple', 'noconnector', 'trigram'],
        ['simple', 'noconnector', 'trigram']
    ]
    
    model = Bigram().fit(articles)
    bigrammed = (a for a in model.transformed(articles,0.85))
    trigram = Bigram().fit(bigrammed)

    bigrammed = (a for a in model.transformed(articles,0.85))
    trigrammed = list((a for a in trigram.transformed(bigrammed,0.85)))
    
    
    """
    def __init__(self, min_threshold=0, connector_words = None, delim="_", bigrams=None):
        """
        Parameters
        -------------
        connector_words: list or set
            Words to ignore when generating bigrams.
            For example, in order find bigrams like 'bank_of_england' we want to ignore 'of'.
        
        min_threshold: float (default 0)
            The minimum threshold you may want use for this model.
            Bigrams scoring below this threshold will not be saved in the model.
            Lowering this value means you can explore a wider range of thresholds at transform time
            but increases memory/disk usage.
            
        delim: str (default '_')
            The delimiter to use to join identified bigrams.
            
        bigrams: optional {(str,str):float} 
            Map from bigram tuple to score. 
            Required only if you want to manually specify the bigrams rather than learn them via fit.
        """
        if connector_words is None:
            connector_words = ENGLISH_CONNECTOR_WORDS 
        self.connector_words = frozenset(connector_words)
        self.min_threshold = min_threshold
        self.delim = "_"
        self.bigrams = bigrams
         
    def _drop_word(self,word):
        return word in self.connector_words
    
    def save(self, filepath):
        """
        Save the model to json.
        
        Parameters
        ----------
        filepath: str or Path
            The path to write the file to.
        """
        if self.bigrams is None:
            raise ValueError('model has not been fit!')
        with open(filepath,'w') as f:
            data = {
                'bigrams':list(self.bigrams.items()), # json can't serialise dicts with tuples as keys
                'connector_words':list(self.connector_words), # or frozensets
                'delim':self.delim,
                'min_threshold':self.min_threshold
            }
            json.dump(data,f,indent=4)
    
    @classmethod        
    def load(cls, filepath):
        """Load a previously saved model from json."""
        with open(filepath,'r') as f:
            data = json.load(f)
            return cls(
                data['min_threshold'],
                data['connector_words'],
                data['delim'],
                {tuple(row[0]):row[1] for row in data['bigrams']}
            )
            
    def fit(self, stream_of_sentances, score_function=None, min_count=1):
        """
        Fit the model to score all identified bigrams.
        
        Parameters
        -----------
        stream_of_sentances: iterable/generator over lists of strings
            The text to fit the model on.
        
        score_function: (optional), func(int, int, int, int, int, int)->float
            A function to score bigram candidates. Will be passed:
                worda_count, wordb_count, bigram_count, len_vocab, min_count, corpus_word_count
            Stronger relationships between worda and wordb should yield higher values.
            
        min_count: int
            The minimum number of times a particular pair of words must be seen together to be scored.
            
        """
        
        if score_function is None:
            score_function = npmi_scorer
        words = Counter()
        bigrams = Counter()
        for s in stream_of_sentances:
            filtered = list(filterfalse(self._drop_word, s))
            words.update(filtered)
            bigrams.update(pairwise(filtered))
        
        corpus_word_count = words.total()
        result = {}
        for bigram, count in bigrams.items():
            if count >= min_count:
                score = score_function(
                    words[bigram[0]],
                    words[bigram[1]],
                    count,
                    len(words),
                    min_count,
                    corpus_word_count
                )
                if score > self.min_threshold:
                    result[bigram] = score
        
        self.bigrams = result
        return self
    
    def transformed(self, stream_of_sentances, threshold=None):
        """
        Apply the learned bigrams to the input text.
        
        Parameters
        -----------
        stream_of_sentances: iterable/generator over lists of strings
            The text to fit the model on.
            
        threshold: (optional) float
            The mimimum score a bigram must have to be applied.
            If not set, uses the minimum score for the model.
            
        Yields
        ------------
        transformed_stream: generator over list of strings
            the transformed input
        """
        if threshold is None:
            threshold = self.min_threshold
        for s in stream_of_sentances:
            s_transformed = []
            start_token = None
            in_between = []
            for word in s:
                if word in self.connector_words:
                    if start_token:
                        in_between.append(word)
                    else:
                        s_transformed.append(word)
                else: # not a connector word
                    if not start_token:
                        start_token = word
                    
                    else:
                        score = self.bigrams.get((start_token,word),-np.inf)
                        if score > threshold:
                            parts = [start_token] + in_between + [word]
                            s_transformed.append(self.delim.join(parts))
                            start_token = None
                                                                                 
                        else:
                            s_transformed.append(start_token)
                            s_transformed.extend(in_between)
                            start_token = word
                            
                        in_between = []
            
            if start_token:
                s_transformed.append(start_token)
                          
            yield s_transformed