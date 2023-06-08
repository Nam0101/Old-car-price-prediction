import csv
import sys
from bs4 import BeautifulSoup
import requests
import time

delay = 0.01


def craw(url, count):
    time.sleep(delay)
    r = requests.get(url)
    try:
        soup = BeautifulSoup(r.content, "html.parser")
        div_title = soup.find("div", class_="title")
        title = div_title.h1.text.strip()
        car_name = title.split("-")[0]
        car_year = car_name.split(" ")[-1].strip()
        car_name = car_name.split(car_year)[0].strip()
        car_name = car_name.replace("\n", "").replace("\t", "").replace("\r", "").replace("   ", " ").replace("Xe", "")
        car_price = title.split("-")[1]
        div_tags = soup.find_all("div", class_=["txt_input", "inputbox"])
        assemble = div_tags[0].span.text.strip()
        series = div_tags[2].span.text.strip()
        km = div_tags[3].span.text.strip()
        km_driver = km.split(" ")[0]
        km_driver = km_driver.replace(",", "")
        km = int(km_driver)

        retry_count = 0
        while km == 0 and retry_count < 5:
            print("Re Crawling " + url)
            time.sleep(delay)
            r = requests.get(url)
            soup = BeautifulSoup(r.content, "html.parser")
            div_title = soup.find("div", class_="title")
            title = div_title.h1.text.strip()
            car_price = title.split("-")[1]
            div_tags = soup.find_all("div", class_=["txt_input", "inputbox"])
            km = div_tags[3].span.text.strip()
            km_driver = km.split(" ")[0]
            km_driver = km_driver.replace(",", "")
            km = int(km_driver)
            retry_count += 1

        if km == 0:
            print("Max retries reached. Skipping " + url)
            return

        num_of_door = div_tags[6].span.text.strip()
        num_of_seat = div_tags[7].span.text.strip()
        engine = div_tags[8].span.text.strip()
        # engine type is:Hybrid 1.8 L, split it into 2 parts
        engine_type = engine.split("\t")[0]
        transmission = div_tags[10].span.text.strip()
    except Exception as e:
        print("Error " + str(e))
        return
    count[0] += 1
    with open("data.csv", "a", encoding="utf-8", newline="") as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(
            [car_name, car_year, car_price, assemble, series, km, num_of_door, num_of_seat, engine_type,
             transmission])



def get_all_url(url, count):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "html.parser")
    div_tags = soup.find_all("div", class_="g-box-content")
    div_tags = div_tags[0].find_all("li", class_=["car-item row2", "car-item row1"])
    hrefs = [div.a["href"] for div in div_tags]
    for href in hrefs:
        url = "https://bonbanh.com/" + href
        try:
            craw(url, count)
        except Exception as e:
            print("Error " + str(e))
            continue


if __name__ == '__main__':
    car_count = [0]  # Using a list to store the count
    main_url = "https://bonbanh.com/oto-cu-da-qua-su-dung/page,"
    with open("data.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            ["car_name", "year", "price", "assemble_place", "series", "km", "num_of_door", "num_of_seat", "engine_type",
             "transmission"])
    for i in range(2, 1640):
        page_url = main_url + str(i)
        print("Crawling page " + str(i))
        get_all_url(page_url, car_count)
        print("Crawled car: " + str(car_count[0]))
    print("Done!")
