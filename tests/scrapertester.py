import requests
import operator
import csv
from datetime import datetime
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import importlib.util
spec = importlib.util.spec_from_file_location(
    "Scraper", ".\Scraper.py")
Scraper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(Scraper)

# Sites:
# 'tr': Tech Radar
# 'th': Tom's Hardware
# 'pcg': PC Gamer
# 'aat': Aand Tech
# 'ee': EEJournal
# 'tnp': The Next Platform
# 'fb': Forbes //TODO 5891 / 296 pages
# 'pcw': PC World //TODO
# 'vg': The Verge //TODO
# 'mf': Motley Fool //TODO

# sort csv by date and time
def sortFile(filename):
    try:
        file = open(filename, 'r')
        data = csv.reader(file, delimiter=',')
        sortedData = sorted(data, key=lambda row: (
            datetime.strptime(row[0]+':'+str(row[1]), '%m-%d-%Y:%H').timestamp()))
        file.close()
        file = open(filename, 'w+', newline='')
        write = csv.writer(file)
        write.writerows(sortedData)
        file.close()
        print(filename+' Sorted')
    except Exception as e:
        print(e)

# get most recent link from site in csv
def getLastLink(site, filename):
    sortFile(filename)
    # get links in file
    lastLink = 'No Site Data'
    try:
        links = pd.read_csv(filename).to_numpy()
        for row in links[::-1]:
            if row[2] == site:
                lastLink = row[3]
                break
    except Exception as e:
        print(e)
        links = []
    print('Last Link: ' + lastLink)
    return lastLink

# write all new articles to csv
def writeUntilMatch(site, term, filename):
    art1 = Scraper.Scraper(site, term, page_num=1)

    # get last link
    lastLink = getLastLink(site, filename)
    # append history to file
    history = art1.getUntilMatch(lastLink)

    writeData(filename, history)

    sortFile(filename)

# write total history to csv
def writeHistory(site, term, filename, reverse=False):
    art1 = Scraper.Scraper(site, term, page_num=1)

    if reverse:
        history = art1.getSiteHistoryReverse()
    else:
        history = art1.getSiteHistory()

    writeData(filename, history)

    sortFile(filename)


# write page to csv
def writePage(site, term, filename, pageNum):
    art1 = Scraper.Scraper(site, term, page_num=pageNum)

    page = art1.getPageData()

    writeData(filename, page)

    sortFile(filename)

# append given data to csv
def writeData(filename, data):
    # get links in file
    try:
        links = pd.read_csv(filename).to_numpy()[:, 3].tolist()
    except:
        links = []

    file = open(filename, 'a')
    for art in data:
        if art['link'] not in links and art['date'] != '00-00-0000' and len(art['text']) > 100:
            links.append(art['link'])
            file.write('"'+art['date']+'","'+str(art['time'])+'","' +
                       art['site']+'","'+art['link']+'","'+art['text']+'"\n')
    file.close()


# writePage('th', 'nvidia', 'NVDAhistory.csv', 2)
# writeHistory('th', 'nvidia', 'NVDAhistory.csv', reverse=True)
writeUntilMatch('fb', 'nvidia', 'NVDAhistory.csv')
