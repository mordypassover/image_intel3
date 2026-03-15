
def create_event_html(img, side):
    return f"""
        <div class="event {side}">
            <div class="content">
                <div class="time">{img["datetime"]}</div>
                <div class="filename">{img["filename"]}</div>
                <div class="details"><strong>Camera Make:</strong> {img["camera_make"]}</div>
                <div class="details"><strong>Camera Model:</strong> {img["camera_model"]}</div>
                <div class="details"><strong>Has GPS:</strong> {img["has_gps"]}</div>
                <div class="details"><strong>Latitude:</strong> {img["latitude"]}</div>
                <div class="details"><strong>Longitude:</strong> {img["longitude"]}</div>
            </div>
        </div>
    """


def build_page_html(events_html):
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Image Timeline</title>

        <style>
            * {{
                box-sizing: border-box;
            }}

            body {{
                margin: 0;
                font-family: Heebo, sans-serif;
                background: #f4f7fb;
                color: #222;
                padding: 40px 20px;
            }}

            .page-title {{
                text-align: center;
                margin-bottom: 40px;
            }}

            .page-title h1 {{
                margin: 0;
                font-size: 32px;
                color: #1f3b5b;
            }}

            .page-title p {{
                margin-top: 10px;
                color: #666;
                font-size: 16px;
            }}

            .timeline {{
                position: relative;
                max-width: 1000px;
                margin: 0 auto;
                padding: 20px 0;
            }}

            .timeline::after {{
                content: "";
                position: absolute;
                width: 4px;
                background: #2f5d8a;
                top: 0;
                bottom: 0;
                left: 50%;
                margin-left: -2px;
                border-radius: 2px;
            }}

            .event {{
                position: relative;
                width: 50%;
                padding: 20px 40px;
            }}

            .event.left {{
                left: 0;
            }}

            .event.right {{
                left: 50%;
            }}
                        
            .event.middle {{
                left: 50%;
                transform: translateX(-50%);
                width: 50%;
                text-align: center;
            }}

            .content {{
                background: white;
                padding: 18px;
                border-radius: 12px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
                position: relative;
                z-index: 2;
            }}

            .time {{
                font-weight: bold;
                color: #2f5d8a;
                margin-bottom: 10px;
            }}

            .filename {{
                font-size: 18px;
                font-weight: bold;
                margin-bottom: 10px;
                color: #1f1f1f;
            }}

            .details {{
                margin-bottom: 6px;
                color: #444;
                font-size: 14px;
            }}

            @media screen and (max-width: 768px) {{
                .timeline::after {{
                    left: 20px;
                }}

                .event {{
                    width: 100%;
                    padding-left: 50px;
                    padding-right: 20px;
                }}

                .event.left,
                .event.right {{
                    left: 0;
                }}
            }}
        </style>
    </head>
    <body>

        <div class="page-title">
            <h1>Image Timeline</h1>
            <p>Chronological visual display of image data</p>
        </div>

        <div class="timeline">
            {events_html}
        </div>

    </body>
    </html>
    """


def create_timeline(images_data):

    dated_images = [img for img in images_data if img.get("datetime")]
    dated_images.sort(key=lambda img: img["datetime"])

    if not dated_images:
        events_html = """
        <div class="event middle">
            <div class="content">
                <div class="time">No timeline data</div>
                <div class="details">No images with datetime metadata were found.</div>
            </div>
        </div>
        """
        return build_page_html(events_html)

    events_html = ""

    if len(dated_images) == 1:
        events_html += create_event_html(dated_images[0], "middle")
        return build_page_html(events_html)

    for i, img in enumerate(dated_images):
        side = "left" if i % 2 == 0 else "right"
        events_html += create_event_html(img, side)

    return build_page_html(events_html)

if __name__ == "__main__":
    fake_data = [
        {"filename": "test1.jpg", "latitude": 32.0853, "longitude": 34.7818,
         "has_gps": True, "camera_make": "Samsung", "camera_model": "Galaxy S23",
         "datetime": "2025-01-12 08:30:00"},
        {"filename": "test2.jpg", "latitude": 31.7683, "longitude": 35.2137,
         "has_gps": True, "camera_make": "Apple", "camera_model": "iPhone 15 Pro",
         "datetime": "2025-01-13 09:00:00"},
    ]
    html = create_timeline(fake_data)
    with open("test7.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Map saved to test_map.html")