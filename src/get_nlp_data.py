import pandas as pd
from scorer import Scorer
import datetime as dt


def get_nlp_data(path):

    data = pd.read_pickle(path)

    scorer = Scorer()

    data['nlp_doc'] = data['definition'].apply(
                        lambda x: add_nlp_doc(x, scorer))

    return data


def pickle_nlp_data(data, path):

    # get date that the script was run
    today = dt.datetime.today().strftime('%y%m%d')

    filename = "{}_def_nlp.pkl".format(today)

    # save dataframe to pickle
    data.to_pickle(path + filename)


def add_nlp_doc(definition, nlp_model):
    if type(definition) == str:
        return nlp_model.nlp(definition)
    else:
        return None
