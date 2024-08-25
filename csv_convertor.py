import pandas as pd
from time import strptime
import datetime

df = pd.read_table("nps.csv", delimiter =",")

for index, row in df.iterrows():
    if row['date'] != "NAN":
        date = row['date']
        date_list = date.split(" ")
        year = int(date_list[2])
        day = int(date_list[1])
        month = strptime(date_list[0],'%b').tm_mon
        datetime_obj = datetime.datetime(year, month, day)
        datetime_obj = int(datetime_obj.strftime('%Y%m%d'))
        df.iloc[index]['date'] = datetime_obj
    else:
        df.iloc[index]['date'] = 0

print(df)