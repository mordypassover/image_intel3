from datetime import datetime
from extractor import extract_all
from map_view import create_map
from timeline import create_timeline
from analyzer import file_analysis

def create_report(images_data, map_html, timeline_html, analysis):
    now = datetime.now().strftime("%d/%m/%Y %H:%M")

    # תובנות
    insights = analysis.get("insights", [])
    if not insights:
        insights_html = "<li>אין תובנות זמינות</li>"
    else:
        insights_html = "".join(f"<li>{i}</li>" for i in insights)

    # מצלמות
    cameras = analysis.get("unique_cameras", [])
    if not cameras:
        cameras_html = "<p>אין מצלמות מזוהות</p>"
    else:
        cameras_html = " ".join(f"<span class='badge'>{c}</span>" for c in cameras)

    # מפה וציר זמן – fallback אם ריקים
    map_html_display = map_html if map_html else "<p>אין נתוני מיקום להצגה</p>"
    timeline_html_display = timeline_html if timeline_html else "<p>אין נתוני ציר זמן להצגה</p>"

    html = f"""
    <!DOCTYPE html>
    <html lang="he" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Image Intel Report</title>
        <style>
            body {{
                font-family: Heebo, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background: #f4f6f8;
            }}
            .header {{
                background: linear-gradient(135deg,#1B4F72,#2E86AB);
                color: white;
                padding: 30px;
                border-radius: 12px;
                text-align: center;
                margin-bottom: 25px;
            }}
            .section {{
                background: white;
                padding: 20px;
                margin: 20px 0;
                border-radius: 10px;
                box-shadow: 0 3px 8px rgba(0,0,0,0.08);
            }}
            .section h2 {{
                border-bottom: 2px solid #eee;
                padding-bottom: 8px;
                margin-bottom: 15px;
            }}
            .stats {{
                display: flex;
                gap: 20px;
                justify-content: center;
                flex-wrap: wrap;
            }}
            .stat-card {{
                background: #E8F4FD;
                padding: 20px 30px;
                border-radius: 10px;
                text-align: center;
                min-width: 120px;
            }}
            .stat-number {{
                font-size: 2em;
                font-weight: bold;
                color: #1B4F72;
            }}
            .badge {{
                background: #2E86AB;
                color: white;
                padding: 6px 12px;
                border-radius: 15px;
                margin: 4px;
                display: inline-block;
                font-size: 0.9em;
            }}
            ul {{
                line-height: 1.8;
            }}
            .footer {{
                text-align:center;
                color:#888;
                margin-top:30px;
                font-size:0.9em;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Image Intel Report</h1>
            <p>נוצר ב-{now}</p>
        </div>

        <div class="section">
            <h2>סיכום</h2>
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-number">{analysis.get('total_images', 0)}</div>
                    <div>תמונות</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{analysis.get('images_with_gps', 0)}</div>
                    <div>עם GPS</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{len(cameras)}</div>
                    <div>מכשירים</div>
                </div>
            </div>
        </div>

        <div class="section">
            <h2>תובנות מרכזיות</h2>
            <ul>{insights_html}</ul>
        </div>

        <div class="section">
            <h2>מפה</h2>
            {map_html_display}
        </div>

        <div class="section">
            <h2>ציר זמן</h2>
            {timeline_html_display}
        </div>

        <div class="section">
            <h2>מכשירים</h2>
            {cameras_html}
        </div>

        <div class="footer">
              team  3
        </div>
    </body>
    </html>
    """
    return html


# if __name__ == "__main__":
#     images_data = extract_all(r"C:\Users\mordy\PycharmProjects\image_intel3\images\ready")
#
#     map_html = create_map(images_data)
#
#     timeline_html = create_timeline(images_data)
#
#     analysis = file_analysis(images_data)
#
#     html = create_report(images_data, map_html, timeline_html, analysis)
#     with open("test.html", "w", encoding="utf-8") as f:
#          f.write(html)