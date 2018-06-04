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
        root_score, root_top_match = self.get_top_match(d_roots, u_roots)
        # get sentence similarity score
        sent_sim = self.cos_sim(u_doc.vector, d_doc.vector)

        # get bonus multiword match score
        mw_score, mw_top_match = self.get_top_match(d_mw, u_mw)

        print("root score: {}".format(root_score))
        print("sentence similarity score: {}".format(sent_sim))
        print("bonus score: {}".format(mw_score))

        total_score = root_score * sent_sim + mw_score

        print("total calculated score: {}".format(total_score))

        score_dict = {
            "root_words": root_top_match,
            "sent_sim": round(sent_sim, 3),
            "bonus": mw_top_match,
            "total": round(total_score, 3)
        }

        return score_dict

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

        Arguments:
            d_list (list): list of words from definition
            u_list (list): list of words from user submission

        Key Variables:
            a_list (list): shorter list of words
            b_list (list): longer list of words
        """

        # get root match score
        top_matches = {}
        if len(d_list) < len(u_list):
            a_list, b_list = d_list, u_list
        else:
            b_list, a_list = d_list, u_list

        for a_item in a_list:
            a_item = self.nlp(a_item)
            scores = []
            if len(b_list) > 0:
                for idx, b_item in enumerate(b_list):
                    b_item = self.nlp(b_item)
                    scores.append(self.cos_sim(b_item.vector, a_item.vector))
                    # replace nans with -1
                    scores = ([score if ~np.isnan(score) else -1
                              for score in scores])
            if len(scores) > 0:
                idx_of_top_match = scores.index(max(scores))
                top_match_word = b_list.pop(idx_of_top_match)
                top_matches[(a_item, top_match_word)] = max(scores)

        if len(top_matches) > 0:
            top_match_words = sorted(top_matches.items(), key=lambda x: x[1],
                                     reverse=True)
            if len(top_match_words) > 3:
                top_match_words = top_match_words[:3]
            top_match_words = [x[0] for x in top_match_words if x[1] > 0.75]
            print(top_match_words)
            top_scores = top_matches.values()
            print(top_scores)
            match_score = sum(top_scores) / len(top_scores)
            return match_score, top_match_words
        else:
            return 0, None

    def cos_sim(self, a_vec, b_vec):
        """Calculates and returns the cosine similarity value
        """
        return (np.sum((a_vec * b_vec))
                / (np.sqrt(np.sum((a_vec ** 2)))
                   * np.sqrt(np.sum((b_vec ** 2)))))
