import requests
import json
import os
import pandas as pd

lists = []
characters = {'/', '\\', '%', '*', '"', '<', '>', '|', ':', '?'}
list_url = "https://hotels4.p.rapidapi.com/properties/list"
search_url = "https://hotels4.p.rapidapi.com/locations/search"
photo_url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"

location = input('Name of countries, cities, districts, places, etc… : ')

search_querystring = {"query": {location}, "locale": "en_US"}

headers = {
    'x-rapidapi-key': "727f37a8camshb83e2ba47933fe7p1aebc9jsnca961d544f1f",
    'x-rapidapi-host': "hotels4.p.rapidapi.com"
    }

try:
    os.mkdir(location)
except FileExistsError:
    pass

main_directory = f'{os.getcwd()}/{location}'
os.chdir(main_directory)

search_response = requests.request("GET", search_url, headers=headers, params=search_querystring)

with open('hotel search.json', 'w') as hotel_search1:
    hotel_search1.write(search_response.text)

with open('hotel search.json') as hotel_search2:
    search_load = json.load(hotel_search2)

print(search_load)
city_search = search_load['suggestions'][0]
suggestions = city_search['entities']
Breaker = False
for suggestion in suggestions:
    name = suggestion['name']
    while True:
        destination = input(f'{name}, do you want to search for this region? defult will be the first region if all '
                            f'is (n) (y/n): ').lower()
        if destination == 'y':
            destination_id = suggestion['destinationId']
            try:
                os.mkdir(name)
            except FileExistsError:
                pass
            
            region_directory = f'{os.getcwd()}/{name}'
            Breaker = True
            break
        elif destination == 'n':
            break
        else:
            print('Try again. enter (y/n) only.')
            continue
    if Breaker:
        break


while True:
    try:
        page_number = int(input('How many pages you\'re searching for? (Max is 5): '))
    except ValueError:
        print("Please enter a number")
        continue
    if 5 < page_number or page_number < 1:
        print('try again, enter a number from 1-5.')
    else:
        break


check_in = input("What's your check-in date? (make sure to type yyyy-mm-dd or else script will fail): ")
check_out = input("What's your check-out date? (make sure to type yyyy-mm-dd or else script will fail): ")

i = 1
while i <= page_number:

    try:
        list_querystring = {f"destinationId": {destination_id}, "pageNumber": {page_number}, "checkIn": {check_in},
                            "checkOut": {check_out}, "pageSize": "25", "adults1": "1", "currency": "USD",
                            "locale": "en_US", "sortOrder": "PRICE"}
        print(list_querystring)
    except NameError:
        destination_id = search_load['suggestions'][0]['entities'][0]['destinationId']
        list_querystring = {f"destinationId": {destination_id}, "pageNumber": {page_number}, "checkIn": {check_in},
                            "checkOut": {check_out}, "pageSize": "25", "adults1": "1", "currency": "USD",
                            "locale": "en_US", "sortOrder": "PRICE"}
        print(list_querystring)

    list_response = requests.request("GET", list_url, headers=headers, params=list_querystring)

    with open('hotel list.json', 'w') as hotel_list:
        hotel_list.write(list_response.text)

    with open('hotel list.json') as hotel_list2:
        list_load = json.load(hotel_list2)

    hotels_list = list_load['data']['body']['searchResults']['results']


    for hotel in hotels_list:
        os.chdir(region_directory)
        data_dict = {}
        data_dict['id'] = hotel['id']
        data_dict['hotel name'] = hotel['name']
        for character in characters:
            if character in data_dict['hotel name']:
                data_dict['hotel name'] = data_dict['hotel name'].replace(character, '')
        try:
            os.mkdir(data_dict['hotel name'])
        except FileExistsError:
            pass
        os.chdir(f'{region_directory}/{data_dict["hotel name"]}')
        querystring = {"id": data_dict['id']}
        response = requests.request("GET", photo_url, headers=headers, params=querystring)
        with open('hotel image.json', 'w') as file:
            file.write(response.text)
        with open('hotel image.json') as file2:
            load = json.load(file2)
        hotel_images = load['hotelImages']
        for image in hotel_images:
            image_url = image['baseUrl'].replace('{size}', 'z')
            r = requests.get(image_url)
            filename = image_url.split('/')[-1]
            open(filename, 'wb').write(r.content)
        data_dict['star rating'] = hotel['starRating']
        data_dict['rating average'] = hotel['guestReviews']['rating']
        data_dict['price'] = hotel['ratePlan']['price']['current']
        address = hotel['address']
        data_dict['street address'] = address['streetAddress']
        data_dict['local'] = address['locality']
        data_dict['zipcode'] = address['postalCode']
        data_dict['region'] = address['region']
        data_dict['country'] = address['countryName']
        with open('hotel.txt', 'w', encoding='utf-8') as text:
            text.write(f'Hotel ID: {data_dict["id"] }'
                       f'Hotel address: {data_dict["street address"]}, {data_dict["local"]}, {data_dict["zipcode"]}, {data_dict["region"]}, {data_dict["country"]} '
                       f' Hotel price: {data_dict["price"] }'
                       f'{data_dict["star rating"]} star hotel rating: {data_dict["rating average"]}'
                       f' Hotel name: {data_dict["hotel name"]}')
        lists.append(data_dict)

os.chdir(region_directory)
df = pd.DataFrame(lists)
df.to_csv(f'hotel.csv', index=False)
