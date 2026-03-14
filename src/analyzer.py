from map_view import sort_by_time
from extractor import extract_all
from geopy.distance import geodesic
from geopy.geocoders import Nominatim

"""{
    "total_images": 12,
    "images_with_gps": 10,
    "images_with_datetime": 11,
    "unique_cameras": ["Samsung Galaxy S23", "Apple iPhone 15 Pro", "Canon EOS R5"],
    "date_range": {"start": "2025-01-12", "end": "2025-01-16"},
    "insights": [
        "נמצאו 3 מכשירים שונים - ייתכן שהסוכן החליף מכשירים",
        "ב-13/01 הסוכן עבר ממכשיר Samsung ל-iPhone",
        "ריכוז של 3 תמונות באזור תל אביב",
        "המצלמה המקצועית (Canon) הופיעה רק פעם אחת - בנמל חיפה"
        ]
    }
"""
def total_images(images_data):
    return len(images_data)

def images_with_gps(images_data):
    pass

def images_with_datetime(images_data):
    return len(list(filter(lambda image: image["datetime"]!=False, images_data)))

def unique_cameras(images_data):
    pass

def date_range(images_data):# בודק טווח זמן מחזיר תאריך תמונה ראשונה ואחרונה.
    return {"start": sort_by_time(images_data)[0]["datetime"].split()[0],  "end": sort_by_time(images_data)[-1]["datetime"].split()[0]}



def detect_camera_switches(images_data):
    sorted_images = sorted(
        [img for img in images_data if img["datetime"]],
        key=lambda x: x["datetime"]
    )
    switches = []
    for i in range(1, len(sorted_images)):
        prev_cam = sorted_images[i - 1].get("camera_model")
        curr_cam = sorted_images[i].get("camera_model")
        if prev_cam and curr_cam and prev_cam != curr_cam:
            switches.append({
                "date": sorted_images[i]["datetime"],
                "from": prev_cam,
                "to": curr_cam
            })
    return switches

def get_city_name(lat, lon):
    geolocator = Nominatim(user_agent="my_app")

    location = geolocator.reverse(f"{lat}, {lon}", language="he")
    if location:
        address = location.raw.get("address", {})
        return address.get("city") or address.get("town") or address.get("village")

def pictures_in_range_detection(images_data, rad_range=1):
    clusters = []
    sorted_data = sorted(images_data, key=lambda img: (img["latitude"], img["longitude"]), reverse=True)

    while sorted_data:
        first_point = sorted_data.pop(0)
        source = (first_point["latitude"], first_point["longitude"])
        tmp_result = [first_point]

        remaining = []
        for img in sorted_data:
            destination = (img["latitude"], img["longitude"])
            distance = geodesic(source, destination).km

            if distance <= rad_range:
                tmp_result.append(img)
            else:
                remaining.append(img)

        sorted_data = remaining

        if len(tmp_result) > 1:
            clusters.append(tmp_result)

    result = []
    for cluster in clusters:
        city_name = get_city_name(cluster[0]["latitude"], cluster[0]["longitude"])
        result.append((city_name, len(cluster)))

    return result

def time_difference_detection(images_data, time_difference=12):
    pass

def location_repeat_detection(images_data):
    pass

def insights_organisation(images_data):
    return [
        detect_camera_switches(images_data),
        pictures_in_range_detection(images_data),
        time_difference_detection(images_data),
        location_repeat_detection(images_data)
    ]



def file_analysis(filepath):#מקבלת נתיב לתיקיה ומחלצת את המידע הלבנתי על ידי פונקציה ומחזירה אנליזה של התיקית תמונות
    extracted_data=extract_all(filepath)
    analysis = {"total_images": total_images(extracted_data),
                "images_with_gps": images_with_gps(extracted_data),
                "images_with_datetime": images_with_datetime(extracted_data),
                "unique_cameras": unique_cameras(extracted_data),
                "date_range": date_range(extracted_data),
                "insights": insights_organisation(extracted_data)}
    return analysis
