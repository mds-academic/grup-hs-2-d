import re
import json

html_path = '/Users/yazidhilmi/Documents/cloud/Kalananti-cloud/Academic_Content/B2B/UOB/Async/Highschool/sesi40-44/slide_deck_part1.html'
with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find all slides
# <div class="slide" data-title="PROYEK PYTHON" data-subtitle="Celengan Pintar">
slide_pattern = re.compile(r'data-title="([^"]+)"\s+data-subtitle="([^"]+)"')
slides = slide_pattern.findall(content)

# Group by kicker (data-title)
groups = []
current_kicker = None
current_group = None

for title, subtitle in slides:
    if title != current_kicker:
        if current_group:
            groups.append(current_group)
        current_kicker = title
        current_group = {
            "kicker": title,
            "title": subtitle, # Use first subtitle as title for the chapter, or custom
            "duration": "15 Menit",
            "videoId": "TBC",
            "startSeconds": 0,
            "endSeconds": 0,
            "bookmarks": [],
            "quizzes": []
        }
    current_group["bookmarks"].append({
        "time": len(current_group["bookmarks"]) * 60, # 1 minute apart just for structure
        "label": subtitle
    })

if current_group:
    groups.append(current_group)

# Adjust titles to be more descriptive than just the first slide's subtitle
titles_map = {
    "PROYEK PYTHON": "Merancang Aplikasi Impian",
    "BERTANYA SEBELUM BERAKSI": "Design Thinking & Kebutuhan Pengguna",
    "MERANCANG PROGRAM": "Flowchart & Use Case",
    "DATA CELENGAN": "Menganalisis Data Transaksi",
    "FINANCIAL DATA": "Logika & Rekomendasi Pintar",
    "APP INTEGRATION": "Menyatukan Kode Program",
    "FINAL PROJECT": "Membangun Proyek Utama",
    "WRAP UP": "Rangkuman Pembelajaran",
    "EXIT TICKET": "Refleksi Diri"
}

course_data_str = "export const courseData = {\n"
for i, group in enumerate(groups, 1):
    group["title"] = titles_map.get(group["kicker"], group["title"])
    course_data_str += f'  "{i}": {json.dumps(group, indent=4)},\n'

course_data_str = course_data_str.rstrip(",\n") + "\n};\n"

with open('/Users/yazidhilmi/Documents/cloud/Kalananti-cloud/Academic_Content/B2B/UOB/Async/Highschool/sesi40-44/grup-hs-2-d/src/courseData.js', 'w', encoding='utf-8') as f:
    f.write(course_data_str)

print(f"Generated {len(groups)} chapters in courseData.js")
