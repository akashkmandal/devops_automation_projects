#!/usr/bin/python3
import requests

url = "https://archives.nseindia.com/content/indices/ind_nifty200list.csv"
response = requests.get(url)

with open("ind_nifty200list.csv", "wb") as f:
    f.write(response.content)

import pandas as pd

df = pd.read_csv("ind_nifty200list.csv")
df = df[["Symbol"]]  # select only the Symbol column
df.to_csv("symbols.csv", index=False)  # save the modified DataFrame as CSV

df = pd.read_csv("symbols.csv")

symbols = df["Symbol"].tolist()  # create a list from the "Symbol" column

if symbols[0] == "Symbol":  # check if the first element is named "Symbol"
    symbols = symbols[1:]

import yfinance as yf

# read symbols from CSV and create list
import pandas as pd
df = pd.read_csv("symbols.csv")
symbols = df["Symbol"].tolist()

# add .NS extension to symbols
symbols_ns = [s + ".NS" for s in symbols]

# download data for each symbol
for symbol in symbols_ns:
    data = yf.download(symbol, period="max")
    symbol_without_ns = symbol.replace(".NS", "")
    data.to_csv(f"{symbol_without_ns}.csv")

