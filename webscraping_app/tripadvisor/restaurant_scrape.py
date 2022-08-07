# %%
# for Trip Advisor
import os
import re
import time

from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    StaleElementReferenceException,
    TimeoutException,
)


def scrapeRestaurant(url):
    """
    Scrape restaurant name and url.

    url : url of the trip advisor of the region.
    """
    def eachPageScrape(data):
        """
        Web scrape data in form of dictionary, into a list.

        driver: selenium driver
        data : list
        """
        response = BeautifulSoup(driver.page_source, 'html.parser')
        restaurants = response.find_all('div', class_='OhCyu')
        domain = "https://www.tripadvisor.com.my"

        lastNext = response.find('span', {'class': 'nav next disabled'})
        if lastNext:
            raise TimeoutException

            # compile data
        for restaurant in restaurants:
            document = {}
            document['Restaurant'] = restaurant.text
            document['url'] = domain + restaurant.find('a')['href']
            data.append(document)

    # driver settings
    driverpath = "/Users/ckng/Desktop/utils/chromedriver_v99"
    options = webdriver.ChromeOptions()
    options.add_argument("--lang=en")
    driver = webdriver.Chrome(driverpath, options=options)

    # load url
    driver.get(url)
    driver.set_page_load_timeout(10)  # seconds for time out

    # Scape Individual page
    data = []
    wait = WebDriverWait(driver, 10)
    while True:
        try:  # from 1st page
            eachPageScrape(data)
            next_btn = wait.until(
                EC.element_to_be_clickable((By.LINK_TEXT, "Next")))
            next_btn.click()

        except StaleElementReferenceException:
            try:  # redefine element
                next_btn = wait.until(
                    EC.element_to_be_clickable((By.LINK_TEXT, "Next")))
                next_btn.click()
                time.sleep(0.5)
            except ElementClickInterceptedException:  # until last page
                eachPageScrape(data)
                print("Done")
                break
            except TimeoutException:
                print("Done")
                break
        except TimeoutException:  # if only have 1 page
            if driver.find_elements_by_css_selector('span.nav.next.disabled'):
                print("last page, done.")
                break
                # driver.refresh()
        except Exception:  # other general execeptions
            # driver.refresh()
            ...

    # combine data into dataframe
    df = pd.DataFrame(data)
    # preprocessing
    # get name after number eg. 1. Grant Hatyai
    df['Restaurant'] = df['Restaurant'].apply(
        lambda x: re.compile("(^[0-9]+\.\s)?(.*)").search(x).group(2))
    df = df.drop_duplicates(subset='Restaurant')

    return df


def main(url, location):
    filepath = f"data/Restaurants_{location}.csv"
    # skip files if already done.
    if os.path.exists(filepath):
        print(f"Skip {location}")
        return

    df = scrapeRestaurant(url)
    # df.drop_duplicates(inplace=True)
    df.to_csv(filepath, index=False)
    print(f"Done {location}")


# %%
if __name__ == "__main__":
    # url =
    urls = [
        ("https://www.tripadvisor.com.my/Restaurants-g298570-Kuala_Lumpur_Wilayah_Persekutuan.html", 'KL'),
        ("https://www.tripadvisor.com.my/Restaurants-g298278-Johor_Bahru_Johor_Bahru_District_Johor.html", 'JB'),
        ("https://www.tripadvisor.com.my/Restaurants-g660694-Penang_Island_Penang.html", 'Penang'),
        ("https://www.tripadvisor.com.my/Restaurants-g306997-Melaka_Central_Melaka_District_Melaka_State.html", 'Melaka'),
        ("https://www.tripadvisor.com.my/Restaurants-g298298-Ipoh_Kinta_District_Perak.html", 'Ipoh'),
        ("https://www.tripadvisor.com.my/Restaurants-g303998-Miri_Miri_District_Sarawak.html", 'Miri'),
        ("https://www.tripadvisor.com.my/Restaurants-g298309-Kuching_Sarawak.html", 'Kuching'),
        ("https://www.tripadvisor.com.my/Restaurants-g298283-Langkawi_Langkawi_District_Kedah.html", 'Langkawi'),
        ("https://www.tripadvisor.com.my/Restaurants-g298316-Shah_Alam_Petaling_District_Selangor.html", 'Shah Alam'),
        ("https://www.tripadvisor.com.my/Restaurants-g298313-Petaling_Jaya_Petaling_District_Selangor.html", 'PJ'),
    ]
    for url, loc in urls:
        main(url, loc)


# %%
