from map_view import sort_by_time
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
    pass

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

def pictures_in_range_detection(images_data,rad_range):
    pass

def time_difference_detection(images_data, time_difference):
    pass

def location_repeat_detection(images_data):
    pass

def file_analysis(images_data):
    pass