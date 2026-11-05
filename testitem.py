import db

items = db.get_all_items()
print("Rows:", len(items))
print(items[:2])