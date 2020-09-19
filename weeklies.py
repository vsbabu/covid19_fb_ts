#!/usr/bin/env python3
import pandas as pd
import numpy as np
from fbprophet import Prophet

import sys
import argparse

import logging
logger = logging.getLogger("weeklies")

import datetime
today = datetime.date.today()

argparser = argparse.ArgumentParser(description="Reads dt,value without header from stdin and prints a weekly folded html with anomalies", add_help=True)
argparser.add_argument("--start_week_date", "-s", help="Start date; must be a Monday")
argparser.add_argument("--how_many_weeks", "-k", help="For how many weeks?")
argparser.add_argument("--time_format", "-t", help="Strftime pattern to parse (%y%m%d)")
argparser.add_argument("--output", "-o", help="Output HTML file")
argparser.add_argument("--group", "-g", help="Output HTML file group")
argparser.add_argument("--positive_color", "-p", help="Color for anomaly above band (lightgreen)")
argparser.add_argument("--negative_color", "-n", help="Color for anomaly below band (orange)")
argparser.add_argument("--future_color", "-f", help="Color for future predictions (silver)")
argparser.add_argument("--marker_yaml", "-m", help="Additional marker lines to be drawn")

args = argparser.parse_args()

if args.how_many_weeks:
    args.how_many_weeks = int(args.how_many_weeks)
else:
    args.how_many_weeks = 8
if not args.start_week_date:
    args.start_week_date = today - datetime.timedelta(days=today.weekday(), weeks = args.how_many_weeks)

if today.weekday() == 0: #if monday, let us ensure we predict rest of the week too
    args.start_week_date = today - datetime.timedelta(days=today.weekday(), weeks = (args.how_many_weeks-1))


if not args.time_format:
    args.time_format = "%y%m%d"

if not args.positive_color:
    args.positive_color = "lightgreen"
if not args.negative_color:
    args.negative_color = "orange"
if not args.future_color:
    args.future_color = "silver"

dfi = pd.read_csv(sys.stdin, sep=",", header=None, names=["ds", "y"])

dates = pd.date_range(args.start_week_date, periods=((args.how_many_weeks+0) * 7))
remaining_days_in_week = dates[-1].dayofweek - today.weekday()

todayf = today.strftime(args.time_format)
if todayf not in dfi.ds.values:
    #if today's data is not there, let us predict it 
    remaining_days_in_week = remaining_days_in_week + 1

dfi["ds"] = pd.to_datetime(dfi.ds, format=args.time_format)
dfi = dfi.set_index("ds")

dfi = dfi.resample("D").asfreq().fillna(0)

dfi.v = dfi.y.astype(int)

dfi.reset_index(inplace=True)
dfi.columns = ["ds", "y"]


def fit_predict_model(dataframe, interval_width=0.99, changepoint_range=0.8,
        future_periods=0):
    # your data MAY HAVE weekly/monthly seasonality and holidays. Change accordingly
    m = Prophet(
        daily_seasonality=False,
        yearly_seasonality=False,
        weekly_seasonality=False,
        seasonality_mode="additive",
        interval_width=interval_width,
        changepoint_range=changepoint_range,
    )
    m = m.fit(dataframe)
    forecast = m.predict(dataframe)
    forecast["fact"] = dataframe["y"].reset_index(drop=True)
    fdataframe = m.make_future_dataframe(periods=future_periods)
    forecast_f = m.predict(fdataframe)
    forecast_f["fact"] = forecast_f["yhat"].reset_index(drop=True)
    forecast_f['fact'] =  forecast_f.fact.astype(int)
    return (forecast, forecast_f, m)


