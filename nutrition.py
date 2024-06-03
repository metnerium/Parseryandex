import csv
import asyncio
import aiohttp
import re


async def fetch_product_data(session, row, semaphore):
    public_id = row['Public ID']
    async with semaphore:
        url = 'https://eda.yandex.ru/api/v2/menu/product?auto_translate=false'
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
        data = {
            # заполнить магазин pyaterochka_cpmsn perekrestok_nmdiv vkusvill_profsoyuznaya_26_lojgm
            'place_slug': 'pyaterochka_cpmsn',
            'product_public_id': public_id,
            'with_categories': True,
            'location': {
                'latitude': 55.67740842930555,
                'longitude': 37.55965071682982
            }
        }

        try:
            async with session.post(url, headers=headers, json=data) as response:
                if response.status == 200 and response.content_type == 'application/json':
                    data = await response.json()
                    if 'detailed_data' in data and data['detailed_data']:
                        for item in data['detailed_data']:
                            if 'payload' in item and 'energy_values' in item['payload']:
                                energy_values = item['payload']['energy_values']
                                energy_values_dict = {}
                                for ev in energy_values:
                                    value = re.sub(r'\xa0.*', '', ev['value'])
                                    energy_values_dict[ev['name']] = value.strip() or '0'

                                # Проверяем наличие всех необходимых данных
                                if ('fat' in energy_values_dict and
                                        'protein' in energy_values_dict and
                                        'carbohydrates' in energy_values_dict and
                                        'kcal' in energy_values_dict):
                                    row['Fat'] = energy_values_dict['fat']
                                    row['Protein'] = energy_values_dict['protein']
                                    row['Carbs'] = energy_values_dict['carbohydrates']
                                    row['KCal'] = energy_values_dict['kcal']
                                    # print(row)
                                elif('kcal' in energy_values_dict):
                                    row['Fat'] = '0'
                                    row['Protein'] = '0'
                                    row['Carbs'] = '0'
                                    row['KCal'] = energy_values_dict['kcal']
                                    print(f"Неполные данные для продукта с Public ID: {public_id}")

                    else:
                        print(f"Данные не найдены для продукта с Public ID: {public_id}")
                else:
                    print(f"Ошибка при запросе для Public ID {public_id}: {response.status} - {response.reason}")
        except Exception as e:
            print(f"Ошибка при запросе для Public ID {public_id}: {e}")
        print(row)
        return row


async def main():
    semaphore = asyncio.Semaphore(50)
    async with aiohttp.ClientSession() as session:
        with open('products2.csv', 'r', encoding='utf-8', errors='replace') as file:
            reader = csv.DictReader(file)
            fieldnames = reader.fieldnames + ['Fat', 'Protein', 'Carbs', 'KCal']
            rows = list(reader)

        tasks = []
        for row in rows:
            tasks.append(asyncio.create_task(fetch_product_data(session, row, semaphore)))

        updated_rows = await asyncio.gather(*tasks)

        with open('products2.csv', 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(updated_rows)

    print('Файл products.csv обновлен.')


if __name__ == '__main__':
    asyncio.run(main())