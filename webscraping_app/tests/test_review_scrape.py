from webscraping_app.tripadvisor.review_scrape import scrapeReview


def test_scrapeReview():
    url = "https://www.tripadvisor.com.my/Restaurant_Review-g298570-d15297795-Reviews-Positano_Risto-Kuala_Lumpur_Wilayah_Persekutuan.html"
    df = scrapeReview(url)
    assert len(df) != 0
    assert df['Restaurant'].iloc[0] == "Positano Risto"
