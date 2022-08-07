from django.urls import path

from .views import about, api_guide, index, SentimentAnalysisAPI, infographics, notebookAnalytics, notebookSentimentAnalysis

urlpatterns = [
    path('', index, name='index'),
    path('about/', about, name='about'),
    path('api-guide/', api_guide, name='api-guide'),
    path('api/', SentimentAnalysisAPI.as_view(), name='api'),
    path('infographics/', infographics, name='infographics'),
    path('notebook/sentimentanalysis/', notebookSentimentAnalysis,
         name='notebook-sentimentanalysis'),
    path('notebook/analytics/', notebookAnalytics, name='notebook-analytics'),
]
