import requests
from bs4 import BeautifulSoup

article_map = {'tr': 'listingResult small result',
               'pcw': 'excerpt-text', 'vg': 'c-compact-river__entry', 'th': 'listingResult small result', 'pcg': 'listingResult small result', 'aat': 'cont_box1'}
dt_tim = {'tr': 'no-wrap relative-date chunk',
          'pcw': 'datePublished', 'vg': 'c-byline__item', 'th': 'no-wrap relative-date chunk', 'pcg': 'no-wrap relative-date chunk'}
art_bodies = {'tr': 'article-body',
              'pcw': 'drr-container', 'vg': 'c-entry-content', 'th': 'article-body', 'pcg': 'article-body', 'aat': 'articleContent'}
article = ''
is_set = False
months = {'January': '01', 'February': '02', 'March': '03', 'April': '04', 'May': '05', 'June': '06',
          'July': '07', 'August': '08', 'September': '09', 'October': '10', 'November': '11', 'December': '12'}


class Scraper:

    def __init__(self, link, site, num):
        global is_set
        is_set = False
        self.site = site
        self.num = num
        self.link = link
        self.art_link = ''
        # parameter declaration

    def getArtLink(self):
        if self.art_link == '':
            # get html file of the home page
            homepage = requests.get(self.link, allow_redirects=False)
            homepage = BeautifulSoup(homepage.text, 'html.parser')

            # determine what website is being scraped and choose the top article
            if self.site == 'pcw':
                links = []
                for i in homepage.find_all(class_=article_map[self.site]):
                    if i.find('a')['href'][:8] == '/article':
                        links.append(i.find('a')['href'])
                    elif i.find('a')['href'][:7] == '/column':
                        links.append(i.find_all('a')[1]['href'])
                artLink = 'https://www.pcworld.com/' + links[self.num-1]
            elif self.site == 'vg' or self.site == 'aat':
                links = []
                for i in homepage.find_all(class_=article_map[self.site]):
                    links.append(i.find('a')['href'])
                # print(self.num)
                artLink = links[self.num-1]
            else:
                artLink = homepage.find(
                    class_=article_map[self.site]+str(self.num)).find('a')['href']
            if self.site == 'th':
                artLink = 'https://www.tomshardware.com/' + artLink
            if self.site == 'aat':
                artLink = 'https://www.anandtech.com' + artLink
            self.art_link = artLink
            return artLink
        return self.art_link

    def getNumArticles(self):
        # get html file of the home page
        homepage = requests.get(self.link)
        homepage = BeautifulSoup(homepage.text, 'html.parser')
        # determine what website is being scraped and choose the top article
        links = []
        if self.site == 'tr' or self.site == 'th' or self.site == 'pcg':
            for i in range(30):
                try:
                    links.append(homepage.find(
                        class_=article_map[self.site]+str(i+1)).find('a')['href'])
                except:
                    break
        else:
            for i in homepage.find_all(class_=article_map[self.site]):
                if self.site == 'pcw':
                    if i.find('a')['href'][:8] == '/article':
                        links.append(i.find('a')['href'])
                    elif i.find('a')['href'][:7] == '/column':
                        links.append(i.find_all('a')[1]['href'])
                elif self.site == 'vg' or self.site == 'aat':
                    links.append(i.find('a')['href'])

        return len(links)

    def setArticle(self):
        global article
        global is_set
        is_set = True
        try:
            article = BeautifulSoup(requests.get(
                self.getArtLink()).text, 'html.parser')
        except:
            print('Broken Link')
            article = ''

    def getDateTime(self):
        global article
        global is_set
        if not is_set:
            self.setArticle()
        try:
            if self.site == 'pcw':
                datetime = article.find(
                    itemprop=dt_tim[self.site]).get('content')
            elif self.site == 'vg':
                datetime = article.find(
                    'time', class_=dt_tim[self.site]).get('datetime')
                # print(datetime)
            elif self.site == 'th' or self.site == 'pcg':
                datetime = article.find(
                    'time', class_=dt_tim[self.site]).get('datetime')
            elif self.site == 'aat':
                datetime = article.find('em').get_text()
            else:
                datetime = article.find(
                    class_=dt_tim[self.site]).get('datetime')
        except:
            datetime = '0000-00-00T00:00'

        return datetime

    def getArtTime(self):
        datetime = self.getDateTime()
        if self.site == 'aat':
            arr = datetime.split(' ')
            time = int(arr[4][0])
            if arr[5] == 'PM':
                time += 12
        else:
            date = datetime.split('T')
            time = int(date[1][:2])
        return time

    def getArtDate(self):
        datetime = self.getDateTime()
        if self.site == 'aat':
            arr = datetime.split(' ')
            date = str(months[arr[1]] + '/' +
                       arr[2].replace(',', '').zfill(2) + '/' + arr[3])
            return date
        else:
            date = datetime.split('T')
            date[0] = date[0][5:].replace('-', '/') + '/' + date[0][:4]
            return date[0]

    def getArtText(self):
        global article
        global is_set
        if not is_set:
            self.setArticle()
        try:
            if self.site == 'vg' or self.site == 'aat':
                content = article.find(class_=art_bodies[self.site]).get_text()
            else:
                content = article.find(id=art_bodies[self.site]).get_text()
            # print(content)
        except:
            content = ''
        if self.site == 'tr' or self.site == 'th' or self.site == 'pcg':
            try:
                captions = article.findAll('figure')
                # print(captions)
                for i in range(len(captions)):
                    if len(captions[i].get_text()) == 0:
                        break
                    content = content.replace(captions[i].get_text(), " ")
            except:
                captions = ''
        # if len(content) > 32767:
        #     return content[:36767]
        # print(content)
        return content.lower()

    def getArtFilteredText(self):
        article = self.getArtText()
        filt = article.replace(', ', ' ').replace('.', ' ').replace('(', ' '). replace(')', ' ').replace(';', ' ').replace(':', ' ').replace('\\', ' ').replace('\"', ' ').replace('/', ' ').replace('<', " ").replace('>', ' ').replace('[', ' ').replace(
            ']', ' ').replace('{', ' ').replace('}', ' ').replace('_', ' ').replace('\'s', str('')).replace('\' ', str('')).replace(' \'', str('')).replace(' - ', ' ').replace('?', ' ').replace('!', ' ').replace('\n', str('')).replace('–', str('')).replace('&', 'and')
        while '  ' in filt:
            filt = filt.replace('  ', ' ')
        return filt.strip()
