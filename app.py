from NextDay import NextDay
from Scraper import Scraper
import tkinter as tk
from tkinter import filedialog, Text
import os
from datetime import datetime, date, timedelta
import time
import csv
import json
import numpy as np
import pandas as pd
import matplotlib
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib import style
from webull import paper_webull  # for paper trading import paper_webull
import asyncio
import threading
from dotenv import load_dotenv
load_dotenv()

# init window
root = tk.Tk()
root.title('Stonks')

# gui vars
isPaused = False  # pauses the whole application
countdownInterval = 30  # seconds between web scrapes
secondsLeft = countdownInterval  # seconds left before next web scrape

# matplotlib vars
style.use("ggplot")
lastGraphSelection = ""
lastTimeSelection = ""

# stock vars
symbols = []  # stock symbols
companyNames = {}  # map symbol to companyMame
positions = []  # list of positions currently held
positionsText = ''  # positions text for positions label
predictions = {}  # map symbols to their predicted change
changes = {}  # map symbols to their actual change
sortedPredictions = []  # stores the symbols in the descending order of predicted change
sortedChange = []  # stores the symbols in the descending order of actual change
status = open("status.csv", "r")  # timestamp of last operation

# dictionary of historical stock data
historicalData = {}

# storage bools
pnlStored = False
stockDataStored = False
marketOpenToday = False

wb = paper_webull()
# webull.get_mfa('plogden2@gmail.com') #this line will send the mfa code
wb.login('plogden2@gmail.com', 'Voodood978', 'MacOS Chrome', '813559')
account = wb.get_account()
print(account)
print('\n')
wb.get_trade_token('102829')


# load checked stocks
with open('watchlist.csv', mode='r')as file:
    watchlistFile = csv.reader(file)
    for lines in watchlistFile:
        symbols.append(lines[0])
        companyNames[lines[0]] = lines[1]

# load historical stock data
for symbol in symbols:
    historicalData[symbol] = pd.read_csv(
        './price_history/'+symbol+'.csv').to_numpy()[-30:, :]

# load pnl data
historicalData['PNL'] = pd.read_csv('pnl.csv').to_numpy()

# start checks


def startChecks():
    global pnlStored, stockDataStored, marketOpenToday
    # get current date
    now = datetime.now()
    currDate = now.strftime("%Y-%m-%d")

    # get last status datetime

    # get last pnl date
    if(historicalData['PNL'][-1, 0] == currDate):
        pnlStored = True

    # determine if market is open today
    marketOpenToday = marketOpenCheck()

    # check if stock data was stored for today
    stockDataStored = True
    for symbol in symbols:
        if(historicalData[symbol][-1, 0] != currDate):
            stockDataStored = False
    print('Stock Data Stored: '+str(stockDataStored))


def marketOpenCheck():
    today = date.today()
    today = str(today.strftime("%m/%d/%Y"))
    yesterday = date.today() - timedelta(days=1)
    yesterday = str(yesterday.strftime('%m/%d/%Y'))

    if NextDay(yesterday).getNext() == today:
        print('Stock Market Open Today')
        return True
    print('Stock Market Closed Today')
    return False

# pauses/resumes app functions


def pauseApp():
    global isPaused
    isPaused = not isPaused
    pauseAppBtn.config(text='Start App' if isPaused else 'Pause App')

    if(not isPaused):
        threading.Thread(target=countdown).start()
        threading.Thread(target=updatePredictions).start()
        threading.Thread(target=updatePositions).start()
        threading.Thread(target=updateChange).start()


# stores stock data for today
def storeStockData():
    now = datetime.now()
    date = now.strftime("%Y-%m-%d")

    for symbol in symbols:
        quote = wb.get_quote(symbol)
        # timestamp of last operation
        file = open('./price_history/'+symbol+'.csv', "a")
        file.write('\n'+date +
                   ','+quote['open']+','+quote['high']+','+quote['low']+','+quote['close']+','+quote['close']+','+quote['volume'])
        file.close()
        historicalData[symbol] = pd.read_csv(
            './price_history/'+symbol+'.csv').to_numpy()[-30:, :]


