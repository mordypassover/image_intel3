import folium
from datetime import datetime

def sort_by_time(arr):
    return sorted(arr, key=lambda x: datetime.strptime(x["datetime"], "%Y-%m-%d %H:%M:%S") if x.get(
        "datetime") else datetime.max)


def extract_center_of_map(list_location: list[dict]) -> list:
    if not list_location:
        return [32.0853, 34.7818]
    count = len(list_location)
    latitude_avg = sum(coord[0] for coord in list_location) / count
    longitude_avg = sum(coord[1] for coord in list_location) / count
    return [latitude_avg, longitude_avg]


def create_map(images_data):
    # רשימת הצבעים
    folium_colors = ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 'lightred', 'beige', 'darkblue',
                     'darkgreen', 'cadetblue', 'darkpurple', 'pink', 'lightblue', 'lightgreen', 'gray', 'black',
                     'lightgray']

    device_to_color = {}
    color_index = 0

    sorted_data = sort_by_time(images_data)
    valid_coords = [[loc["latitude"], loc["longitude"]] for loc in sorted_data if loc.get("has_gps")]
    center_map = extract_center_of_map(valid_coords)
    m = folium.Map(location=center_map)

    # בונה קווים בין הנקודות
    folium.PolyLine(locations=valid_coords, color="#2980b9", weight=4, opacity=0.6, dash_array='10, 10').add_to(m)

    # ממרקר כל תמונה על המפה אם אייקון מצלמה וטקסט פנימי מעוצב על ידי בינה מלאכותית
    for loc in images_data:
        if loc.get("has_gps"):
            device_id = f"{loc.get('camera_make', '')} {loc.get('camera_model', '')}".strip()
            if device_id not in device_to_color:
                device_to_color[device_id] = folium_colors[color_index % len(folium_colors)]
                color_index += 1

            icon_color = device_to_color[device_id]

            popup_content = f"""
            <link href="https://fonts.googleapis.com/css2?family=Heebo:wght@400;700&display=swap" rel="stylesheet">
            <div style="font-family: 'Heebo', sans-serif; direction: ltr; text-align: left; padding: 10px; min-width: 180px;">
                <div style="font-weight: 700; color: #2c3e50; border-bottom: 2px solid {icon_color};">{loc['filename']}</div>
                <div style="font-size: 12px; color: #7f8c8d;">📅 {loc['datetime']}</div>
                <div style="font-size: 13px;"><strong>Device:</strong> {device_id}</div>
            </div>
            """

            folium.Marker(
                [loc["latitude"], loc["longitude"]],
                popup=folium.Popup(popup_content, max_width=300),
                icon=folium.Icon(color=icon_color, icon='camera')
            ).add_to(m)
    # מתכווץ ומתרחב לפי הנקודות על המפה
    if valid_coords:
        m.fit_bounds(valid_coords)

    return m._repr_html_()