import json
import csv

TXT_FILE = "files/data.txt"
JSON_FILE = "files/data.json"
CSV_FILE = "files/data.csv"


# ── TXT ──────────────────────────────────────────────────────────────────────

def read_from_txt():
    with open(TXT_FILE, "r") as file:
        content = file.readlines()
        print(content)


def write_to_txt(str):
    with open(TXT_FILE, "a") as file:
        file.write(str)


# ── JSON ─────────────────────────────────────────────────────────────────────

def read_from_json():
    with open(JSON_FILE, "r") as file:
        data: dict = json.load(file)
        print(data)
    return data


def append_to_json(new_record: dict):
    data = read_from_json()

    data.append(new_record)

    with open(JSON_FILE, "w") as file:
        json.dump(data, file, indent=4)


# ── CSV ──────────────────────────────────────────────────────────────────────

def read_from_csv():
    with open(CSV_FILE, "r", newline="") as file:
        reader = csv.DictReader(file)
        rows = list(reader)
        print(rows)
    return rows


def append_to_csv(new_record: dict):
    with open(CSV_FILE, "r", newline="") as file:
        reader = csv.DictReader(file)
        fieldnames = reader.fieldnames

    with open(CSV_FILE, "a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writerow(new_record)


# ── Demo ─────────────────────────────────────────────────────────────────────

print("=== TXT ===")
read_from_txt()
write_to_txt("This is Python file handling\n")
read_from_txt()

print("\n=== JSON ===")
read_from_json()
append_to_json({"name": "Diana", "age": 28, "city": "Pune"})
read_from_json()

print("\n=== CSV ===")
read_from_csv()
append_to_csv({"name": "Diana", "age": 28, "city": "Pune"})
read_from_csv()
