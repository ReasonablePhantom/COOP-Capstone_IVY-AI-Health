import zipfile
import xml.etree.ElementTree as ET
import pandas as pd
from datetime import datetime, timedelta

def parse_xlsx_to_df(path):
    with zipfile.ZipFile(path) as z:
        # 1. sharedStrings
        shared_strings = []
        if 'xl/sharedStrings.xml' in z.namelist():
            tree = ET.fromstring(z.read('xl/sharedStrings.xml'))
            for si in tree.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}si'):
                text = ''.join([t.text for t in si.iter('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t') if t.text])
                shared_strings.append(text)
                
        # 2. worksheet
        stree = ET.fromstring(z.read('xl/worksheets/sheet1.xml'))
        rows = stree.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheetData/{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row')
        
        all_data = []
        for r in rows:
            # map by column letter or order
            # To handle sparse cells correctly, read cell reference 'r' (e.g. A1, B1)
            row_dict = {}
            for c in r.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
                ref = c.attrib.get('r', '')
                col = ''.join([ch for ch in ref if ch.isalpha()])
                t = c.attrib.get('t')
                v = c.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
                val = v.text if v is not None else ''
                if t == 's' and val.isdigit() and int(val) < len(shared_strings):
                    val = shared_strings[int(val)]
                row_dict[col] = val
            all_data.append(row_dict)
            
    header_row = all_data[0]
    # sort cols
    cols = sorted(header_row.keys(), key=lambda x: (len(x), x))
    header = [header_row[c] for c in cols]
    
    rows_data = []
    for r in all_data[1:]:
        row = [r.get(c, '') for c in cols]
        rows_data.append(row)
        
    df = pd.DataFrame(rows_data, columns=header)
    return df

df_preg = parse_xlsx_to_df('Teammate_Data/ivy_pregnancy_tracker_review.xlsx')
df_coach = parse_xlsx_to_df('Teammate_Data/ivy_wellness_coach_reviews.xlsx')

print(f"Teammate Pregnancy Tracker rows: {len(df_preg)}")
print(f"Teammate Wellness Coach rows: {len(df_coach)}")

# Save as CSV for fast inspection
df_preg.to_csv("Teammate_Data/teammate_pregnancy_reviews.csv", index=False)
df_coach.to_csv("Teammate_Data/teammate_coach_reviews.csv", index=False)
print("Saved both to Teammate_Data/*.csv successfully!")
