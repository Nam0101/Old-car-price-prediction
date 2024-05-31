from bs4 import BeautifulSoup
import requests
import csv

URL = 'https://oto.com.vn/'

def crawler(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        data = []
        info_cars = soup.find_all('div', class_='item-car vippro dev-item-car')
        if not info_cars:
            return []  # Return an empty list if no cars found
        for car in info_cars:
            car_name = car.find('span', class_='car-name').get_text(strip=True).split(" - ")[1]
            price = car.find('p', class_='price').get_text(strip=True)
            link_car = URL + car.find('a')['href']

            car_details = {}
            response_item = requests.get(link_car)
            if response_item.status_code == 200:
                soup_item = BeautifulSoup(response_item.content, 'html.parser')
                car_items = soup_item.find('ul', class_='list-info').find_all('li')
                for car_item in car_items:
                    label_item = car_item.find('label', class_='label').contents[-1].strip()
                    if label_item == 'Năm SX':
                        car_details['year'] = car_item.contents[-1].strip()
                    elif label_item == 'Kiểu dáng':
                        car_details['series'] = car_item.contents[-1].strip()
                    elif label_item == 'Xuất xứ':
                        car_details['assemble_place'] = car_item.contents[-1].strip()
                    elif label_item == 'Km đã đi':
                        car_details['km'] = car_item.contents[-1].strip()
                    elif label_item == 'Hộp số':
                        car_details['transmission'] = car_item.contents[-1].strip()
                    elif label_item == 'Nhiên liệu':
                        car_details['engine_type'] = car_item.contents[-1].strip()

            data.append([car_name, car_details.get('year', ''), price, car_details.get('assemble_place', ''),
                         car_details.get('series', ''), car_details.get('km', ''), car_details.get('engine_type', ''),
                         car_details.get('transmission', ''), link_car])
        return data
    else:
        print("Yêu cầu không thành công.")
        return []  # Return an empty list if the request fails


def save_to_file(data, filename, header=True):  # Default header to True
    with open(filename, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if header:  # Write header only if header is True
            writer.writerow(['car_name', 'year', 'price', 'assemble_place', 'series', 'km', 'engine_type', 'transmission', 'url'])
        writer.writerows(data)
    print(f"Dữ liệu đã được lưu vào file {filename}")


def craw():
    save_to_file([], 'data_oto.csv')  # Call save_to_file with header=True (default)

    count = 0
    for i in range(1, 1000):
        if i == 1:
            url = URL + 'mua-ban-xe'
        else:
            url = URL + 'mua-ban-xe' + '/p' + str(i)
        print(url)
        data = crawler(url)
        if not data:
            print("Không tìm thấy xe hơi.")
            break
        else:
            save_to_file(data, 'data_oto.csv', header=False)  # Don't write header for subsequent calls
            count += len(data)

    with open('count_car2.txt', 'w') as file:
        file.write(str(count))


if __name__ == '__main__':
    craw()