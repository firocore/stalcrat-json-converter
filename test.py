import json

with open("json-database/listing.json", 'r') as file:
    file = json.load(file)

names = []
for rows in file:
    names.append(rows.get('name'))

print(names)