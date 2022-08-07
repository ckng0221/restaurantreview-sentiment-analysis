from django.shortcuts import render
# from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response

from .analysisTools import getPolarity, getStarRating, sentimentAnalysis, posProcessing, posTagging
from .forms import TextInputForm


# @csrf_exempt
def index(request):
    sentimentResult_multiclass, sentimentResult_binary, posResult, polarityResult, starRatingResult = "", "", "", "", ""
    positive_multiclass, neutral_multiclass, negative_multiclass = "", "", ""
    positive_binary, negative_binary = "", ""
    template = "sentiment/index.html"

    # submitbutton = request.POST.get("submit")
    form = TextInputForm(request.POST or None)

    if request.method == "POST":
        print(request.POST)
        if form.is_valid():
            text = form.cleaned_data.get("textInput")
            if text != "":
                # -- sentiment analysis --
                # multiclass classificaiton
                sentimentResult_multiclass, probabilities = sentimentAnalysis(
                    text, classificationType="multiclass")
                positive_multiclass = probabilities[0][2] * 100
                neutral_multiclass = probabilities[0][1] * 100
                negative_multiclass = probabilities[0][0] * 100
                if round(positive_multiclass, 2) == round(neutral_multiclass, 2) == round(negative_multiclass, 2):
                    sentimentResult_multiclass = "no result"

                # binary classificaiton
                sentimentResult_binary, probabilities = sentimentAnalysis(
                    text, classificationType="binary")
                positive_binary = probabilities[0][1] * 100
                negative_binary = probabilities[0][0] * 100
                if round(positive_binary, 2) == round(negative_binary, 2):
                    sentimentResult_binary = "no result"

                # POS tagging
                posResult = posProcessing(text)

                # polarity
                polarity_score = getPolarity(text)
                polarityResult = polarity_score['compound']
                starRatingResult = getStarRating(polarity_score)

    context = {
        'form': form,
        # -- mutliclass --
        'sentimentResult_multiclass': sentimentResult_multiclass,
        # probability
        'positive_multiclass': positive_multiclass,
        'neutral_multiclass': neutral_multiclass,
        'negative_multiclass': negative_multiclass,
        # -- binary --
        'sentimentResult_binary': sentimentResult_binary,
        # probability
        'positive_binary': positive_binary,
        'negative_binary': negative_binary,

        'posResult': posResult,
        'polarityResult': polarityResult,
        'starRatingResult': starRatingResult,
        
        # active page
        'navbar': 'index',
    }

    return render(request, template, context)


class SentimentAnalysisAPI(APIView):
    def get(self, request):
        url = getHostName(request)
        apiEndpoint = url + '/api/'
        text = f"""To use the sentiment analysis api by performing POST request on the api end point.
        Endpoint: {apiEndpoint}
        With following JSON body. eg.
        {{'text': 'Best restaurant in town!'}}
        """
        text = text.replace("\n", "")
        return Response(text, status=200)

    def post(self, request):
        """
        API to perform sentiment analysis.

        Returns
        -------
        json : {
            'result' : {'Negative', 'Neutral', 'Positive'},
            'probailities' : ['Probability of Bad', 'Probability of Neutral'], ['probability of Positive']]
        }

        Example to use
        --------------
        - curl
            curl -X POST http://{hostname}/api/ \
                -H 'Content-Type: application/json' \
                -d '{"text":"The food is nice! I will come again."}'

        - Python requests 
            import requests

            url = "http://{hostname}/api/"
            reviewText = "The food is nice! I will come again."
            r = requests.post(url=url, json={"text": reviewText})
            response = r.json()
            print(response)
        """

        data = request.data
        text = data['text']

        result_multiclass, probabilities_multiclass = sentimentAnalysis(
            text, classificationType="multiclass")
        result_binary, probabilities_binary = sentimentAnalysis(
            text, classificationType="binary")
        pos_tags = posProcessing(text)
        polarity_score = getPolarity(text)
        starRatingResult = getStarRating(polarity_score)

        response_dict = {
            'sentiment-analysis': [
                {
                    'multiclass': {
                        'result': result_multiclass,
                        'probabilities': probabilities_multiclass[0],
                    },
                    'binary': {
                        'result': result_binary,
                        'probabilities': probabilities_binary[0],
                    }
                }
            ],
            'pos_tags': pos_tags,
            'polarity_score': polarity_score,
            'polarity_rating': starRatingResult,
        }

        return Response(response_dict, status=200)


def about(request):
    context = {
        # active page
        'navbar': 'about',
    }
    template = "sentiment/about.html"
    return render(request, template, context)


def api_guide(request):
    # url = "http://127.0.0.1:8000"  # change this
    url = getHostName(request)  # change this
    context = {
        'url': url,
        # active page
        'navbar': 'api-guide',
    }
    template = "sentiment/api-guide.html"
    return render(request, template, context)


def infographics(request):
    context = {
        # active page
        'navbar': 'infographics',
    }
    template = "sentiment/infographics.html"
    return render(request, template, context)


def notebookSentimentAnalysis(request):
    context = {
        # active page
        'navbar': 'notebook',
    }
    template = "notebook/sentimentanalysis.html"
    return render(request, template, context)


def notebookAnalytics(request):
    context = {
        # active page
        'navbar': 'notebook',
    }
    template = "notebook/analytics.html"
    return render(request, template, context)


def getHostName(request):
    scheme = request.scheme               # http or https
    domain = request.META['HTTP_HOST']    # example.com

    return f"{scheme}://{domain}"  # eg. http://google.com