# updates time
def clock():
    global pnlStored, stockDataStored, marketOpenToday
    while True:
        now = datetime.now()
        timeformat = now.strftime("%Y-%m-%d %H:%M:%S")

        # store timne in status every minute
        if(now.second == 0):
            status = open("status.csv", "w")  # timestamp of last operation
            status.write(timeformat)
            status.close()

        if(not pnlStored and now.hour >= 16):
            try:
                clockLabel.config(text='Storing PnL')
                account = wb.get_account()
                file = open("pnl.csv", "a")  # timestamp of last operation
                file.write('\n'+now.strftime("%Y-%m-%d") +
                           ','+account['totalProfitLoss'])
                file.close()
                historicalData['PNL'] = pd.read_csv('pnl.csv').to_numpy()
                pnlStored = True
            except Exception as e:
                pass

        if(not stockDataStored and marketOpenToday and now.hour >= 16):
            try:
                clockLabel.config(text='Storing Stock Data')
                storeStockData()
                stockDataStored = True
            except Exception as e:
                print(e)

        clockLabel.config(text=timeformat)

        time.sleep(0.1)

# updates scaper countdown


def countdown():
    global secondsLeft
    while not isPaused:
        if(secondsLeft):
            timeformat = 'Time until next scrape: ' + str(secondsLeft)
            countdownLabel.config(text=timeformat)
            secondsLeft -= 1

        elif isPaused:
            countdownLabel.config(text='Time until next scrape: PAUSED')
        else:
            countdownLabel.config(text='Getting Articles')
            # TODO get articles
            secondsLeft = countdownInterval

        time.sleep(1)

# updates watchlist change label data


def updateChange():
    while(not isPaused):
        getChanges()
        sortMap(changes, sortedChange)
        text = 'Changes:'
        for symbol in sortedChange:
            change = changes[symbol]
            text += '\n' + symbol + \
                ': ' + f'{change:.2f}' + '%'
        watchlistChangeLabel.config(text=text)
        time.sleep(0.01)

# gets changes from webull api


def getChanges():
    for symbol in symbols:
        quote = wb.get_quote(symbol)
        changes[symbol] = float(quote['changeRatio'])*100

# updates prediction labels


def updatePredictions():
    while(not isPaused):
        getPredictions()
        sortMap(predictions, sortedPredictions)
        predictionsText = 'Predictions:'
        for symbol in sortedPredictions:
            predictedChange = predictions[symbol]
            predictionsText += '\n' + symbol + \
                ': ' + f'{predictedChange:.2f}' + '%'
        predictionsLabel.config(text=predictionsText)
        time.sleep(1)


# gets predictions from model given symbol
def getPredictions():
    for symbol in symbols:
        predictions[symbol] = (np.random.rand()*10)-5


# sorts sortedSymbold in order of descending predicted change
# param: inMap -- map to be sorted
# param: output -- list of map keys in decending order of corresponding value
def sortMap(inMap, output):
    output.clear()
    for i in sorted((value, key) for (key, value) in inMap.items()):
        output.insert(0, i[1])

# puts the positions into positions list


def getPositions():
    positions.clear()
    pos = wb.get_positions()

    for i in pos:
        positions.append([i['ticker']['symbol'], i['marketValue'],
                          i['unrealizedProfitLoss']])

# formats the text for the positions label


def setPositionsText():
    global positionsText
    positionsText = "Positions:"
    for i in positions:
        positionsText += '\n'+i[0]+' ['+i[1]+']('+i[2]+')'
    positionsLabel.config(text=positionsText)


# updates position labels
def updatePositions():
    global wb
    while(not isPaused):
        try:
            portfolio = wb.get_portfolio()
            account = wb.get_account()
            getPositions()
            setPositionsText()

            # update net liquidation, usable cash, and market values
            usableCash = float(portfolio['usableCash'])
            marketValue = float(portfolio['totalMarketValue'])
            netLiquidation = float(account['netLiquidation'])
            accountBalanceLabel.config(
                text='Net Liquidation: $'+f'{netLiquidation:,}'+"\nUsable Cash: $"+f'{usableCash:,}'+"\nMarket Value: $"+f'{marketValue:,}')

            # update p&l value
            pnlValue = float(portfolio['dayProfitLoss'])
            totalPnlValue = float(account['totalProfitLoss'])
            pnlLabel.config(text="Day P&L: $" +
                            f'{pnlValue:,}'+"\nTotal P&L: $"+f'{totalPnlValue:,}')

            # update change value
            dayChange = (pnlValue/marketValue)*100
            totalChange = (totalPnlValue/netLiquidation)*100
            portfolioChangeLabel.config(text="Day Change: " +
                                        f'{dayChange:2f}'+"%\nTotal Change: "+f'{totalChange:2f}'+'%')
        except Exception as e:
            pass
        finally:
            time.sleep(0.1)


