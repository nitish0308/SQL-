import pandas as pd
import sqlite3

# Create a database connection
conn = sqlite3.connect(':memory:')

#Load your CSV(s) into pandas

import glob
csv_files = glob.glob('bike_data/*.csv')
print(csv_files)

# Loop through the files and load each into pandas
dataframes = {}

for file in csv_files:
    table_name = file.split('/')[-1].replace('.csv', '')  # gets just the filename without path/extension
    dataframes[table_name] = pd.read_csv(file)

#Push each DataFrame into your SQLite database as a table

for table_name, df in dataframes.items():
    df.to_sql(table_name, conn, index=False, if_exists='replace')
    
#Check what tables you now have

tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table'", conn)
print(tables)

import os
table_name = os.path.splitext(os.path.basename(file))[0]


