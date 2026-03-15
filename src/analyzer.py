from map_view import sort_by_time
from extractor import extract_all
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
from datetime import datetime

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

def parse_to_datetime(dt_input):
    """פונקציה אחת שמרכזת את כל ניקוי ותיקון התאריכים"""
    if not dt_input or not isinstance(dt_input, str):
        return None
    try:
        # פותר את בעיית הנקודתיים בפורמט EXIF
        clean_dt = dt_input.replace(":", "-", 2)
        return datetime.strptime(clean_dt, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None

def safe_parse(x):
    """משמשת את sort_by_time - מחזירה מקסימום אם התאריך פגום"""
    return parse_to_datetime(x.get("datetime")) or datetime.max

def total_images(images_data):
    return len(images_data)

def images_with_gps(images_data):
    return sum(1 for img in images_data if img.get("datetime"))

def images_with_datetime(images_data):
    return len(list(filter(lambda image: image["datetime"]!=False, images_data)))

def unique_cameras(images_data):
    return list(set(image['camera_model'] for image in images_data))

def date_range(images_data):
    sorted_data = sort_by_time(images_data)
    return {
        "start": sorted_data[0]["datetime"].split()[0],
        "end": sorted_data[-1]["datetime"].split()[0]
    }

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
    return None


def pictures_in_range_detection(images_data, rad_range=1):
    gps_only = [img for img in images_data if img.get("has_gps") and img.get("latitude") is not None]
    if not gps_only:
        return []

    sorted_data = sorted(gps_only, key=lambda img: (img["latitude"], img["longitude"]))
    clusters = []
    visited = set()

    for i in range(len(sorted_data)):
        if i in visited:
            continue

        current_cluster = []
        queue = [i]
        visited.add(i)

        while queue:
            current_idx = queue.pop(0)
            current_node = sorted_data[current_idx]
            current_cluster.append(current_node)

            source_coord = (current_node["latitude"], current_node["longitude"])

            # חיפוש "שכנים" לנקודה הנוכחית בשרשרת
            for j in range(len(sorted_data)):
                if j not in visited:
                    target_coord = (sorted_data[j]["latitude"], sorted_data[j]["longitude"])
                    # אם התמונה קרובה למישהו שכבר בשרשרת - היא נגררת פנימה
                    if geodesic(source_coord, target_coord).km <= rad_range:
                        visited.add(j)
                        queue.append(j)

        # רק אם מצאנו קבוצה (יותר מתמונה אחת)
        if len(current_cluster) > 1:
            clusters.append(current_cluster)

    # 2. המרת הקלאסטרים לפורמט הנדרש (עיר, כמות)
    result = []
    for cluster in clusters:
        # לוקחים את שם העיר של הנקודה הראשונה בקבוצה
        city_name = get_city_name(cluster[0]["latitude"], cluster[0]["longitude"])
        city_name = city_name if city_name else "מיקום לא ידוע"
        result.append((city_name, len(cluster)))

    return result

def time_difference_detection(images_data, time_difference=12):
    if len(images_data) < 2:
        return []

    sorted_images = sort_by_time(images_data)
    flagged_filenames = set()

    for i in range(len(sorted_images) - 1):
        # שימוש בפונקציה המרכזית שסידרנו למעלה
        current_dt = parse_to_datetime(sorted_images[i].get("datetime"))
        next_dt = parse_to_datetime(sorted_images[i + 1].get("datetime"))

        if not current_dt or not next_dt:
            continue

        # חישוב הפרש השעות
        diff_hours = (next_dt - current_dt).total_seconds() / 3600

        if diff_hours >= time_difference:
            flagged_filenames.add(sorted_images[i]["filename"])
            flagged_filenames.add(sorted_images[i + 1]["filename"])

    return [img for img in sorted_images if img["filename"] in flagged_filenames]

def location_repeat_detection(images_data, radius_km=0.2):

    gps_images = [img for img in images_data if img.get("has_gps")]

    repeats = []

    for i in range(len(gps_images)):
        for j in range(i + 1, len(gps_images)):

            coord1 = (gps_images[i]["latitude"], gps_images[i]["longitude"])
            coord2 = (gps_images[j]["latitude"], gps_images[j]["longitude"])

            distance = geodesic(coord1, coord2).km

            if distance <= radius_km:

                city = get_city_name(*coord1)

                repeats.append(
                    f"הסוכן חזר למיקום באזור {city}"
                )

                break

    return list(repeats)

def format_insights(
    switches: list[dict],
    clusters: list[tuple[str, int]],
    time_gaps: list[dict],
    repeated_cities: list[str]) -> list[str]:
    insights = []

    # החלפות מצלמה
    if switches:
        total = len(switches)
        insights.append(f"נמצאו {total} החלפות מצלמה")
        for s in switches:
            insights.append(f"הסוכן החליף מ-{s['from']} ל-{s['to']} ב-{s['date']}")

    # ריכוזי תמונות
    for city, count in clusters:
        insights.append(f"ריכוז של {count} תמונות ב{city}")

    # פערי זמן
    if time_gaps:
        filenames = [img["filename"] for img in time_gaps]
        insights.append(f"נמצאו פערי זמן גדולים סביב: {', '.join(filenames)}")

    # חזרה למיקומים
    for city in repeated_cities:
        insights.append(f"הסוכן חזר למיקום באזור {city}")

    return insights

def insights_organisation(images_data):
    switches = detect_camera_switches(images_data)
    clusters = pictures_in_range_detection(images_data)
    time_gaps = time_difference_detection(images_data)
    repeated_cities = location_repeat_detection(images_data)

    return format_insights(switches, clusters, time_gaps, repeated_cities)

def file_analysis(filepath) -> dict:
    extracted_data = extract_all(filepath)
    return {
        "total_images": total_images(extracted_data),
        "images_with_gps": images_with_gps(extracted_data),
        "images_with_datetime": images_with_datetime(extracted_data),
        "unique_cameras": unique_cameras(extracted_data),
        "date_range": date_range(extracted_data),
        "insights": insights_organisation(extracted_data)
    }