# animate function for matplotlib


def animate(i):
    global lastGraphSelection, lastTimeSelection
    if(graphSelection.get() != lastGraphSelection or timeSelection.get() != lastTimeSelection):
        lastGraphSelection = graphSelection.get()
        lastTimeSelection = timeSelection.get()

        timescale = 30
        if(lastTimeSelection == 'Week'):
            timescale = 7
        elif(lastTimeSelection == 'Day'):
            timescale = 1

        subplot.clear()
        subplot.plot(
            historicalData[graphSelection.get()][-timescale:, 0], historicalData[graphSelection.get()][-timescale:, 1])


# pause app button
pauseAppBtn = tk.Button(
    root, text='Start App' if isPaused else 'Pause App', padx=10, pady=10, command=pauseApp)
pauseAppBtn.grid(row=0, column=0)

# clock
clockLabel = tk.Label(root, text="", font=(
    'Times New Roman', 12), bg='darkblue', fg='white')
clockLabel.grid(row=0, column=6)

# countdown to next article check
countdownLabel = tk.Label(root, text="", font=('Times New Roman', 14))
countdownLabel.grid(row=1, column=6)


# graph of stock performance and predictions
fig = Figure(figsize=(5, 4), dpi=100)
subplot = fig.add_subplot(111)
graph = FigureCanvasTkAgg(fig, master=root)
graph.draw()
graph.get_tk_widget().grid(row=1, column=0, rowspan=5, columnspan=3)

# graph toolbar
toolbarFrame = tk.Frame(root)
toolbarFrame.grid(row=6, column=0, columnspan=2)

toolbar = NavigationToolbar2Tk(graph, toolbarFrame)
toolbar.update()

# graph options dropdown
stockGraphOptions = ['PNL'] + symbols
graphSelection = tk.StringVar(root)
graphSelection.set(stockGraphOptions[0])
graphDropdown = tk.OptionMenu(root, graphSelection, *stockGraphOptions)
graphDropdown.grid(row=6, column=2)

# graph timescale dropdown
timeGraphOptions = ['Month', 'Week', 'Day']
timeSelection = tk.StringVar(root)
timeSelection.set(timeGraphOptions[0])
timeDropdown = tk.OptionMenu(root, timeSelection, *timeGraphOptions)
timeDropdown.grid(row=7, column=2)

# stock prediction leaderboard
predictionsLabel = tk.Label(
    root, text="Predictions:", font=('Times New Roman', 14))
predictionsLabel.grid(row=1, column=4, rowspan=3)

# stock watchlist change leaderboard
watchlistChangeLabel = tk.Label(
    root, text="Changes: XXXX --.--%", font=('Times New Roman', 14))
watchlistChangeLabel.grid(row=1, column=5, rowspan=3)

# stock watchlist change leaderboard
articleCounterLabel = tk.Label(
    root, text="Articles: XXXX Today: -- Total: ----", font=('Times New Roman', 14))
articleCounterLabel.grid(row=4, column=4, rowspan=3, columnspan=2)

# Net Liquidation, usable cash and market value
accountBalanceLabel = tk.Label(
    root, text="", font=('Times New Roman', 14))
accountBalanceLabel.grid(row=2, column=6)

# Profit and Loss value
pnlLabel = tk.Label(
    root, text="P&L: ", font=('Times New Roman', 14))
pnlLabel.grid(row=3, column=6)

# percent change value
portfolioChangeLabel = tk.Label(
    root, text="Change: ", font=('Times New Roman', 14))
portfolioChangeLabel.grid(row=4, column=6)

# Positions
positionsLabel = tk.Label(
    root, text="Positions:", font=('Times New Roman', 14))
positionsLabel.grid(row=5, column=6, rowspan=3)

ani = animation.FuncAnimation(fig, animate, interval=1000)

startChecks()
threading.Thread(target=clock).start()
threading.Thread(target=countdown).start()
threading.Thread(target=updatePredictions).start()
threading.Thread(target=updatePositions).start()
threading.Thread(target=updateChange).start()

root.mainloop()
