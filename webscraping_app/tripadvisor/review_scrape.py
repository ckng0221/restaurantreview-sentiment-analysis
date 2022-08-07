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
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def scrapeReview(url, driver):
    "scrape the restaurant review, based on restaurant url."
    def eachPageScrape(data):
        """
        Web scrape data in form of dictionary, into a list.

        driver: selenium driver
        data : list
        """

        response = BeautifulSoup(driver.page_source, 'html.parser')

        # check if "more" present
        morebtn = response.find('span', {'class': 'taLnk ulBlueLinks'})
        if morebtn:
            if morebtn.text == "More":
                clickMore()
                # scrap the page again
                response = BeautifulSoup(driver.page_source, 'html.parser')

        reviewContainers = response.find_all(
            'div', {'class': 'review-container'})
        for reviewObj in reviewContainers:  # only get the first one
            author = reviewObj.find('div', class_="info_text pointer_cursor")
            title = reviewObj.find('a', class_="title")
            # to avoid the response from management
            review = reviewObj.find(
                'div', class_="prw_rup prw_reviews_text_summary_hsx")
            rating = reviewObj.find(
                'div', class_="prw_rup prw_reviews_review_resp")
            rating_date = reviewObj.find('span', class_="ratingDate")

        # compile data
        # for author, title, review, rating, rating_date in zip(authors, titles, reviews, ratings, rating_dates):
            document = {}
            document['Author'] = author.text
            document['Title'] = title.text
            document['Review'] = review.text
            document['Rating'] = rating.find("span",
                                             class_="ui_bubble_rating")['class'][1].split('_')[1][0]
            document['Dates'] = rating_date.text
            data.append(document)

        # if only 1 page, check if have page numbers
        pageNumbers = response.find('div', {'class': "pageNumbers"})
        if not pageNumbers:
            return "Only 1 page"

    def clickMore():
        # click the "More button"
        result = None
        while result is None:
            try:  # keep trying until success
                wait.until(EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, 'span.taLnk.ulBlueLinks'))).click()
                result = 1
                # wait until the "Show less" btn presence, before next step
                WebDriverWait(driver, 5).until(
                    EC.text_to_be_present_in_element(
                        (By.CSS_SELECTOR, 'span.taLnk.ulBlueLinks'), 'Show less')
                )
            except (StaleElementReferenceException, ElementClickInterceptedException):
                driver.refresh()
                pass
            except TimeoutException:
                result = 1
                pass
            except Exception:
                # for other unkown errors
                driver.refresh()
                pass

    # load url
    driver.get(url)
    # driver.set_page_load_timeout(5) # seconds for time out

    # restaurantName
    response = BeautifulSoup(driver.page_source, 'html.parser')
    restaurantName = response.find('h1', class_='HjBfq').text

    # Scape Individual page
    data = []
    wait = WebDriverWait(driver, 10)
    # js_query = """
    #     document.querySelector('span.taLnk.ulBlueLinks').click();"
    # """
    # to expand all comments
    while True:
        try:  # from 1st page
            # driver.execute_script(js_query)
            x = eachPageScrape(data)
            if x == "Only 1 page":
                print("Only 1 page")
                break
            next_btn = wait.until(
                EC.element_to_be_clickable((By.LINK_TEXT, "Next")))
            next_btn.click()
        except StaleElementReferenceException:
            try:  # redefine element
                driver.refresh()
                # next_btn = wait.until(
                #     EC.element_to_be_clickable((By.LINK_TEXT, "Next")))
                # next_btn.click()
                pass
            except ElementClickInterceptedException:  # until last page
                x = eachPageScrape(data)
                print("Done")
                break
        except (TimeoutException, ElementClickInterceptedException):  # if only have 1 page
            if driver.find_elements_by_css_selector('a.nav.next.ui_button.primary.disabled'):
                print("last page, done.")
                break
            driver.refresh()
            pass
        except Exception as e:
            # for unkwown errors            print(f"Having other error:\n{e}")
            # preserve the overall data
            break

    # combine data into dataframe
    df = pd.DataFrame(data)
    df['Restaurant'] = restaurantName

    return df


if __name__ == "__main__":
    url = "https://www.tripadvisor.com.my/Restaurant_Review-g298570-d11947368-Reviews-or130-Canopy_Rooftop_Bar_and_Lounge-Kuala_Lumpur_Wilayah_Persekutuan.html"
    scrapeReview(url)

    # timeout page
    # https://www.tripadvisor.com.my/Restaurant_Review-g298570-d11947368-Reviews-or540-Canopy_Rooftop_Bar_and_Lounge-Kuala_Lumpur_Wilayah_Persekutuan.html
