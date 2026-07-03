import re

with open("src/courseData.js", "r") as f:
    content = f.read()

# Delete Tab 7, 8, 9
content = re.sub(r',\s*"7": makeLesson\(\{[\s\S]*', '\n};', content)

with open("src/courseData.js", "w") as f:
    f.write(content)

print("courseData.js updated successfully for Tab 7, 8, 9")
