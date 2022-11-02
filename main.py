import requests
from bs4 import BeautifulSoup as BS
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS


def img_parser(link):
    # Парсинг страницы по ссылке
    r = requests.get(link)
    html = BS(r.content, 'html.parser')

    images = []  # Массив ссылок на изображения
    for img in html.findAll('img'):  # Заносим в массив все ссылки на изображения
        images.append(img.get('src'))

    return images


# Функция скачивания изображения
def get_img(img_url):
    with open('img.png', 'wb') as handle:
        img_data = requests.get(img_url).content
        handle.write(img_data)


def get_exif(filename):
    exif = Image.open(filename).getexif()

    if exif is not None:
        for key, value in exif.items():
            name = TAGS.get(key, key)
            exif[name] = exif.pop(key)

        if 'GPSInfo' in exif:
            for key in exif['GPSInfo'].keys():
                name = GPSTAGS.get(key, key)
                exif['GPSInfo'][name] = exif['GPSInfo'].pop(key)

    return exif


metadata = get_exif('image.jpg')
print(metadata)