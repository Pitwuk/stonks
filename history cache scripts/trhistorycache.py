import requests
from bs4 import BeautifulSoup
import xlsxwriter
import time

from Scraper import Scraper

# This program saves the date, time, and text contents of all news articles with the search result for
# nvidia on tech radar into an xlsx file

start_time = time.time()
schtuff = []

# 0-141
iteration = 0
pages_per = 20
workbook = xlsxwriter.Workbook('nvidiaArticles'+str(iteration)+'.xlsx')
sheet1 = workbook.add_worksheet()
i = 0
for i in range(pages_per):
    for j in range(20):
        art1 = Scraper('https://www.techradar.com/more/filter/search/nvidia/news/publishedDate/' +
                       str(141-i-(pages_per*iteration))+'?searchTerm=nvidia', 'tr', str(20-j))
        # sheet1.write((i*20)+j, 0, art1.getArtDate())
        # sheet1.write((i*20)+j, 1, art1.getArtTime())
        # sheet1.write((i*20)+j, 2, art1.getArtFilteredText())
        schtuff.append(
            [art1.getArtDate(), art1.getArtTime(), art1.getArtLink(), art1.getArtFilteredText()])
        print('article ' + str((j+((i+(pages_per*iteration))*20))) +
              '/'+str((141)*20))
        print(len(schtuff[j][3]))


for i in range(len(schtuff)):
    sheet1.write(i, 0, schtuff[i][0])
    sheet1.write(i, 1, schtuff[i][1])
    sheet1.write(i, 2, schtuff[i][2])
    sheet1.write(i, 3, str(schtuff[i][3]))
workbook.close()
print("Finished iteration: " + str(iteration))
print('Elapsed Time: ' + str(time.time()-start_time))
