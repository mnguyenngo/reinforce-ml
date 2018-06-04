from flask import Flask, render_template, request, jsonify, Markup
from scorer import Scorer
from render_text import render_text
# import json

app = Flask(__name__)

scorer = Scorer()
baseurl = 'https://en.wikipedia.org'
scorer.load_nlp_pickle('../data/180603_def_nlp.pkl')
# json_data = json.loads(scorer.nlp_data.to_json(orient='index'))
directory = scorer.nlp_data['title'].tolist()


@app.route('/', methods=['GET'])
def index():
    return render_template('app.html', data=directory, baseurl=baseurl)


@app.route('/define/<word>', methods=['GET'])
def define_page(word):
    return render_template('define.html', word=word)


@app.route('/submit', methods=['POST'])
def submit():
    page_data = request.json

    user_submission = page_data["user_subm"]
    annotate_subm = render_text(scorer.nlp(user_submission))
    word = page_data["word"]

    mask = scorer.nlp_data['title'] == word
    definition = scorer.nlp_data.loc[mask]['nlp_doc'].values[0]
    definition = scorer.get_first_sent(definition)
    annotate_def = render_text(definition)
    href = scorer.nlp_data.loc[mask]['href'].values[0]

    url = baseurl + href

    score = scorer.score(word, user_submission)
    submission = render_template('annotate-submission.html',
                                 data=Markup(annotate_subm))
    answer = render_template('annotate-definition.html',
                             data=Markup(annotate_def), url=url)
    show_score = render_template('score.html', data=score)

    return jsonify({'submission': submission,
                    'answer': answer,
                    'score': show_score})


if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True)