def detect_anomalies(forecast):
    forecasted = forecast[
        ["ds", "trend", "yhat", "yhat_lower", "yhat_upper", "fact"]
    ].copy()

    #add an anomaly value of 0 for everything
    #make it 1 or -1 for those facts above or below yhat bands
    forecasted["anomaly"] = 0
    forecasted.loc[forecasted["fact"] > forecasted["yhat_upper"], "anomaly"] = 1
    forecasted.loc[forecasted["fact"] < forecasted["yhat_lower"], "anomaly"] = -1

    # anomaly importances
    forecasted["importance"] = 0
    forecasted.loc[forecasted["anomaly"] == 1, "importance"] = (
        forecasted["fact"] - forecasted["yhat_upper"]
    ) / forecast["fact"]
    forecasted.loc[forecasted["anomaly"] == -1, "importance"] = (
        forecasted["yhat_lower"] - forecasted["fact"]
    ) / forecast["fact"]

    return forecasted


def highlight_anomaly_wk(d):
    p_anom = f"background-color: {args.positive_color}"
    n_anom = f"background-color: {args.negative_color}"
    f_anom = f"background-color: {args.future_color}"
    regular = ""
    df1 = pd.DataFrame(regular, index=d.index, columns=d.columns)
    for wd in "mon tue wed thu fri sat sun".split():
        a = "a_" + wd
        p_mask = d[a] > 0
        n_mask = d[a] == -1
        f_mask = d[a] < -1
        df1.loc[p_mask, wd] = p_anom
        df1.loc[n_mask, wd] = n_anom
        df1.loc[f_mask, wd] = f_anom
    return df1



(pred, fut, m) = fit_predict_model(dfi, 0.99, 0.8, future_periods = remaining_days_in_week)
pred = detect_anomalies(pred)
fut['anomaly'] = -2
dfi.set_index("ds", inplace=True)
dfd = dfi.loc[dates]

edf = pred[["ds", "fact", "anomaly"]].copy()
edfut = fut[["ds", "fact", "anomaly"]].copy()
edf = edf.combine_first(edfut)
edf.set_index("ds", inplace=True)

edf=edf.reindex(dates) 
edf['fact'] =  edf.fact.astype(int)

# Now, fold the df by weeks. fact goes to a day value and anomaly goes to a_day value
wkv = edf[["fact", "anomaly"]].copy().values.reshape(args.how_many_weeks+0, 7 * 2)
efw = edf[edf.index.weekday_name == "Monday"]
efw = pd.DataFrame(
    wkv,
    index=efw.index,
    columns=[
        "mon",
        "a_mon",
        "tue",
        "a_tue",
        "wed",
        "a_wed",
        "thu",
        "a_thu",
        "fri",
        "a_fri",
        "sat",
        "a_sat",
        "sun",
        "a_sun",
    ],
)
#float64 prints numbers > 1million as scientific in HTML render. So make it int32.
efw = efw.astype({col: 'int32' for col in efw.select_dtypes('float64').columns})
efw.index.name = "week"
efw.sort_index(ascending=False, inplace=True)


html = efw.style.apply(highlight_anomaly_wk, axis=None).hide_columns(
    ["a_mon", "a_tue", "a_wed", "a_thu", "a_fri", "a_sat", "a_sun"]
)

if args.output:
    with open(args.output, "w") as f:
        f.write(html.render())
else:
    print(html.render())

future_days = int((7*args.how_many_weeks/2) + remaining_days_in_week)
fdataframe = m.make_future_dataframe(periods=future_days)
forecast_f = m.predict(fdataframe)
fig = m.plot(forecast_f)
ax = fig.get_axes()[0]
if args.marker_yaml:
    import yaml
    try:
        with open(args.marker_yaml, "r") as ymlfile:
            ymg = yaml.load(ymlfile, yaml.SafeLoader)
        for i, marker in enumerate(ymg["markers"], 1):
            ax.axvline(x=marker['val'], color=marker['color'], label=marker['label'], linestyle=marker['mark'], linewidth=1)
            ax.text(marker['val'],0,marker['label'],rotation=90)
    except Exception as e:
        logger.error("Marker config failed " + str(e))
fig.savefig(args.group + "_pred_" + args.output + ".png")
