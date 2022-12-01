import requests
from bs4 import BeautifulSoup as BS
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS


# Парсинг всех изображений на сайте
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


# Возвращает словарь из exif-данных изображения и конвертирует GPS
def get_exif_data(image):
    exif_data = {}
    info = image._getexif()
    if info:
        for tag, value in info.items():
            decoded = TAGS.get(tag, tag)
            if decoded == "GPSInfo":
                gps_data = {}
                for t in value:
                    sub_decoded = GPSTAGS.get(t, t)
                    gps_data[sub_decoded] = value[t]

                exif_data[decoded] = gps_data
            else:
                exif_data[decoded] = value

    return exif_data


# Проверяет существование данных координат в метаданных изображения
def _get_if_exist(data, key):
    if key in data:
        return data[key]

    return None


# Функция конвертации GPS-координат в градусы в float-формате
def convert_to_degrees(value):
    degrees = value[0]
    minutes = value[1] / 60.0
    seconds = value[2] / 3600.0

    return degrees + minutes + seconds


# Возвращает широту и долготу из полученных exif-данных, если возможно
def get_lat_lon(exif_data):
    lat = None
    lon = None

    if "GPSInfo" in exif_data:
        gps_info = exif_data["GPSInfo"]

        gps_latitude = _get_if_exist(gps_info, "GPSLatitude")
        gps_latitude_ref = _get_if_exist(gps_info, 'GPSLatitudeRef')
        gps_longitude = _get_if_exist(gps_info, 'GPSLongitude')
        gps_longitude_ref = _get_if_exist(gps_info, 'GPSLongitudeRef')

        if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
            lat = convert_to_degrees(gps_latitude)
            if gps_latitude_ref != "N":
                lat = 0 - lat

            lon = convert_to_degrees(gps_longitude)
            if gps_longitude_ref != "E":
                lon = 0 - lon

    return lat, lon


# Проверяет координаты изображения и их причастность к Иркутской области
def check_within(object):
    if object[0] is None or object[1] is None:
        return None  # Нет координат

    lat = 48.1710037793, 66.2334166789
    lon = 93.8312147383, 122.198214607
    if lat[0] < object[0] < lat[1] and lon[0] < object[0] < lon[1]:
        return True  # Координаты принадлежат Иркутской области
    else:
        return False  # Координаты не принадлежат Иркутской области


if __name__ == "__main__":
    source_image = Image.open('./image.jpg')
    exif = get_exif_data(source_image)
    coordinates = get_lat_lon(exif)
    print(check_within(coordinates))
