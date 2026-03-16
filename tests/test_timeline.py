from src.extractor import extract_all
from src.timeline import create_timeline

ready = extract_all(r"C:\Users\Shimshon\PycharmProjects\image_intel3\images\ready")
sample_data = extract_all(r"C:\Users\Shimshon\PycharmProjects\image_intel3\images\sample_data")
uploads = extract_all(r"C:\Users\Shimshon\PycharmProjects\image_intel3\images\uploads")

all_data = sample_data + ready + uploads

print(all_data)

html = create_timeline(all_data)

with open("timeline.html", "w", encoding="utf8") as f:
    f.write(html)