from PIL import Image
from PIL.ExifTags import TAGS
from pathlib import Path
import os

"""
extractor.py - שליפת EXIF מתמונות
צוות 1, זוג A

ראו docs/api_contract.md לפורמט המדויק של הפלט.

"""


def has_gps(data: dict):
    return "GPSInfo" in data


def latitude(data: dict):
    gps = data.get("GPSInfo")
    if not gps:
        return None

    lat = gps.get(2)
    ref = gps.get(1)

    if not lat:
        return None

    deg, minute, sec = lat
    value = deg + float(minute) / 60 + float(sec) / 3600

    if ref == "S":
        value = -value

    return round(value, 4)

def longitude(data: dict):
    gps = data.get("GPSInfo")
    if not gps:
        return None

    lon = gps.get(4)
    ref = gps.get(3)

    if not lon:
        return None

    deg, minute, sec = lon
    value = deg + float(minute) / 60 + float(sec) / 3600

    if ref == "W":
        value = -value

    return round(value, 4)

def datatime(data: dict):
    return data['DateTimeOriginal'] if 'DateTimeOriginal' in data else None


def camera_make(data: dict):
    return data['Make'] if 'Make' in data else None


def camera_model(data: dict):
    return data['Model'] if 'Model' in data else None


def extract_metadata(image_path):
    """
    שולף EXIF מתמונה בודדת.

    Args:
        image_path: נתיב לקובץ תמונה

    Returns:
        dict עם: filename, datetime, latitude, longitude,
              camera_make, camera_model, has_gps
    """
    path = Path(image_path)

    # תיקון: טיפול בתמונה בלי EXIF - בלי זה, exif.items() נופל עם AttributeError
    try:
        img = Image.open(image_path)
        exif = img._getexif()
    except Exception:
        exif = None

    if exif is None:
        return {
            "filename": path.name,
            "datetime": None,
            "latitude": None,
            "longitude": None,
            "camera_make": None,
            "camera_model": None,
            "has_gps": False
        }

    data = {}
    for tag_id, value in exif.items():
        tag = TAGS.get(tag_id, tag_id)
        data[tag] = value

    # תיקון: הוסר print(data) שהיה כאן - הדפיס את כל ה-EXIF הגולמי על כל תמונה

    exif_dict = {
        "filename": path.name,
        "datetime": datatime(data),
        "latitude": latitude(data),
        "longitude": longitude(data),
        "camera_make": camera_make(data),
        "camera_model": camera_model(data),
        "has_gps": has_gps(data)
    }
    return exif_dict


def extract_all(folder_path):
    """
    שולף EXIF מכל התמונות בתיקייה.

    Args:
        folder_path: נתיב לתיקייה

    Returns:
        list של dicts (כמו extract_metadata)
    """
    final_list=[]
    for image_path in Path(folder_path).iterdir():
        if image_path.is_file():
            final_list.append(extract_metadata(image_path))
        elif image_path.is_dir() and not image_path.is_symlink():
            final_list += extract_all(image_path)
    return final_list

print(extract_all(r"C:\Users\USER\PycharmProjects\image_intel3\images\ready"))