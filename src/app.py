from flask import Flask, render_template, request, jsonify, Markup
from scorer import Scorer
import json

app = Flask(__name__)

scorer = Scorer()
baseurl = 'https://en.wikipedia.org'
scorer.load_pickle('../data/180530_def.pkl')
json_data = json.loads(scorer.raw_data.to_json(orient='index'))

@app.route('/', methods=['GET'])
def index():
    return render_template('app.html', data=json_data, baseurl=baseurl)


@app.route('/submit', methods=['POST'])
def submit():
    user_submission = request.json
    return render_template('annotate-submission.html', data=user_submission)


if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True)
