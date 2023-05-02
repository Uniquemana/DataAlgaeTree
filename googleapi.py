# credentials = ServiceAccountCredentials.from_json_keyfile_name("dataalgaetreegsheets-388ac829236c.json", scope)

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# Connect to Google Sheets
scope = ['https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive"]

credentials = ServiceAccountCredentials.from_json_keyfile_name("dataalgaetreegsheets-388ac829236c.json", scope)
client = gspread.authorize(credentials)

if client is not None:
    print("Success")
else:
    print("Nope")

sheet = client.open("DATq1").sheet1

if sheet is not None:
    print("sheet opened")
else:
    print("cant open sheet")

# Define the variable you want to write to the sheet
data_to_write = "Hello, World!"

try:
    # Update a specific cell (in this case, A1) with the variable 'data_to_write'
    sheet.update_cell(1, 1, data_to_write)
    print("Data successfully written to the sheet.")
except Exception as e:
    print("Error occurred while writing data to the sheet:", e)

# sheet.share('abolinskristians@gmail.com', perm_type='user', role='writer')
# if sheet.share is not None:
#     print("perm given")
# else:
#     print("cant give perm")