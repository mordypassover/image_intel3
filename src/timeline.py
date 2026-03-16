
def create_event_html(img, side, color_class):
    full_date = img.get("datetime", "")
    return f"""
        <div class="event {side} {color_class}">
            <div class="content">
                <div class="dot"></div>
                <div class="time">{full_date}</div>
                <div class="filename">{img.get("filename", "")}</div>
                <hr style="border: 0; border-top: 1px solid #eee; margin: 10px 0;">
                <div class="details"><strong>Camera:</strong> {img.get("camera_make", "")} {img.get("camera_model", "")}</div>
                <div class="details"><strong>GPS:</strong> {img.get("latitude", "")}, {img.get("longitude", "")}</div>
            </div>
        </div>
    """


def build_timeline_component(events_html):
    return f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;700&display=swap');

        .timeline-container {{
            direction: ltr;
            padding: 40px 0;
            font-family: 'Heebo', sans-serif;
            background-color: #f8f9fa;
            border-radius: 15px;
        }}

        .timeline {{
            position: relative;
            max-width: 900px;
            margin: 0 auto;
        }}

        /* הקו המרכזי */
        .timeline::after {{
            content: "";
            position: absolute;
            width: 4px;
            background: #d1d8e0;
            top: 0;
            bottom: 0;
            left: 50%;
            margin-left: -2px;
            border-radius: 10px;
        }}

        .event {{
            position: relative;
            width: 50%;
            padding: 15px 40px;
            box-sizing: border-box;
            transition: transform 0.3s ease;
        }}

        .event:hover {{
            transform: translateY(-5px);
        }}

        .event.left {{ left: 0; }}
        .event.right {{ left: 50%; }}
        .event.middle {{ left: 25%; width: 50%; text-align: center; }}

        .content {{
            background: white;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.05);
            position: relative;
            z-index: 2;
            border-top: 5px solid #2f5d8a; /* ברירת מחדל */
        }}

        /* נקודות על הציר */
        .dot {{
            position: absolute;
            width: 16px;
            height: 16px;
            background: white;
            border: 4px solid #2f5d8a;
            border-radius: 50%;
            top: 25px;
            z-index: 3;
        }}

        .left .dot {{ right: -48px; }}
        .right .dot {{ left: -48px; }}

        /* וריאציות צבעים לפי תאריך */
        .date-theme-0 .content {{ border-top-color: #2e86ab; }}
        .date-theme-0 .dot {{ border-color: #2e86ab; }}
        .date-theme-0 .time {{ color: #2e86ab; }}

        .date-theme-1 .content {{ border-top-color: #a29bfe; }}
        .date-theme-1 .dot {{ border-color: #a29bfe; }}
        .date-theme-1 .time {{ color: #a29bfe; }}

        .date-theme-2 .content {{ border-top-color: #fab1a0; }}
        .date-theme-2 .dot {{ border-color: #fab1a0; }}
        .date-theme-2 .time {{ color: #fab1a0; }}

        .date-theme-3 .content {{ border-top-color: #55efc4; }}
        .date-theme-3 .dot {{ border-color: #55efc4; }}
        .date-theme-3 .time {{ color: #55efc4; }}

        .time {{
            font-size: 13px;
            font-weight: 700;
            margin-bottom: 5px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}

        .filename {{
            font-size: 16px;
            font-weight: 800;
            color: #2d3436;
            word-break: break-all;
        }}

        .details {{
            font-size: 13px;
            color: #636e72;
            margin-top: 4px;
        }}

        /* רספונסיביות למובייל */
        @media screen and (max-width: 768px) {{
            .timeline::after {{ left: 30px; }}
            .event {{ width: 100%; padding-left: 60px; padding-right: 20px; left: 0 !important; }}
            .dot {{ left: 22px !important; }}
        }}
    </style>

    <div class="timeline-container">
        <div class="timeline">
            {events_html}
        </div>
    </div>
    """


def create_timeline(images_data):
    # סינון ומיון לפי תאריך
    dated_images = [img for img in images_data if img.get("datetime")]
    dated_images.sort(key=lambda img: img["datetime"])

    if not dated_images:
        return build_timeline_component('<div class="event middle"><div class="content">No Data Available</div></div>')

    events_html = ""
    current_date_str = ""
    color_index = -1

    for i, img in enumerate(dated_images):
        img_date = img["datetime"].split(" ")[0] if " " in img["datetime"] else img["datetime"]

        if img_date != current_date_str:
            current_date_str = img_date
            color_index = (color_index + 1) % 4

        side = "left" if i % 2 == 0 else "right"
        color_class = f"date-theme-{color_index}"

        events_html += create_event_html(img, side, color_class)

    return build_timeline_component(events_html)