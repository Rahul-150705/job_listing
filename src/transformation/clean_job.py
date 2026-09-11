import json
import pandas as pd
from pathlib import Path


# ==========================================
# 1. FIND PROJECT ROOT
# ==========================================

# clean_job.py
#     ↓
# transformation
#     ↓
# src
#     ↓
# project root

project_root = Path(__file__).resolve().parents[2]

input_file = project_root / "data" / "raw" / "jobs.json"
output_dir = project_root / "data" / "processed"
output_file = output_dir / "jobs.csv"


# ==========================================
# 2. CHECK INPUT FILE
# ==========================================

if not input_file.exists():
    print("ERROR: jobs.json was not found.")
    print("Expected location:")
    print(input_file)
    exit()


print("Input file:")
print(input_file)


# ==========================================
# 3. LOAD RAW JSON
# ==========================================

with open(input_file, "r", encoding="utf-8") as file:
    data = json.load(file)


# ==========================================
# 4. GET JOB RESULTS
# ==========================================

jobs = data.get("results", [])

print("\nTotal jobs in current API response:", len(jobs))


if not jobs:
    print("ERROR: No jobs found inside 'results'.")
    exit()


# ==========================================
# 5. EXTRACT USEFUL FIELDS
# ==========================================

cleaned_jobs = []

for job in jobs:

    company = job.get("company") or {}
    location = job.get("location") or {}
    category = job.get("category") or {}

    cleaned_job = {
        "job_id": job.get("id"),
        "title": job.get("title"),
        "company": company.get("display_name"),
        "location": location.get("display_name"),
        "description": job.get("description"),
        "contract_time": job.get("contract_time"),
        "salary_predicted": job.get("salary_is_predicted"),
        "latitude": job.get("latitude"),
        "longitude": job.get("longitude"),
        "category": category.get("label"),
        "created": job.get("created"),
        "job_url": job.get("redirect_url")
    }

    cleaned_jobs.append(cleaned_job)


# ==========================================
# 6. CREATE DATAFRAME
# ==========================================

df = pd.DataFrame(cleaned_jobs)

print("\n------------------------------------------")
print("DATA BEFORE CLEANING")
print("------------------------------------------")

print(df.head())

print("\nNumber of rows:", len(df))
print("Number of columns:", len(df.columns))


# ==========================================
# 7. REMOVE DUPLICATE JOBS
# ==========================================

before_duplicates = len(df)

df = df.drop_duplicates(
    subset=["job_id"],
    keep="first"
)

after_duplicates = len(df)

print("\nDuplicates removed:",
      before_duplicates - after_duplicates)


# ==========================================
# 8. CLEAN TEXT COLUMNS
# ==========================================

text_columns = [
    "title",
    "company",
    "location",
    "description",
    "category"
]

for column in text_columns:

    df[column] = (
        df[column]
        .astype("string")
        .str.strip()
    )


# ==========================================
# 9. CLEAN EMPTY STRINGS
# ==========================================

for column in text_columns:

    df[column] = df[column].replace(
        ["", "nan", "None"],
        pd.NA
    )


# ==========================================
# 10. CONVERT DATE
# ==========================================

df["created"] = pd.to_datetime(
    df["created"],
    errors="coerce",
    utc=True
)


# ==========================================
# 11. CONVERT SALARY FLAG
# ==========================================

df["salary_predicted"] = pd.to_numeric(
    df["salary_predicted"],
    errors="coerce"
)


# ==========================================
# 12. REMOVE JOBS WITHOUT JOB ID
# ==========================================

before_missing_id = len(df)

df = df.dropna(
    subset=["job_id"]
)

after_missing_id = len(df)

print(
    "Rows removed because of missing job ID:",
    before_missing_id - after_missing_id
)


# ==========================================
# 13. RESET INDEX
# ==========================================

df = df.reset_index(drop=True)


# ==========================================
# 14. CREATE PROCESSED DIRECTORY
# ==========================================

output_dir.mkdir(
    parents=True,
    exist_ok=True
)


# ==========================================
# 15. SAVE PROCESSED DATA
# ==========================================

df.to_csv(
    output_file,
    index=False,
    encoding="utf-8"
)


# ==========================================
# 16. VERIFY FILE
# ==========================================

print("\n------------------------------------------")
print("DATA AFTER CLEANING")
print("------------------------------------------")

print(df.head())

print("\nNumber of processed jobs:", len(df))

print("\nData types:")
print(df.dtypes)

print("\nMissing values:")
print(df.isna().sum())


print("\n------------------------------------------")
print("OUTPUT")
print("------------------------------------------")

print("Saved to:")
print(output_file)

print("\nFile exists:", output_file.exists())

if output_file.exists():

    print(
        "File size:",
        round(output_file.stat().st_size / 1024, 2),
        "KB"
    )

    print("\nSUCCESS: jobs.csv created successfully!")

else:

    print("\nERROR: jobs.csv was not created.")