import folium
from datetime import datetime
import html


def clean_text(value, default="Unknown"):
    if value is None:
        return default

    text = str(value).replace("\x00", "").strip()
    return text if text else default


def parse_datetime(value):
    if not value:
        return None

    if isinstance(value, datetime):
        return value

    value = str(value).strip()

    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y:%m:%d %H:%M:%S",
        "%Y-%m-%d",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue

    return None


def to_float(value):
    try:
        if value is None or value == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def is_valid_coordinate(lat, lon):
    lat = to_float(lat)
    lon = to_float(lon)

    if lat is None or lon is None:
        return False

    if not (-90 <= lat <= 90):
        return False

    if not (-180 <= lon <= 180):
        return False

    return True


def normalize_record(item):
    if not isinstance(item, dict):
        return None

    filename = clean_text(item.get("filename"), "Unknown file")
    dt_obj = parse_datetime(item.get("datetime"))
    latitude = to_float(item.get("latitude"))
    longitude = to_float(item.get("longitude"))
    camera_make = clean_text(item.get("camera_make"), "Unknown")
    camera_model = clean_text(item.get("camera_model"), "Unknown")

    has_real_gps = is_valid_coordinate(latitude, longitude)

    return {
        "filename": filename,
        "datetime": dt_obj,
        "datetime_str": dt_obj.strftime("%Y-%m-%d %H:%M:%S") if dt_obj else "Unknown date",
        "latitude": latitude,
        "longitude": longitude,
        "camera_make": camera_make,
        "camera_model": camera_model,
        "has_gps": has_real_gps,
    }


def sort_by_time(arr):
    normalized = []

    for item in arr:
        record = normalize_record(item)
        if record is not None:
            normalized.append(record)

    return sorted(
        normalized,
        key=lambda x: x["datetime"] if x["datetime"] is not None else datetime.max
    )


def extract_center_of_map(list_location):
    if not list_location:
        return [32.0853, 34.7818]

    count = len(list_location)
    latitude_avg = sum(coord[0] for coord in list_location) / count
    longitude_avg = sum(coord[1] for coord in list_location) / count
    return [latitude_avg, longitude_avg]


def create_map(images_data):
    folium_colors = [
        'red', 'blue', 'green', 'purple', 'orange', 'darkred', 'lightred',
        'beige', 'darkblue', 'darkgreen', 'cadetblue', 'darkpurple',
        'pink', 'lightblue', 'lightgreen', 'gray', 'black', 'lightgray'
    ]

    device_to_color = {}
    color_index = 0

    if not isinstance(images_data, list):
        images_data = []

    sorted_data = sort_by_time(images_data)

    valid_records = [loc for loc in sorted_data if loc["has_gps"]]
    valid_coords = [[loc["latitude"], loc["longitude"]] for loc in valid_records]

    center_map = extract_center_of_map(valid_coords)
    m = folium.Map(location=center_map, zoom_start=10)

    if len(valid_coords) >= 2:
        folium.PolyLine(
            locations=valid_coords,
            color="#2980b9",
            weight=4,
            opacity=0.6,
            dash_array='10, 10'
        ).add_to(m)

    for loc in valid_records:
        device_id = f"{loc['camera_make']} {loc['camera_model']}".strip()

        if device_id not in device_to_color:
            device_to_color[device_id] = folium_colors[color_index % len(folium_colors)]
            color_index += 1

        icon_color = device_to_color[device_id]

        safe_filename = html.escape(loc["filename"])
        safe_datetime = html.escape(loc["datetime_str"])
        safe_device = html.escape(device_id)

        popup_content = f"""
        <div style="font-family: Arial, sans-serif; direction: ltr; text-align: left; padding: 10px; min-width: 200px;">
            <div style="font-weight: 700; color: #2c3e50; border-bottom: 2px solid {icon_color}; margin-bottom: 6px;">
                {safe_filename}
            </div>
            <div style="font-size: 12px; color: #7f8c8d;">{safe_datetime}</div>
            <div style="font-size: 13px; margin-top: 4px;"><strong>Device:</strong> {safe_device}</div>
            <div style="font-size: 12px; margin-top: 4px;">
                <strong>GPS:</strong> {loc["latitude"]}, {loc["longitude"]}
            </div>
        </div>
        """

        folium.Marker(
            [loc["latitude"], loc["longitude"]],
            popup=folium.Popup(popup_content, max_width=300),
            icon=folium.Icon(color=icon_color, icon='camera', prefix='fa')
        ).add_to(m)

    if len(valid_coords) == 1:
        m.location = valid_coords[0]
        m.zoom_start = 14
    elif len(valid_coords) > 1:
        m.fit_bounds(valid_coords)

    return m._repr_html_()