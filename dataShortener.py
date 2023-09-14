import csv
from datetime import datetime, timedelta

# Input and output file paths
input_csv_file = 'DATq1 - sheet3.csv'
output_csv_file = 'output.csv'

# Define the time interval between rows to keep (in minutes)
interval_minutes = 10

# Dictionary to store rows per day
rows_per_day = {}

# Open the input CSV file for reading
with open(input_csv_file, 'r') as infile:
    reader = csv.reader(infile)

    # Skip the header row if it exists
    header = next(reader, None)

    for row in reader:
        # Assuming the timestamp is in the 12th column (index 11)
        timestamp_str = row[11]

        # Convert the timestamp to a datetime object
        timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')

        # Extract the date from the timestamp
        date = timestamp.date()

        # If the date is not in the dictionary, create a new list for it
        if date not in rows_per_day:
            rows_per_day[date] = []

        # Append the row to the list for that date
        rows_per_day[date].append(row)

# Open the output CSV file for writing
with open(output_csv_file, 'w', newline='') as outfile:
    writer = csv.writer(outfile)

    # Write the header row to the output file
    writer.writerow(header)

    # Write selected rows to the output file (one every interval_minutes)
    for date in rows_per_day:
        rows = rows_per_day[date]
        num_rows = len(rows)
        for i in range(0, num_rows, interval_minutes):
            writer.writerow(rows[i])

print(f"Selected and saved rows for {len(rows_per_day)} days.")
 