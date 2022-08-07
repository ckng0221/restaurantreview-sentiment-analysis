# Restaurant Review Linguistic Features Analytics & Sentiment Analysis Tools

Restaurant Review Sentiment Analysis Tool is a sentiment analysis tool developed using **machine learning** algorithms, that is able to perform multiclass ("positive", "neutral", "negative") and binary ("positive" and "negative") sentiment classfication, based on users input. The web application was developed using Django framework. 

The machine learning model used for the tool was developed using the collected restaurant reviews from various regions in Malaysia, where the data collection was done by web scrapping.

The repository contains the complete source codes for web scraping application, linguistic features analytics, and web application development. 

The collected data is published on Kaggle:
https://www.kaggle.com/datasets/choonkhonng/malaysia-restaurant-review-datasets

The deployed Restaurant Review Sentiment Analysis Tool web application can be found on:
https://restaurant-sentimentanalysis.herokuapp.com/

The Tool can be used either directly on web page by submiting the input or directly sending POST requests via REST API.

## Directories

**data** : Consists of raw data and cleaned data. Raw data consists of restaurant names at various locations in Malaysia, and the raw data collected.

**notebook** : Consists of the work done on data and linguistic features analytics, and sentiment analysis model development, in Jupyter Notebook.

**webapp** : The source code for the Restaurant Review Sentiment Analysis Tool. 

**webscraping_app** : Consists of the source codes used for the web scraping application for Google reviews and TripAdvisor.



========================================================================================

The work is done for the Research Project for Master of Data Science, by Ng Choon Khon in year 2022. 

========================================================================================
