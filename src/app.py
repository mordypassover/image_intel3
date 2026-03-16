from flask import Flask, render_template, request
import os
import tempfile

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/analyze', methods=['POST'])
def analyze_images():

    folder_path = request.form.get('folder_path')
    uploaded_files = request.files.getlist('photos')

    # מצב א': הגיע נתיב תיקייה
    if folder_path and folder_path.strip():
        folder_path = folder_path.strip()
        if not os.path.isdir(folder_path):
            return f"תיקייה לא נמצאה: '{folder_path}'", 400

    # מצב ב': הגיעו קבצים - שומרים אותם בתיקייה זמנית
    elif uploaded_files and uploaded_files[0].filename:
        tmp_dir = tempfile.mkdtemp()
        for f in uploaded_files:
            f.save(os.path.join(tmp_dir, f.filename))
        folder_path = tmp_dir

    else:
        return "לא נשלחו קבצים או נתיב", 400

    # שלב 1: שליפת נתונים
    from extractor import extract_all
    images_data = extract_all(folder_path)

    # שלב 2: יצירת מפה
    from map_view import create_map
    map_html = create_map(images_data)

    # שלב 3: ציר זמן
    from timeline import create_timeline
    timeline_html = create_timeline(images_data)

    # שלב 4: ניתוח
    from analyzer import file_analysis
    analysis = file_analysis(images_data)

    # שלב 5: הרכבת דו"ח
    from report import create_report
    return create_report(images_data, map_html, timeline_html, analysis)


if __name__ == '__main__':
    app.run(debug=True)