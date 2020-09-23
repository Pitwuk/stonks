import requests
from bs4 import BeautifulSoup

from Scraper import Scraper
# tech radar history
# https://www.techradar.com/more/filter/search/nvidia/news/publishedDate/100?searchTerm=nvidia

sites_list = {
    'aat': 'https://www.anandtech.com/SearchResults?CurrentPage=3&q=nvidia&sort=date', 'tr': 'https://www.techradar.com/more/filter/search/nvidia/news/publishedDate/23?searchTerm=nvidia', 'pcw': 'https://www.pcworld.com/search?query=nvidia&s=d&start=0&submit=search&t=2', 'vg': 'https://www.theverge.com/search?order=date&page=137&q=nvidia&type=Article', 'th': 'https://www.tomshardware.com/more/filter/search/nvidia/all/publishedDate/335?searchTerm=nvidia'}


art1 = Scraper(sites_list['aat'], 'aat', 2)
print(art1.getNumArticles())
print(art1.getArtLink())
print(art1.getDateTime())
print(art1.getArtDate())
print(art1.getArtTime())
# print(art1.getArtFilteredText())
