# In Your Own Words
Uses Wikipedia's Machine Learning Book as a resource to quiz and score user's input.
Try the out the web app at http://iyow.xyz

**See dev branch to contribute**

## Project Brief

### Scope/Premise
Uses Wikipedia's Machine Learning Book as a resource to quiz and score user's input.

### Scoring
As an example:
1. Application asks user to define what is precision?
2. User enters their explanation in a text box.
3. Application scores their response using cosine similarity and bonus points for matching 'noun chunks'.

### Stack
#### "Scraping"
* requests
* Beautiful Soup

#### NLP
* spaCy

#### Deployment
* Flask
* AWS


### Resources
* [Book:Machine Learning – The Complete Guide - Wikipedia](https://en.wikipedia.org/wiki/Book:Machine_Learning_%E2%80%93_The_Complete_Guide)
* [Rules of Machine Learning:  |  Machine Learning Rules  |  Google Developers](https://developers.google.com/machine-learning/rules-of-ml/)
* [ML Reference](http://mlreference.com/)

### Implimentation
To run this website on your own:

`pip install spacey`
`python -m spacy download en_core_web_lg`
`python src/app.py`

