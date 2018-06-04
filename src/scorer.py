import pandas as pd
import numpy as np
import spacy
import datetime as dt


class Scorer(object):
    """Scorer class object handles the comparison of the user query to the
    stored definition.
    """

    def __init__(self, nlp_model_name=None):
        """
        Arguments:
            nlp_model_name (str)

        """
        self._created_date = dt.datetime.today()
        self.raw_data = None
        self.nlp_data = None
        if nlp_model_name is None:
            self.nlp = spacy.load('en_core_web_lg')
        else:
            self.nlp = spacy.load(nlp_model_name)

    def load_raw_pickle(self, path):
        self.raw_data = pd.read_pickle(path)

    def load_nlp_pickle(self, path):
        self.nlp_data = pd.read_pickle(path)

    def score(self, word, user_subm):
        """Scores the user submission against the definition given by Wikipedia

        Arguments:
            word (str): the word that the user will attempt to define
            user_subm (str): the definition given by the user

        Return:
            total_score (float): total calculated score

        Score is calculated by:
        top noun chunks that match / total num of noun chunks in the definition
            multiplied by
        sentence similarity
            plus
        bonus:
            num of multiword noun chunks that match / total num of multiword nc
        """
        u_doc = self.get_first_sent(self.nlp(user_subm))
        # d_doc = self.get_first_sent(self.nlp(definition))
        mask = self.nlp_data['title'] == word
        d_doc = self.nlp_data.loc[mask]['nlp_doc'].values[0]
        d_doc = self.get_first_sent(d_doc)

        d_roots = self.get_lemma_roots(d_doc)
        d_mw = self.get_mw_nc(d_doc)

        u_roots = self.get_lemma_roots(u_doc)
        u_mw = self.get_mw_nc(u_doc)

        # get root match score
        root_score = self.get_top_match(d_roots, u_roots)
        # get sentence similarity score
        sent_sim = self.cos_sim(u_doc.vector, d_doc.vector)

        # get bonus multiword match score
        mw_score = self.get_top_match(d_mw, u_mw)

        print("root score: {}".format(root_score))
        print("sentence similarity score: {}".format(sent_sim))
        print("bonus score: {}".format(mw_score))

        total_score = root_score * sent_sim + mw_score

        print("total calculated score: {}".format(total_score))

        return total_score

    def get_first_sent(self, doc):
        sents = list(doc.sents)
        return sents[0]

    def get_lemma_roots(self, doc):
        """Get list of lemmatized roots of noun chunks.

        Arguments:
            doc (spaCy doc object)

        Returns:
            lemma_roots (list): list of lemmatized roots of noun chunks
        """
        nc = list(doc.noun_chunks)
        roots = [token.root.lemma_ for token in nc]

        return list(set(roots))

    def get_mw_nc(self, doc):
        """Get list of multiword noun chunks.

        Tokens with dependency of 'det' are removed.

        Arguments:
            doc (spaCy doc object)

        Returns:
            mw_nc (list): list of multiword noun chunks
        """
        mw_nc = list(doc.noun_chunks)

        # only keep multiword noun chunks
        pruned_mw = []
        for chunk in mw_nc:
            replace = []
            for token in chunk:
                # remove det tokens
                if token.dep_ is not 'det':
                    replace.append(token.lemma_)
            if len(replace) > 1:
                pruned_mw.append(" ".join(replace))

        return list(set(pruned_mw))

    def get_top_match(self, d_list, u_list):
        """Returns the scores for the matching items in two lists
        """
        # get root match score
        top_scores = []
        for d_item in d_list:
            d_item = self.nlp(d_item)
            scores = []
            for u_item in u_list:
                u_item = self.nlp(u_item)
                scores.append(self.cos_sim(u_item.vector, d_item.vector))
                scores = [score for score in scores if ~np.isnan(score)]
                print(scores)
            if len(scores) > 0:
                top_scores.append(max(scores))

        print("top_scores: {}".format(top_scores))
        print(sum(top_scores))
        print(len(top_scores))
        # print(sum(top_scores) / len(top_scores))
        return sum(top_scores) / len(top_scores)

    def cos_sim(self, a_vec, b_vec):
        """Calculates and returns the cosine similarity value
        """
        return (np.sum((a_vec * b_vec))
                / (np.sqrt(np.sum((a_vec ** 2)))
                   * np.sqrt(np.sum((b_vec ** 2)))))
