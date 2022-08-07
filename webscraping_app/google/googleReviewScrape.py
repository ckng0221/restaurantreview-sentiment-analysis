# %%
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
import time
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    TimeoutException,
    StaleElementReferenceException,
)
import pandas as pd
import os
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service


class NoGoogleReviewException(Exception):
    "No Google Review available."


class DoneReviewException(Exception):
    "Have already done review."


# CLI arguments
parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
parser.add_argument("-l", "--location", default="KL",
                    help="location to scrape")
args = vars(parser.parse_args())


# ignore, not being used
def clickMore(driver):
    # click the "More button"
    # wait = WebDriverWait(driver, 5)
    try:  # keep trying until success
        # wait.until(EC.element_to_be_clickable(
        #     (By.CSS_SELECTOR, 'a.review-more-link'))).click()
        driver.find_element(by=By.CSS_SELECTOR,
                            value='a.review-more-link').click()
    except Exception:
        pass


def extract_google_reviews(driver, query):
    driver.get('https://www.google.com/?hl=en')
    driver.find_element(by=By.NAME, value='q').send_keys(query)
    driver.find_element(by=By.NAME, value='q').send_keys(Keys.ENTER)

    try:
        reviews_header = driver.find_element(
            by=By.CSS_SELECTOR, value='div.kp-header')
        reviews_link = reviews_header.find_element(
            by=By.PARTIAL_LINK_TEXT, value='Google reviews')
        number_of_reviews = int(reviews_link.text.split()[0].replace(",", ""))
    except Exception as e:
        raise NoGoogleReviewException

    reviews_link.click()

    # name & location forst
    time.sleep(3)
    response = BeautifulSoup(driver.page_source, 'html.parser')
    name = response.find('div', {'class': 'fp-w review-dialog-top'}) \
        .find('div', {'class': 'P5Bobd'}).text
    if name in completedRestaurant:  # actual file completed restaurant
        raise DoneReviewException
    location = response.find('div', {'class': 'fp-w review-dialog-top'}) \
        .find('div', {'class': 'T6pBCe'}).text

    all_reviews = WebDriverWait(driver, 3).until(EC.presence_of_all_elements_located(
        (By.CSS_SELECTOR, 'div.WMbnJf.vY6njf.gws-localreviews__google-review')))
    while len(all_reviews) < number_of_reviews - 1:  # minus 1 review, as may not able to get
        driver.execute_script(
            'arguments[0].scrollIntoView(true);', all_reviews[-1])
        WebDriverWait(driver, 5, 0.25).until_not(EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'div[class$="activityIndicator"]')))
        all_reviews = driver.find_elements(
            by=By.CSS_SELECTOR, value='div.WMbnJf.vY6njf.gws-localreviews__google-review')

        response = BeautifulSoup(driver.page_source, 'html.parser')
        review_check = response.find_all('div', {'class': "Jtu6Td"})[-1].text

        # when no text review, stop
        if review_check == "":
            break

        # limit number of reviews per restaurant, to improve speed
        # slow loading review grows, as without pagination
        if len(all_reviews) == 300:
            break

    # after scroll to the end
    reviews = []
    response = BeautifulSoup(driver.page_source, 'html.parser')

    # review blocks
    reviewblocks = response.find_all(
        "div", {'class': 'WMbnJf vY6njf gws-localreviews__google-review'})
    for item in reviewblocks:
        reviewDict = {}
        reviewDict['Author'] = item.find(
            'div', {'class': "TSUbDb"}).text
        reviewDict['Rating'] = item.find(
            'span', {'class': "Fam1ne EBe2gf"}).attrs['aria-label']
        reviewDict['Review'] = item.find(
            'div', {'class': "Jtu6Td"}).text
        reviews.append(reviewDict)

    # dataframe
    df = pd.DataFrame(reviews)
    df['Restaurant'] = name
    df['Location'] = location

    return df


def main(location):
    global completedRestaurant

    options = webdriver.ChromeOptions()
    options.add_argument("--lang=en")
    # driver = webdriver.Chrome(driverpath, options=options)
    driver = webdriver.Chrome(service=Service(
        ChromeDriverManager().install()), options=options)

    # create directories
    googleReview_dir = "data/review/GoogleReview/"
    log_dir = "log/"
    os.makedirs(googleReview_dir, exist_ok=True)
    os.makedirs(log_dir, exist_ok=True)

    allRestaurantsFile = f'data/restaurant/Restaurants_{location}.csv'
    existingRestaurantsFile = os.path.join(
        googleReview_dir, f"GoogleReview_{location}.csv")

    doneRestaurant = os.path.join(
        log_dir, f"doneRestaurant_Google_{location}.csv")

    if not os.path.exists(existingRestaurantsFile):
        # start from scratch, if don't have any file
        existingReviews_df = pd.read_json(
            '{"Author":{}, "Review":{}, "Rating":{}, "Restaurant":{}}')
    else:
        existingReviews_df = pd.read_csv(existingRestaurantsFile)
        existingReviews_df.drop_duplicates(inplace=True)
    completedRestaurant = list(existingReviews_df["Restaurant"].unique())

    # for recording the done scraping restaurant, based on filename, instead of google name
    if not os.path.exists(doneRestaurant):
        # start from scratch, if don't have any file
        doneRestaurant_df = pd.read_json(
            '{"Restaurant":{}}')
    else:
        doneRestaurant_df = pd.read_csv(doneRestaurant)

    # search from all restuarant list
    restaurants = pd.read_csv(allRestaurantsFile)

    for restaurant in restaurants.Restaurant:
        data = []
        # Skip based on log recorded restaurant
        if restaurant in doneRestaurant_df['Restaurant'].to_list():
            print(f"skip {restaurant}")
            continue

        try:
            print(restaurant)
            df = extract_google_reviews(
                driver, f'{restaurant} {location}')
        except DoneReviewException:
            print(f"Done review {restaurant} before, skip.")
            continue
        except NoGoogleReviewException:
            print("No Google Review")
            continue
        except Exception as e:
            print(e)
        else:
            data.append(df)
            print(f"Done {restaurant}")

            # rewrite new file everytime, for security
            df_all = pd.concat(data)
            df_all.drop_duplicates(inplace=True)
            existingReviews_df = existingReviews_df.append(df_all)
            existingReviews_df.to_csv(existingRestaurantsFile, index=False)
        finally:
            # put into log
            current_restaurant = pd.DataFrame([{"Restaurant": restaurant}])
            doneRestaurant_df = doneRestaurant_df.append(
                current_restaurant, ignore_index=True)
            doneRestaurant_df.to_csv(doneRestaurant, index=False)

    driver.quit()


if __name__ == '__main__':
    location = args["location"]  # {default: KL}
    main(location=location)
    # main(location='Ipoh')
    # ---- To use ----
    # eg. python app/review_scape.py -l Melaka
