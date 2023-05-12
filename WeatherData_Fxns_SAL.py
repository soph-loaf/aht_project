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


#convective heat transfer
L = 80 
rho = 1.22
mu = 17.93*10**-6
k = .02557  ##assuming constant

Re_x = lambda u: rho * u * L / mu
Pr = .71

#solar radiation
alpha_qs = 200.0
sigma = 5.67*10**-8
epsilon = .85
T_sky = 280
T_g_ref = 300 ##place holder

# evaporative heat transfer
# evap_dict = {'March':1.19E-08, 'April':2.50E-08, 'May':2.65E-08, 'June':1.98E-08, 'July':1.53E-08, 'August':1.18E-08, 'September':2.99E-08}
#define evaporation constant d based on monthly precipitation data
# evap_dict = {3 : 1.19E-08, 4 : 2.50E-08, 5 : 2.65E-08, 6 : 1.98E-08, 7 : 1.53E-08, 8 : 1.18E-08, 9 : 2.99E-08}
evap_list = [1.19E-08, 2.50E-08, 2.65E-08, 1.98E-08, 1.53E-08, 1.18E-08, 2.99E-08]

# q = 2256 kJ/kg * 1000 kg/m^3 * 1 m * 1 m * d
q_evap = lambda d: 2256.0*10**6*d


def q_conv(T_a, u, T_g=300.0):
    """q_conv = lambda T_g, T_a, h: h*(T_g - T_a)"""
    Nu_turb = .037*Re_x(u)**.8*Pr**(1/3)
    h_turb = Nu_turb * k / L
    q_conv = h_turb*(T_g - T_a)
    return q_conv

def ground_temp(T_a, u):
    """predicting ground temperature for non-vegetated areas"""
    # Nu = .0296*Re**.8*Pr**.33
    # Nu_turb = .037*Re_x(u_ref)**.8*Pr**(1/3)
    # Nu_lam = .664*Re_x(u_ref)**.5*Pr**(1/3)
    Nu_turb = .037*Re_x(u)**.8*Pr**(1/3)

    # Re_ref = 600000
    # u_ref = 5.0
    h_turb = Nu_turb * k / L
    T_g = (alpha_qs + h_turb*T_a + 4.0*sigma*epsilon*T_sky**4)/(h_turb + 4.0*sigma*epsilon*T_sky**3)
    return T_g

def ground_temp_ctrl(T_a, u, d):
    """predicting ground temperature for Central Park (includes evaporation)"""
    Nu_turb = .037*Re_x(u)**.8*Pr**(1/3)
    h_turb = Nu_turb * k / L
    T_g_ctrl = (alpha_qs + h_turb*T_a + 4.0*sigma*epsilon*T_sky**4 - q_evap(d))/(h_turb + 4.0*sigma*epsilon*T_sky**3)
    return T_g_ctrl

def predict_air_temp(T_g, q_conv, h):
    T_a = T_g - q_conv/h
    return T_a

def ground_temp_solar_var(T_a, u, n, alpha=.6):
    """predicting ground temperature using variable solar radiation"""
    Nu_turb = .037*Re_x(u)**.8*Pr**(1/3)
    h_turb = Nu_turb * k / L
    delta_s = 23.45*np.sin((360/365)*(n-81)*np.pi/180)
    # print(delta_s)
    alpha_qs_var = 333.333*alpha*np.sin((90 - 40.7 + delta_s)*np.pi/180)
    # print(alpha_qs_var)
    T_g = (alpha_qs_var + h_turb*T_a + 4.0*sigma*epsilon*T_sky**4)/(h_turb + 4.0*sigma*epsilon*T_sky**3)
    # print(T_g)
    # q_solar_var = alpha_qs_var - 4.0*sigma*epsilon*T_sky**3*(T_g_ref - T_sky)
    return T_g

def ground_temp_ctrl_var(T_a, u, d, n, alpha=.6):
    """predicting ground temperature for Central Park (includes evaporation & variable solar radiation)"""
    Nu_turb = .037*Re_x(u)**.8*Pr**(1/3)
    h_turb = Nu_turb * k / L
    delta_s = 23.45*np.sin((360/365)*(n-81)*np.pi/180)
    alpha_qs_var = 333.333*alpha*np.sin((90 - 40.7 + delta_s)*np.pi/180)
    T_g_ctrl = (alpha_qs_var + h_turb*T_a + 4.0*sigma*epsilon*T_sky**4 - q_evap(d))/(h_turb + 4.0*sigma*epsilon*T_sky**3)
    return T_g_ctrl
    


