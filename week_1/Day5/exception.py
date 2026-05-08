import csv
import json

class MissingColumnError(Exception):
    pass

def validate_csv(file_path, req_cols):
    cleaned_data = []

    with open(file_path, "r") as file:
        reader = csv.DictReader(file)

        csv_columns = reader.fieldnames
        for col in req_cols:
            if col not in csv_columns:
                raise MissingColumnError(f"Missing required column: {col}")
        
        for row in reader:
            clean_row = {}

            for col in req_cols:
                value = row[col].strip()

                if value == "":
                    raise ValueError(f"Empty value in required column: {col}")
                clean_row[col] = value
            cleaned_data.append(clean_row)
    return cleaned_data

def save_json(data, output_file):
    with open(output_file, "w") as file:
        json.dump(data, file, indent=4)

try:
    req_cols = ["First Name", "Last Name", "Email", "Job Title"]
    data = validate_csv("people-100.csv", req_cols)
    save_json(data, "output.json")
    print("CSV validated and converted to json successfully")

except MissingColumnError as e:
    print("Column Error:", e)

except ValueError as e:
    print("Data Error:", e)

except Exception as e:
    print("Unexpected Error:", e)