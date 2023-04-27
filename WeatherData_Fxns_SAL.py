import requests
import pandas as pd
import numpy as np
import math

from matplotlib import pyplot as plt, dates as mdates
import datetime as datetime


def read_data_from_wu(station, start_date, end_date):
    date_range = pd.date_range(start=start_date, end=end_date)
    weatherdata = pd.DataFrame()
    try:
        for dates in date_range:
            #print(str(dates.date()))
            url = 'https://www.wunderground.com/dashboard/pws/'+station + \
                '/table/'+str(dates.date())+'/'+str(dates.date())+'/daily'
            rweather = requests.get(url)
            html = rweather.content
            htmldf = pd.read_html(html)
            wdata = htmldf[-1]
            wdata['Date'] = dates.date()
            weatherdata = weatherdata.append(wdata)
    except:
        print('something went wrong on ' + str(dates.date()))
    weatherdata.dropna(thresh=5)
    weatherdata.to_csv(station+'_wunderground_'+start_date +
                       '_'+str(dates.date())+'.csv', index=False)

    return weatherdata


def get_temp(data):
    x = list(data['Date'])
    for i in range(len(x)):
        x[i] = datetime.datetime.fromisoformat(x[i])
    # x[:] = datetime.fromisoformat(x[:])
    T = data['Temperature']
    # T = conv_temp(list(data['Temperature']))
    x = np.array(x)
    T = np.array(T)

    return x, T
