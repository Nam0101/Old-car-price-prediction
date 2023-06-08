import csv
import sys
from bs4 import BeautifulSoup
import requests
import time

delay = 0.1


def save_state(page_number, car_count):
    with open("state.txt", "w") as f:
        f.write(f"{page_number},{car_count[0]}")


def load_state():
    try:
        with open("state.txt", "r") as f:
            data = f.read().split(",")
            page_number = int(data[0])
            car_count = [int(data[1])]
            return page_number, car_count
    except FileNotFoundError:
        return 2, [0]


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
        while km < 500 and retry_count < 5:
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
        num_dorr = num_of_door.split(" ")[0]
        num_of_door = int(num_dorr)
        num_seat = num_of_seat.split(" ")[0]
        num_of_seat = int(num_seat)
        if num_of_door == 0 or num_of_seat == 0:
            # retry
            retry_count = 0
            while (num_of_door == 0 or num_of_seat == 0) and retry_count < 5:
                print("Re Crawling " + url)
                time.sleep(delay)
                r = requests.get(url)
                soup = BeautifulSoup(r.content, "html.parser")
                div_title = soup.find("div", class_="title")
                title = div_title.h1.text.strip()
                car_price = title.split("-")[1]
                div_tags = soup.find_all("div", class_=["txt_input", "inputbox"])
                num_of_door = div_tags[6].span.text.strip()
                num_of_seat = div_tags[7].span.text.strip()
                num_dorr = num_of_door.split(" ")[0]
                num_of_door = int(num_dorr)
                num_seat = num_of_seat.split(" ")[0]
                num_of_seat = int(num_seat)
                retry_count += 1
        if num_of_door == 0 or num_of_seat == 0:
            print("Max retries reached. Skipping " + url)
            return
        engine = div_tags[8].span.text.strip()
        # engine type is:Hybrid 1.8 L, split it into 2 parts
        engine_type = engine.split("\t")[0]
        transmission = div_tags[10].span.text.strip()
    except Exception as e:
        print("Error " + str(e))
        return
    count[0] += 1
    with open("data.csv", "a+", encoding="utf-8", newline="") as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(
            [car_name, car_year, car_price, assemble, series, km, num_of_door, num_of_seat, engine_type,
             transmission, url])


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
            # retry connection
            print("Re Crawling Because connetion error" + url)
            time.sleep(delay)
            try:
                craw(url, count)
            except Exception as e:
                print("Error " + str(e))
            continue


if __name__ == '__main__':
    page_number, car_count = load_state()
    main_url = "https://bonbanh.com/oto-cu-da-qua-su-dung/page,"
    with open("data.csv", "a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        if f.tell() == 0:
            writer.writerow(
                ["car_name", "year", "price", "assemble_place", "series", "km", "num_of_door", "num_of_seat",
                 "engine_type", "transmission"])

    for i in range(page_number, 1640):
        page_url = main_url + str(i)
        print("Crawling page " + str(i))
        get_all_url(page_url, car_count)
        print("Crawled car: " + str(car_count[0]))
        save_state(i, car_count)

    print("Done!")
