from typing import List, Tuple

import joblib
import nltk
import pandas as pd
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# load classifier
# multiclass
classifier_multiclass = joblib.load(
    'sentiment/classifier/lg_classifier_multiclass.pkl')
vectorizer_multiclass = joblib.load(
    'sentiment/classifier/vectorizer_multiclass.pkl')
# binary
classifier_binary = joblib.load(
    'sentiment/classifier/lg_classifier_binary.pkl')
vectorizer_binary = joblib.load(
    'sentiment/classifier/vectorizer_binary.pkl')

# download required libarry
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('vader_lexicon')


def sentimentAnalysis(text: str, classificationType: str = "multiclass"):
    """
    Perform sentiment analysis.

    text : Review content for sentiment analysis
    classificationType : {'multiclass', 'binary'}. To choose multiclass or binary classification. Default multiclass

    >>> Returns 
    ['positive', ...] , [probilitiy, ...]
    """

    if classificationType == "multiclass":
        df_text = pd.DataFrame([{"Review": text}])
        X = vectorizer_multiclass.transform(df_text["Review"])
        X_text_df = pd.DataFrame(
            X.toarray(), columns=vectorizer_multiclass.get_feature_names_out())

        # reverse label
        labels = {
            0: 'negative',
            1: 'neutral',
            2: 'positive',
        }

        result = int(classifier_multiclass.predict(X_text_df)[0])
        probabilites = classifier_multiclass.predict_proba(X_text_df)

        return labels[result], probabilites

    elif classificationType == "binary":
        df_text = pd.DataFrame([{"Review": text}])
        X = vectorizer_binary.transform(df_text["Review"])
        X_text_df = pd.DataFrame(
            X.toarray(), columns=vectorizer_binary.get_feature_names_out())

        # reverse label
        labels = {
            0: 'negative',
            1: 'positive',
        }

        result = int(classifier_binary.predict(X_text_df)[0])
        probabilites = classifier_binary.predict_proba(X_text_df)

        return labels[result], probabilites


def posTagging(text: str):
    """
    Return list of pos tags

    text: input from users.

    return, eg.
    [('I', 'PRP'), ('like', 'VBP'), ('the', 'DT'), ('food', 'NN'), ('here', 'RB'), ('.', '.')]

    """
    return nltk.pos_tag(nltk.word_tokenize(text))


def posProcessing(text: str):
    # dicts of pos tags:
    posTagDict = {
        'CC': 'Conjunction',
        'CD': 'cardinal digit',
        'DT': 'determiner',
        'EX': 'existential',
        'FW': 'foreign word',
        'IN': 'preposition/subordinating conjunction',
        'JJ': 'adjective',
        'JJR': 'adjective, comparative',
        'JJS': 'adjective, superlative',
        'LS': 'list marker',
        'MD': 'modal',
        'NN': 'noun, singular',
        'NNS': 'noun plural',
        'NNP': 'proper noun',
        'NNPS': 'proper noun',
        'PDT': 'predeterminer',
        'POS': 'possessive ending',
        'PRP': 'personal pronoun',
        'PRP$': 'possessive pronoun',
        'RB': 'adverb',
        'RBR': 'adverb',
        'RBS': 'adverb, superlative',
        'RP': 'particle',
        'TO': 'to',
        'UH': 'interjection',
        'VB': 'verb, base form',
        'VBD': 'verb, past tense',
        'VBG': 'verb, gerund/present',
        'VBN': 'verb, past participle taken',
        'VBP': 'verb, present',
        'VBZ': 'verb, 3rd person',
        'WDT': 'wh-determiner',
        'WP': 'wh-pronoun',
        'WP$': 'possessive wh-pronoun',
        'WRB': 'wh-abverb where, when',
    }

    postList = posTagging(text)

    # convert to dict
    postListDict = [{i[0]:i[1]} for i in postList]
    print(postListDict)
    new_dict = {}
    for dict_ in postListDict:
        for key, value in dict_.items():
            value = posTagDict.get(value)
            if value != None:
                new_dict[key.lower()] = value
    return new_dict


def getPolarity(text: str):
    """
    Return dict of polarity.
    eg. 
    >>> polarity
    {'neg': 0.362, 'neu': 0.638, 'pos': 0.0, 'compound': -0.5267}
    """
    polarityAnalyzer = SentimentIntensityAnalyzer()
    polarity = polarityAnalyzer.polarity_scores(text)
    return polarity


def getStarRating(polarity: dict):
    """
    Convert the polarity into star rating.

    Return {'1','2','3','4','5'}
    """
    def minmax_Normalization(x, min, max):
        return (x-min)/(max-min)

    compoundScore = polarity['compound']
    # star rating
    if compoundScore == 0:
        starRating = '3'
    else:
        starRating = minmax_Normalization(compoundScore, -1, 1) * 5
        starRating = str(int(
            # minimum star is 1
            max(
                round(starRating, 0),
                1
            )
        ))
    return starRating
