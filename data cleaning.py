import pandas as pd
import numpy as np
import sys
import re

np.set_printoptions(threshold=500)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

try:
    df = pd.read_csv(r"C:\Users\TUF\PycharmProjects\data\.venv\Scripts\output\crag_routes.csv")
except FileNotFoundError:
    print("Error: The CSV file was not found. Please update the file path.")
    sys.exit(1)

df = df.drop_duplicates()
df['Route Name'] = df['Route Name'].astype(str).str.strip("★")

df = df.dropna(subset=['Grade'])

original_df = df.copy()
original_df['Grade_Str'] = original_df['Grade'].astype(str).str.upper()
original_df['Grade_Str_Cleaned'] = original_df['Grade_Str'].str.replace(r'\s+', '', regex=True)

df_working = original_df.copy()

mixed_df = df_working[df_working['Grade_Str_Cleaned'].str.startswith('M', na=False)].copy()
df_working = df_working.drop(mixed_df.index)

ice_df = df_working[df_working['Grade_Str_Cleaned'].str.startswith('WI', na=False)].copy()
df_working = df_working.drop(ice_df.index)

aid_pattern = r'\b[A|C]\d+|\b[A|C]$'
aid_df = df_working[df_working['Grade_Str_Cleaned'].str.contains(aid_pattern, na=False)].copy()
df_working = df_working.drop(aid_df.index)

bouldering_df = df_working[df_working['Grade_Str_Cleaned'].str.contains(r'\{FB\}', na=False)].copy()
df_working = df_working.drop(bouldering_df.index)

alpine_pattern = r'(\d[+-]?)(\d[A|B])|(D|E|B/C|IFAS:AD|R\d)'
alpine_df = df_working[df_working['Grade_Str_Cleaned'].str.contains(alpine_pattern, na=False)].copy()
df_working = df_working.drop(alpine_df.index)

free_climbing_df = df_working.copy()

print(f"\n--- DATA SPLIT SUMMARY ---")
print(f"Mixed Routes: {len(mixed_df)}")
print(f"Ice Routes: {len(ice_df)}")
print(f"Aid Routes: {len(aid_df)}")
print(f"Bouldering Routes: {len(bouldering_df)}")
print(f"Alpine/Combined Routes: {len(alpine_df)}")
print(f"Free Climbing Routes to Standardize: {len(free_climbing_df)}")

integer_grade_pattern = r'^\s*([1-9]|10)[+-]?\s*$'

integer_grades_df = free_climbing_df[
    free_climbing_df['Grade_Str'].str.match(integer_grade_pattern, na=False)
].copy()

free_climbing_df_complex = free_climbing_df.drop(integer_grades_df.index)

uiaa_to_french = {
    '5': '4c', '5+': '5a',
    '6-': '5a', '6': '5b', '6+': '5c',
    '7-': '6a', '7': '6a+', '7+': '6b',
    '8-': '6b+', '8': '6c', '8+': '6c+',
    '9-': '7a', '9': '7a+', '9+': '7b',
    '10-': '7b+', '10': '7c'
}

integer_grades_df['Standard_Grade'] = integer_grades_df['Grade_Str'].str.strip().replace(uiaa_to_french)
integer_grades_df = integer_grades_df.dropna(subset=['Standard_Grade'])


def standardize_complex_french_grade(grade_str_cleaned):
    grade_str = str(grade_str_cleaned).lower()

    match = re.search(r'(fr:|{fr})?(\d[abc]?[-+]?)(\/(\d[abc]?[-+]))?', grade_str)

    if match:
        grade = match.group(4) if match.group(4) else match.group(2)

        grade = grade.replace('fr:', '').replace('{fr}', '')

        if re.match(r'^[1-3][a-c]', grade) or re.match(r'^[1-3][+-]?$', grade):
            return None

        return grade

    return None


free_climbing_df_complex['Standard_Grade'] = free_climbing_df_complex['Grade_Str_Cleaned'].apply(
    standardize_complex_french_grade)

free_climbing_df_complex_standardized = free_climbing_df_complex.dropna(subset=['Standard_Grade'])

free_climbing_df_final = pd.concat([
    free_climbing_df_complex_standardized,
    integer_grades_df
])

free_climbing_df_final = free_climbing_df_final.drop(columns=['Grade_Str', 'Grade_Str_Cleaned'], errors='ignore')

classified_indices = pd.Index([])
for df_category in [mixed_df, ice_df, aid_df, bouldering_df, alpine_df, free_climbing_df_final]:
    classified_indices = classified_indices.union(df_category.index)

unclassified_df = original_df.drop(classified_indices)
unclassified_df['Standard_Grade'] = 'UNCLASSIFIED'
unclassified_df = unclassified_df.drop(columns=['Grade_Str_Cleaned'], errors='ignore')

print(f"\n--- Final Standardized FREE CLIMBING Routes ({len(free_climbing_df_final)} rows) ---")
print(free_climbing_df_final[['Route Name', 'Grade', 'Standard_Grade']].head())

print(f"\n--- TRULY MISCELLANEOUS/UNCLASSIFIED Grades ({len(unclassified_df)} rows) ---")
print(unclassified_df['Grade_Str'].value_counts())

output_path = 'Climbing_Grade_Classification.xlsx'

sheets = {
    '01_Free_Climbing_FR_Standard': free_climbing_df_final,
    '02_Bouldering_Font': bouldering_df.drop(columns=['Grade_Str_Cleaned']),
    '03_Alpine_Combined': alpine_df.drop(columns=['Grade_Str_Cleaned']),
    '04_Aid_Climbing': aid_df.drop(columns=['Grade_Str_Cleaned']),
    '05_Mixed_Climbing': mixed_df.drop(columns=['Grade_Str_Cleaned']),
    '06_Ice_Climbing': ice_df.drop(columns=['Grade_Str_Cleaned']),
    '07_Unclassified_Other': unclassified_df.drop(columns=['Grade_Str_Cleaned'], errors='ignore')
}

try:
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        for sheet_name, df_to_write in sheets.items():
            df_to_write.to_excel(writer, sheet_name=sheet_name, index=False)

    print(f"\nSuccessfully exported all classified data to {output_path}")

except Exception as e:
    print(
        f"\nAn error occurred during Excel export. Ensure you have the necessary engine installed (e.g., run: pip install openpyxl): {e}")
