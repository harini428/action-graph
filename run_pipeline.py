from extract import extract_items
from db import init_db, save_meeting, get_items

init_db()

with open("transcript.txt", "r", encoding="utf-8") as f:
    text = f.read()

items = extract_items(text)
meeting_id = save_meeting("Weekly Project Sync", text, items)

for row in get_items(meeting_id):
    print(row["type"], "|", row["task"], "|", row["owner"], "|", row["deadline"], "|", row["needs_review"])