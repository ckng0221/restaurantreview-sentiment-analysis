# %%
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import os
import pandas as pd
import re

from joblib import Parallel, delayed, parallel_backend
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from app.tripadvisor.review_scrape import scrapeReview

# CLI arguments
parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
parser.add_argument("-l", "--location", default="Shah Alam",
                    help="location to scrape")
args = vars(parser.parse_args())


def main(location):
    restaurants = pd.read_csv(f"data/restaurant/Restaurants_{location}.csv")

    # sequential work
    error_restaurants = []

    # start driver
    # driver settings
    options = webdriver.ChromeOptions()
    options.add_argument("--lang=en")
    driver = webdriver.Chrome(service=Service(
        ChromeDriverManager().install()), options=options)

    for restaurant, url in zip(restaurants['Restaurant'], restaurants['url']):
        # --------------------------
        data = []
        orifile_path = f"data/review/TripAdvisor/reviews_all_{location}.csv"
        # inefficient, but more safe for generating files for every restaurant
        if not os.path.exists(orifile_path):
            # start from scratch
            existingReviews = pd.read_json(
                '{"Author":{},"Title":{},"Review":{},"Rating":{},"Dates":{},"Restaurant":{}}')
        else:
            existingReviews = pd.read_csv(orifile_path)
            existingReviews.drop_duplicates(inplace=True)
        completedRestaurant = list(existingReviews["Restaurant"].unique())
        # replace " - CLOSED"
        completedRestaurant = list(
            map(lambda x: re.sub(" - CLOSED$", "", x), completedRestaurant))
        # --------------------

        if restaurant in completedRestaurant:
            print(f"skip {restaurant}")
            continue  # skip completed restaurant

        try:
            print(restaurant)
            df = scrapeReview(url, driver)
        except Exception as e:
            print(f"error on {restaurant}")
            print(e)
            error_restaurants.append(restaurant)
            continue
        finally:
            data.append(df)
            df_final = pd.concat(data)
            existingReviews = existingReviews.append(df_final)
            existingReviews.drop_duplicates(inplace=True)
            existingReviews.to_csv(orifile_path, index=False)
    print("Done all Restaurant")


if __name__ == "__main__":
    location = args['location']
    main(location=location)

    # to run:, eg.
    # python3.10 -m app.tripadvisor.main -l Ipoh
