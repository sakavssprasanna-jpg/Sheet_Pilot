import sys
import os

with open(r"C:\Users\VAJAYA\AppData\Local\Programs\Python\Python312\Lib\site-packages\google\genai\_transformers.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

# Print lines 640 to 680
start = 640
end = 680
for i in range(start, min(end, len(lines))):
    print(f"{i+1}: {lines[i]}", end="")
