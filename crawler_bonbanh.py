import csv
import requests
from bs4 import BeautifulSoup
import time
from threading import Thread, Lock, Event
import queue

# Constants
DELAY = 1.05
NUM_THREADS = 5
MAX_PAGES = 2  # Adjust as needed
DATA_FILE = "data_bonbanh.csv"
BASE_URL = "https://bonbanh.com/oto-cu-da-qua-su-dung/page,"

# Global variables
car_count = [0]
page_queue = queue.Queue()
last_crawled_url = None
url_lock = Lock()  # Lock for last_crawled_url
stop_event = Event()  # Event to signal stopping


def craw(url):
    """Crawls a given URL and extracts car information."""
    global last_crawled_url
    time.sleep(DELAY)
    r = requests.get(url)

    try:
        soup = BeautifulSoup(r.content, "html.parser")
        div_title = soup.find("div", class_="title")
        title = div_title.h1.text.strip()
        car_name = title.split("-")[0].strip().replace("Xe", "")
        car_year = car_name.split(" ")[-1].strip()
        car_name = car_name.split(car_year)[0].strip()
        car_name = car_name.replace("\n", "").replace("\t", "").replace("\r", "").replace("   ", " ").replace("Xe", "")
        car_price = title.split("-")[1].strip()
        div_tags = soup.find_all("div", class_=["txt_input", "inputbox"])
        km = div_tags[2].span.text.strip()
        assemble = div_tags[3].span.text.strip()
        series = div_tags[4].span.text.strip()
        transmission = div_tags[5].span.text.strip()
        engine = div_tags[6].span.text.strip()
        num_of_seat = div_tags[9].span.text.strip()
        num_of_door = div_tags[10].span.text.strip()

        with open(DATA_FILE, "a+", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                car_name,
                car_year,
                car_price,
                assemble,
                series,
                km,
                engine,
                transmission,
                url
            ])

        car_count[0] += 1
        print(f"Crawled car: {car_count[0]}")

    except Exception as e:
        print(f"Error crawling {url}: {str(e)}")


def get_all_url(url):
    """Gets all car URLs from a given page."""
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "html.parser")
    div_tags = soup.find_all("div", class_="g-box-content")
    div_tags = div_tags[0].find_all("li", class_=["car-item row2", "car-item row1"])
    hrefs = [div.a["href"] for div in div_tags]

    for href in hrefs:
        craw_url = "https://bonbanh.com/" + href
        page_queue.put(craw_url)


def worker():
    """Worker thread to process URLs from the queue."""
    global last_crawled_url
    while True:
        if stop_event.is_set():
            return  # Exit worker thread if stop_event is set

        try:
            url = page_queue.get(timeout=1)

            with url_lock:
                if last_crawled_url and url == last_crawled_url:
                    print(f"Reached last crawled URL: {last_crawled_url}. Stopping crawling.")
                    stop_event.set()  # Signal all threads to stop
                    page_queue.task_done()
                    return  # Exit worker thread

            craw(url)
            page_queue.task_done()
        except queue.Empty:
            break


def main():
    """Main function to initiate crawling."""
    global last_crawled_url

    # Read last crawled URL from CSV file
    last_crawled_url = get_last_crawled_url(DATA_FILE)
    print(f"Last crawled URL: {last_crawled_url}")

    with open(DATA_FILE, "a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        if f.tell() == 0:
            writer.writerow([
                "car_name",
                "year",
                "price",
                "assemble_place",
                "series",
                "km",
                "engine_type",
                "transmission",
                "url"
            ])

    threads = []
    for _ in range(NUM_THREADS):
        thread = Thread(target=worker)
        thread.daemon = True
        threads.append(thread)
        thread.start()

    # Crawl pages from 0 to MAX_PAGES
    for i in range(0, MAX_PAGES):
        page_url = BASE_URL + str(i)
        print(f"Crawling page {i}")
        get_all_url(page_url)

    # Wait for all threads to finish (only if stop_event is not set)
    for thread in threads:
        thread.join()

    print("Done!")


def get_last_crawled_url(data_file):
    """Reads the first crawled URL from the CSV file."""
    first_url = None
    try:
        with open(data_file, "r", encoding="utf-8", newline="") as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            for row in reader:
                if first_url is None:
                    first_url = row[-1]  # Update first_url only if it's still None
    except FileNotFoundError:
        print(f"File not found: {data_file}")
    return first_url


if __name__ == "__main__":
    main()
