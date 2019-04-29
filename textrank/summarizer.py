from .rank import pagerank
from .sentence import sent_graph
from .word import word_graph


class KeywordSummarizer:
    def __init__(self, sents=None, tokenize=None, min_count=2,
        window=-1, min_cooccurrence=2, vocab_to_idx=None,
        df=0.85, max_iter=30, bias=None, verbose=False):

        self.tokenize = tokenize
        self.min_count = min_count
        self.window = window
        self.min_cooccurrence = min_cooccurrence
        self.vocab_to_idx = vocab_to_idx
        self.df = df
        self.max_iter = max_iter
        self.bias = bias
        self.verbose = verbose

        if sents is not None:
            self.train_textrank(sents)

    def train_textrank(self, sents):
        g, self.idx_to_vocab = word_graph(sents,
            self.tokenize, self.min_count,self.window,
            self.min_cooccurrence, self.vocab_to_idx, self.verbose)
        self.R = pagerank(g, self.df, self.max_iter, self.bias).reshape(-1)
        if self.verbose:
            print('trained TextRank. n words = {}'.format(self.R.shape[0]))

    def keywords(self, topk=30):
        if not hasattr(self, 'R'):
            raise RuntimeError('Train textrank first or use summarize function')
        idxs = self.R.argsort()[-topk:]
        keywords = [(self.idx_to_vocab[idx], self.R[idx]) for idx in reversed(idxs)]
        return keywords

    def summarize(self, sents, topk=30):
        self.train_textrank(sents)
        return self.keywords(topk)


class KeysentenceSummarizer:
    """
    Arguments
    ---------
    sents : list of str
        Sentence list
    tokenize : callable
        Tokenize function: tokenize(str) = list of str
    min_count : int
        Minumum frequency of words will be used to construct sentence graph
    min_sim : float
        Minimum similarity between sentences in sentence graph
    similarity : callable or str
        similarity(s1, s2) returns float
        s1 and s2 are list of str.
        available similarity = [callable, 'cosine', 'textrank']
    vocab_to_idx : dict or None
        Vocabulary to index mapper
    df : float
        PageRank damping factor
    max_iter : int
        Number of PageRank iterations
    bias : None or numpy.ndarray
        PageRank bias term
    verbose : Boolean
        If True, it shows training progress
    """
    def __init__(self, sents=None, tokenize=None, min_count=2,
        min_sim=0.3, similarity=None, vocab_to_idx=None,
        df=0.85, max_iter=30, bias=None, verbose=False):

        self.tokenize = tokenize
        self.min_count = min_count
        self.min_sim = min_sim
        self.similarity = similarity
        self.vocab_to_idx = vocab_to_idx
        self.df = df
        self.max_iter = max_iter
        self.bias = bias
        self.verbose = verbose

        if sents is not None:
            self.train_textrank(sents)

    def train_textrank(self, sents):
        """
        Arguments
        ---------
        sents : list of str
            Sentence list

        Returns
        -------
        None
        """
        g = sent_graph(sents, self.tokenize, self.min_count,
            self.min_sim, self.similarity, self.vocab_to_idx, self.verbose)
        self.R = pagerank(g, self.df, self.max_iter, self.bias).reshape(-1)
        if self.verbose:
            print('trained TextRank. n sentences = {}'.format(self.R.shape[0]))

    def summarize(self, sents, topk=30):
        """
        Arguments
        ---------
        sents : list of str
            Sentence list
        topk : int
            Number of key-sentences to be selected.

        Returns
        -------
        keysents : list of tuple
            Each tuple stands for (sentence index, rank, sentence)

        Usage
        -----
            >>> from textrank import KeysentenceSummarizer

            >>> summarizer = KeysentenceSummarizer(tokenize = tokenizer, min_sim = 0.5)
            >>> keysents = summarizer.summarize(texts, topk=30)
        """
        if not hasattr(self, 'R'):
            self.train_textrank(sents)
        elif len(sents) != self.R.shape[0]:
            raise RuntimeError('Trained sentence must be re-inserted')
        idxs = self.R.argsort()[-topk:]
        keysents = [(idx, self.R[idx], sents[idx]) for idx in reversed(idxs)]
        return keysents
