import pandas as pd
from time import strptime
import datetime

df = pd.read_table("trial.csv", delimiter =",")

for index, row in df.iterrows():
    if row['date'] != "NAN":
        # Create date integer
        date = row['date']
        date_list = date.split(" ")
        year = int(date_list[2])
        day = int(date_list[1])
        month = strptime(date_list[0],'%b').tm_mon
        datetime_obj = datetime.datetime(year, month, day)
        datetime_obj = int(datetime_obj.strftime('%Y%m%d'))
        # Set value of date
        df.at[index, 'date'] = datetime_obj
    else:
        # Set null value to 0
        df.at[index,'date'] = 0

df.to_csv("nps_list.csv")