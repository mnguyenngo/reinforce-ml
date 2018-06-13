from flask import Flask, render_template, request, jsonify, Markup, redirect
from scorer import Scorer
from render_text import render_text
from random import randint
# import json

app = Flask(__name__)

scorer = Scorer()
baseurl = 'https://en.wikipedia.org'
#Set pickle to most up-to-date version
scorer.load_nlp_pickle('../data/180530_def.pkl')
# json_data = json.loads(scorer.nlp_data.to_json(orient='index'))
directory = scorer.nlp_data['title'].tolist()
section_title = scorer.nlp_data['section'].unique()
directory_dict = {}
for sec in section_title:
    mask = scorer.nlp_data['section'] == sec
    directory_dict[sec] = scorer.nlp_data[mask]['title'].values


@app.route('/', methods=['GET'])
def index():
    return render_template('app.html', data=directory_dict)


@app.route('/random', methods=['GET'])
def random_term():
    total_num = len(scorer.nlp_data)
    print(total_num)
    x = randint(0, total_num)
    word = scorer.nlp_data.loc[x, 'title']
    print(word)
    return redirect('/define/{}'.format(word))


@app.route('/define/<word>', methods=['GET'])
def define_page(word):
    mask = scorer.nlp_data['title'] == word
    href = scorer.nlp_data.loc[mask]['href'].values[0]
    url = baseurl + href
    return render_template('define.html', word=word, url=url)


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

    leaderboard = scorer.nlp_data.loc[mask]['leaderboard'].values[0]
    show_leaderboard = render_template('leaderboard.html', data=leaderboard)

    next_step = render_template('next_step.html')

    return jsonify({'submission': submission,
                    'answer': answer,
                    'score': show_score,
                    'leaderboard': show_leaderboard,
                    'next_step': next_step})


if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True)
