from flask import Blueprint, render_template, request
from dataclasses import dataclass
from scipy.optimize import curve_fit
from datetime import datetime
import numpy as np
import json
import calendar

data = Blueprint('data', __name__)

@data.route('/compute/', methods=['GET', 'POST'])
def processData():
    return makeComputations(request.form)

@data.route('/fetch/<tt>')
def getData(tt):
    return load(tt)


import os
import pandas as pd
import datetime

base_folder = os.path.join(os.path.dirname(__name__), '..', 'COVID-19', 'csse_covid_19_data', 'csse_covid_19_time_series')

def load(data):
    global base_folder

    if data == 'countries':
        recovered_data = pd.read_csv(os.path.join(base_folder, 'time_series_covid19_recovered_global.csv'), sep=',')
        countries = recovered_data['Country/Region'].drop_duplicates()
        return countries.to_json()
    else:
        return json.dumps({})


@dataclass
class Values:
    def __init__(self, value: pd.DataFrame):
        self.value = value
        self.value_ma = self.value.rolling(window=7).mean()

    def get(self):
        return {
            'Raw': self.value.fillna(0).to_dict(),
            'Moving Average 7 days': self.value_ma.fillna(0).to_dict()
        }

@dataclass
class Measurement:
    def __init__(self, measurement: pd.DataFrame):
        self.measurement = Values(measurement)
        self.measurement_diff = Values(measurement.diff())

    def get(self):
        return {
            'Cumulative': self.measurement.get(),
            'Daily new': self.measurement_diff.get()
        }

@dataclass
class COVID19:
    def __init__(self, confirmed: pd.DataFrame, deaths: pd.DataFrame, recovered: pd.DataFrame):
        self.confirmed = Measurement(confirmed)
        self.deaths = Measurement(deaths)
        self.recovered = Measurement(recovered)
        self.predictEnd = predictEnd({
            'confirmed': self.confirmed,
            'deaths': self.deaths,
            'recovered': self.recovered
        })

    def to_json(self):
        return json.dumps({
            'confirmed': self.confirmed.get(),
            'deaths': self.deaths.get(),
            'recovered': self.recovered.get(),
            'lockdown': self.predictEnd.to_dict()
        })

def moving_average(df):
    return df.rolling(window=7).mean()

def makeComputations(countries):
    global base_folder

    confirmed = pd.read_csv(os.path.join(base_folder, 'time_series_covid19_confirmed_global.csv'), sep=',')
    deaths = pd.read_csv(os.path.join(base_folder, 'time_series_covid19_deaths_global.csv'), sep=',')
    recovered = pd.read_csv(os.path.join(base_folder, 'time_series_covid19_recovered_global.csv'), sep=',')

    get_total_per_country = lambda df: df.sum(axis=0) if not df.isnull().values.any() else df[df.isna().any(axis=1)]
    # clean_date = lambda df: df.set_index(pd.Index([datetime.date(2000 + int(dd.split('/')[2]), int(dd.split('/')[0]), int(dd.split('/')[1])) for dd in list(df.index.values)]))
    clean_date = lambda df: df.set_index(pd.Index([calendar.timegm(datetime.date(2000 + int(dd.split('/')[2]), int(dd.split('/')[0]), int(dd.split('/')[1])).timetuple()) for dd in list(df.index.values)]))

    countries = [k for k, _ in countries.items()]

    objs = []
    for obj in [confirmed, deaths, recovered]:
        dfs = []
        for c in countries:
            total = get_total_per_country(obj[obj['Country/Region'] == c])
            if isinstance(total, pd.core.frame.Series):
                total = pd.DataFrame(total)
                total = total.transpose()
            total = total.drop(['Province/State', 'Country/Region', 'Lat', 'Long'], axis=1)
            total = total.set_index(pd.Index(['Total ' + c]))
            total = total.transpose()
            total = clean_date(total)
            dfs.append(total)
        objs.append(pd.concat(dfs, axis=1, sort=False))

    selected = COVID19(objs[0], objs[1], objs[2])

    return selected.to_json()


def predictEnd(selection):
    df_confirmed_cumu = selection['confirmed'].measurement.value
    df_confirmed_diff = selection['confirmed'].measurement.value_ma

    predictions = pd.DataFrame()

    for country in df_confirmed_cumu:
        x, y = df_confirmed_cumu[country].index.values, df_confirmed_cumu[country].values
        x, y = rangeSelect(x, y)
        # print(x, y)

    for country in df_confirmed_cumu:
        x, y = df_confirmed_diff[country].index.values, df_confirmed_diff[country].values
        x, y = rangeSelect(x, y)

        # start gaussian at 0
        xdata = range(len(x))

        gauss = gaussRegression(xdata, y)

        # predictions[country] = gauss
        # predictions.set_index(pd.index([]))

    return pd.DataFrame()



def rangeSelect(x, y, thresh=5):
    start = np.where(y > 5)[0][0]
    x, y = x[start:], y[start:]
    return x, y


def gaussRegression(x ,y, forward=7 * 48):
    gauss = lambda x, a, x0, sigma: a*np.exp(-(x-x0)**2/(2*sigma**2))

    popt, _ = curve_fit(gauss, x, y)

    return gauss(range(len(x) + forward), *popt)

def logisticRegression(x, y, forward=7 * 48):
    sigmoid = lambda x, A, B, k, x0: A / (1 + np.exp(-k*(x-x0)))+B

    popt, _ = curve_fit(sigmoid, x, y)

    return sigmoid(range(len(x) + forward), *popt)
