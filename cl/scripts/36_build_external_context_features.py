#!/usr/bin/env python3
from __future__ import annotations
import json, math, sys, urllib.parse, urllib.request
from datetime import date, datetime, timedelta
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.cl_common import DATA_DIR, FEATURE_DIR, ensure_dirs

# External public context data: Korean public holidays + Seoul weather/daylight proxies.
# Weather source: Open-Meteo Archive API (free public historical weather).
SEOUL_LAT, SEOUL_LON = 37.5665, 126.9780
KOREA_HOLIDAYS_2024 = {
    '2024-01-01':'new_year', '2024-02-09':'seollal', '2024-02-10':'seollal', '2024-02-11':'seollal', '2024-02-12':'seollal_sub',
    '2024-03-01':'independence', '2024-04-10':'election', '2024-05-05':'children', '2024-05-06':'children_sub', '2024-05-15':'buddha',
    '2024-06-06':'memorial', '2024-08-15':'liberation', '2024-09-16':'chuseok', '2024-09-17':'chuseok', '2024-09-18':'chuseok',
    '2024-10-03':'foundation', '2024-10-09':'hangeul', '2024-12-25':'christmas'
}


def daylight_hours(day: date, lat: float = SEOUL_LAT) -> tuple[float, float, float]:
    # NOAA-style approximation: enough for date-level circadian context.
    n = day.timetuple().tm_yday
    lat_rad = math.radians(lat)
    decl = math.radians(23.44) * math.sin(2 * math.pi * (284 + n) / 365.0)
    cos_ha = -math.tan(lat_rad) * math.tan(decl)
    cos_ha = min(1.0, max(-1.0, cos_ha))
    ha = math.acos(cos_ha)
    day_len = 24.0 * ha / math.pi
    sunrise = 12.0 - day_len / 2.0
    sunset = 12.0 + day_len / 2.0
    return day_len, sunrise, sunset


def fetch_weather(start: str, end: str) -> pd.DataFrame:
    params = {
        'latitude': SEOUL_LAT, 'longitude': SEOUL_LON,
        'start_date': start, 'end_date': end,
        'daily': ','.join([
            'temperature_2m_mean','temperature_2m_max','temperature_2m_min',
            'precipitation_sum','rain_sum','snowfall_sum',
            'wind_speed_10m_max','shortwave_radiation_sum'
        ]),
        'timezone': 'Asia/Seoul'
    }
    url = 'https://archive-api.open-meteo.com/v1/archive?' + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            obj = json.load(r)
        daily = obj.get('daily', {})
        if not daily or 'time' not in daily:
            raise RuntimeError(f'bad open-meteo response keys={list(obj)}')
        df = pd.DataFrame(daily).rename(columns={'time':'lifelog_date'})
        for c in df.columns:
            if c != 'lifelog_date':
                df['ext_weather_' + c] = pd.to_numeric(df[c], errors='coerce')
                if c.startswith(('temperature','precipitation','rain','snowfall','wind','shortwave')):
                    del df[c]
        return df
    except Exception as e:
        print(f'[WARN] weather fetch failed: {e}. Continuing with non-weather context only.', file=sys.stderr)
        return pd.DataFrame({'lifelog_date': pd.date_range(start, end).strftime('%Y-%m-%d')})


def main():
    ensure_dirs()
    train = pd.read_csv(DATA_DIR/'ch2026_metrics_train.csv')
    test = pd.read_csv(DATA_DIR/'ch2026_submission_sample.csv')
    keys = pd.concat([train[['subject_id','lifelog_date']], test[['subject_id','lifelog_date']]], ignore_index=True).drop_duplicates()
    dates = pd.to_datetime(keys['lifelog_date']).dt.date
    start, end = str(min(dates)), str(max(dates))
    weather = fetch_weather(start, end)
    rows=[]
    hol_dates = sorted(datetime.strptime(d, '%Y-%m-%d').date() for d in KOREA_HOLIDAYS_2024)
    for d in sorted(set(dates)):
        ds = d.isoformat()
        dow = d.weekday()
        doy = d.timetuple().tm_yday
        day_len, sunrise, sunset = daylight_hours(d)
        dist = [abs((d-h).days) for h in hol_dates]
        signed = [(d-h).days for h in hol_dates]
        rows.append({
            'lifelog_date': ds,
            'ext_cal_dow': dow,
            'ext_cal_is_weekend': int(dow>=5),
            'ext_cal_month': d.month,
            'ext_cal_dayofyear': doy,
            'ext_cal_dow_sin': math.sin(2*math.pi*dow/7),
            'ext_cal_dow_cos': math.cos(2*math.pi*dow/7),
            'ext_cal_doy_sin': math.sin(2*math.pi*doy/366),
            'ext_cal_doy_cos': math.cos(2*math.pi*doy/366),
            'ext_cal_is_holiday': int(ds in KOREA_HOLIDAYS_2024),
            'ext_cal_is_holiday_eve': int((d + timedelta(days=1)).isoformat() in KOREA_HOLIDAYS_2024),
            'ext_cal_is_after_holiday': int((d - timedelta(days=1)).isoformat() in KOREA_HOLIDAYS_2024),
            'ext_cal_days_to_nearest_holiday': min(dist) if dist else 99,
            'ext_cal_signed_days_from_nearest_holiday': min(signed, key=lambda x: abs(x)) if signed else 99,
            'ext_cal_is_chuseok_window': int(date(2024,9,13) <= d <= date(2024,9,22)),
            'ext_solar_daylight_hours': day_len,
            'ext_solar_sunrise_hour': sunrise,
            'ext_solar_sunset_hour': sunset,
        })
    cal = pd.DataFrame(rows)
    by_date = cal.merge(weather, on='lifelog_date', how='left')
    out = keys.merge(by_date, on='lifelog_date', how='left')
    # Subject-normalized weather/context deviations where meaningful and computable transductively from input-only dates.
    num_cols = [c for c in out.columns if c not in ['subject_id','lifelog_date']]
    for c in list(num_cols):
        vals = pd.to_numeric(out[c], errors='coerce')
        if vals.notna().sum() and vals.nunique(dropna=True)>1:
            mu = out.groupby('subject_id')[c].transform('mean')
            sd = out.groupby('subject_id')[c].transform('std').replace(0, np.nan)
            out[f'{c}__subj_delta'] = vals - mu
            out[f'{c}__subj_z'] = (vals - mu) / sd
    out.to_parquet(FEATURE_DIR/'external_context_features_v1.parquet', index=False)
    out.to_csv(FEATURE_DIR/'external_context_features_v1.csv', index=False)
    print('wrote', FEATURE_DIR/'external_context_features_v1.parquet', out.shape)
    print(out.head().to_string(index=False))

if __name__ == '__main__':
    main()
