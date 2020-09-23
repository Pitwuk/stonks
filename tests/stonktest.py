from alpha_vantage.timeseries import TimeSeries
import pandas as pd

key = 'P6O4FHCBVPESJ74D'
ts = TimeSeries(key)
nvda, meta = ts.get_daily(symbol='NVDA')

date = '2020-02-11'
day_stats = nvda[date]
print(day_stats)
print('Change: ' +
      str(float(day_stats['4. close']) - float(day_stats['1. open'])))
