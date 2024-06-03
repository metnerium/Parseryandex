import requests
import csv

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en",
    "Content-Type": "application/json;charset=utf-8",
    "X-Taxi": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0 platform=eats_desktop_web",
    "X-Client-Session": "lwtm42dy-o07z5q94qs8-rf10cdtsywl-eijxudrizne",
    "X-Ya-Coordinates": "latitude=55.67740842930555,longitude=37.55965071682982",
    "X-Device-Id": "lwtm42dy-v4iqe2a7ajj-z8ldl9443d-fponqftotl",
    "X-Platform": "desktop_web",
    "X-App-Version": "16.50.3",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "Sec-GPC": "1",
    "Referer": "https://eda.yandex.ru/retail/perekrestok?placeSlug=perekrestok_nmdiv"
}
#заполнить магазин pyaterochka_cpmsn perekrestok_nmdiv vkusvill_profsoyuznaya_26_lojgm
slug = "pyaterochka_cpmsn"
latitude = 55.67740842930555
longitude = 37.55965071682982
url = "https://eda.yandex.ru/api/v2/menu/goods?auto_translate=false"

response = requests.post(url, headers=headers, json={
    "slug": slug,
    "latitude": latitude,
    "longitude": longitude,
    "maxDepth": 100
})

if response.status_code == 200:
    category_ids = [category['id'] for category in response.json()['payload']['categories']]
    unique_products = set()  # Создаем set для хранения уникальных Public ID
    with open('products2.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Name', 'Category', 'Public ID', 'Weight', 'Price']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for category_id in category_ids:
            response = requests.post(url, headers=headers, json={
                "slug": slug,
                "latitude": latitude,
                "longitude": longitude,
                "category_uid": str(category_id),
                "maxDepth": 100
            })
            if response.status_code == 200:
                data = response.json()
                for subcategory in data['payload']['categories']:
                    for item in subcategory['items']:
                        public_id = item['public_id']
                        if public_id not in unique_products:
                            unique_products.add(public_id)
                            row = {
                                'Name': item['name'],
                                'Category': data['payload']['categories'][0]['name'],
                                'Public ID': public_id,
                                'Weight': item.get('weight', ''),
                                'Price': item['price'],
                            }
                            writer.writerow(row)
                        else:
                            print("Already exists: " +str(len(unique_products)))
            else:
                print(f"Ошибка при получении данных для категории {category_id}: {response.status_code}")
else:
    print(f"Ошибка при получении списка категорий: {response.status_code}")