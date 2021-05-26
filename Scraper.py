import requests
import time
import datetime
from bs4 import BeautifulSoup
import csv

article_map = {'tr': 'listingResult small result',
               'pcw': 'excerpt-text', 'vg': 'c-compact-river__entry', 'th': 'listingResult small result', 'pcg': 'listingResult small result', 'aat': 'cont_box1'}
dt_tim = {'tr': 'no-wrap relative-date chunk', 'ee': 'post-date single', 'vg': 'c-byline__item',
          'th': 'no-wrap relative-date chunk', 'pcg': 'no-wrap relative-date chunk', 'tnp': 'entry-meta-date updated'}
art_bodies = {'tr': 'article-body', 'ee': 'entry-content', 'vg': 'c-entry-content',
              'th': 'article-body', 'pcg': 'article-body', 'aat': 'articleContent', 'tnp': 'entry-content clearfix', 'fb': 'article-body-container'}
sites_list = {
    'aat': 'https://www.anandtech.com/SearchResults?CurrentPage=PAGENUMBER&q=SEARCHTERM&sort=date', 'tr': 'https://www.techradar.com/more/filter/search/SEARCHTERM/news/publishedDate/PAGENUMBER?searchTerm=SEARCHTERM',
    'ee': 'https://www.eejournal.com/page/PAGENUMBER/?s=SEARCHTERM', 'th': 'https://www.tomshardware.com/more/filter/search/SEARCHTERM/all/publishedDate/PAGENUMBER?searchTerm=SEARCHTERM',
    'pcg': 'https://www.pcgamer.com/more/filter/search/SEARCHTERM/all/publishedDate/PAGENUMBER/?searchTerm=SEARCHTERM', 'tnp': 'https://www.nextplatform.com/page/PAGENUMBER/?s=SEARCHTERM',
    'fb': 'https://www.forbes.com/simple-data/search/more/?start=PAGENUMBER&sort=recent&q=SEARCHTERM'}
link_headers = {'pcw': 'https://www.pcworld.com/',
                'aat': 'https://www.anandtech.com'}
necessary_component = {'fb': 'https://www.forbes.com/sites/'}
cooldown_sites = ['fb']
cooldown_limits = {'fb':200}#number of requests that can be made before the cooldown goes into effect
daily_limits = {'fb':3000}#number of requests that can be made each day before ip gets blocked
cooldown_counter = 0

article = ''
is_set = False
months = {'January': '01', 'February': '02', 'March': '03', 'April': '04', 'May': '05', 'June': '06',
          'July': '07', 'August': '08', 'September': '09', 'October': '10', 'November': '11', 'December': '12'}
short_months = {'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05', 'Jun': '06',
                'Jul': '07', 'Aug': '08', 'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'}
soup_headers = {'User-Agent': 'Mozilla/5.0'}


class Scraper:

    def __init__(self, site, search_term, page_num=1):
        global is_set
        is_set = False
        self.site = site
        self.search_term = search_term
        self.page_num = page_num
        self.num_pages = -1
        self.article_num = 1
        self.setLink()
        self.links = []
        self.link_history = []
        self.request_counter=0
        self.request_limit_not_met=True
        # parameter declaration

        if self.site in cooldown_sites:
            self.getCooldownRequests()

    # updates the article link to new search term and page number
    def setLink(self):
        self.link = sites_list[self.site]
        self.link = self.link.replace('SEARCHTERM', self.search_term)
        # handle cases where link has start article number instead of page number
        if(self.site == 'fb'):
            self.link = self.link.replace(
                'PAGENUMBER', str((self.page_num-1)*20))
        else:
            self.link = self.link.replace('PAGENUMBER', str(self.page_num))

    # sets the site
    def setSite(self, site):
        self.site = site
        self.setLink()

    # set the page number
    def setPage(self, page_num):
        self.page_num = page_num
        self.setLink()
        self.getArticleLinks()
        

    # returns the link of the currently set article
    def getArtLink(self):
        return self.links[self.article_num-1]

    # returns the number of articles on the page

    def getNumArticles(self):
        if len(self.links) == 0:
            self.getArticleLinks()
        return len(self.links)

    # returns true if the page has articles on it
    def containsArticles(self):
        return not self.getNumArticles() == 0


    # returns the number of pages for the search term on the site
    def getNumPages(self):
        print('Getting number of pages')
        if self.num_pages == -1:
            #increment page number by ten until page empty 
            while True:
                page_num = self.page_num+10
                self.setPage(page_num)
                if not self.containsArticles():
                    #if the site has a cooldown try cooling down before determining last page
                    if self.site in cooldown_sites:
                        self.cooldownSetPage(page_num)
                        if not self.containsArticles():
                            break
                    else:
                        break
            
            self.link_history=[] #empty link history

            #go back 10 then increment by 1 until page is empty
            self.page_num-=10
            while True:
                page_num = self.page_num+1
                self.setPage(page_num)
                if not self.containsArticles():
                    #if the site has a cooldown try cooling down before determining last page
                    if self.site in cooldown_sites:
                        self.cooldownSetPage(page_num)
                        if not self.containsArticles():
                            break
                    else:
                        break
            self.link_history=[] #empty link history

            self.setPage(self.page_num-1)
            self.num_pages = self.page_num

        return self.num_pages


    #cools down a few times while trying to set the page
    def cooldownSetPage(self, num):
        global cooldown_counter
        while cooldown_counter < 10 and not self.containsArticles() and self.request_counter>cooldown_limits[self.site]:
            cooldown_counter += 1
            print('Attempting cooldown ' +
                    str(cooldown_counter), end='\r')
            time.sleep(120)
            self.setPage(num)

        cooldown_counter = 0


    # stores all article links on the page in an array
    def getArticleLinks(self):
        self.links = []
        #check cooldown request limit
        if self.site in cooldown_sites:
            if self.request_counter >= daily_limits[self.site]:
                print('Maximum number of requests for ' + self.site + ' today.')
                self.request_limit_not_met=False
                return 
            else:
                self.request_counter+=1
        # get html file of the home page
        homepage = requests.get(
            self.link, headers=soup_headers)
        homepage = BeautifulSoup(homepage.text, 'html.parser')

        # determine what website is being scraped and choose the top article
        if self.site == 'aat':
            for i in homepage.find_all(class_=article_map[self.site]):
                if self.site in link_headers.keys():
                    link = link_headers[
                        self.site]+i.find('a')['href']
                else:
                    link = i.find('a')['href']
                if link not in self.link_history:
                    self.links.append(link)
                    self.link_history.append(link)
        elif self.site == 'ee' or self.site == 'tnp' or self.site == 'fb':
            for i in homepage.find_all('article'):
                if self.site in link_headers.keys():
                    link = link_headers[
                        self.site]+i.find('a')['href']
                else:
                    link = i.find('a')['href']
                if link not in self.link_history and necessary_component[self.site] in link:
                    self.links.append(link)
                    self.link_history.append(link)
        else:
            i = 1
            while True:
                try:
                    link = homepage.find(
                        class_=article_map[self.site]+str(i)).find('a')['href']
                    if link not in self.link_history:
                        self.links.append(link)
                        self.link_history.append(link)
                    i += 1
                except:
                    break

    # set the current article to the article number

    def setArticle(self, article_num):
        global article
        global is_set
        is_set = True
        self.article_num = article_num
        try:
            #check cooldown request limit
            if self.site in cooldown_sites:
                if self.request_counter >= daily_limits[self.site]:
                    print('Maximum number of requests for ' + self.site + ' today.')
                    self.request_limit_not_met=False
                    return 
                else:
                    self.request_counter+=1
            article = BeautifulSoup(requests.get(
                self.getArtLink(), headers=soup_headers).text, 'html.parser')
        except:
            print('Broken Link')
            article = ''

    # returns the datetime object the article was posted
    def getDateTime(self):
        global article, cooldown_counter, is_set
        if not is_set:
            print('Article Not Sent')
        else:
            try:
                if self.site == 'ee' or self.site == 'tnp':
                    datetime = article.find(
                        class_=dt_tim[self.site]).get_text()
                elif self.site == 'th' or self.site == 'pcg':
                    datetime = article.find(
                        'time', class_=dt_tim[self.site]).get('datetime')
                elif self.site == 'aat':
                    datetime = article.find('em').get_text()
                elif self.site == 'fb':
                    datetime = ''
                    time_arr = article.find(
                        class_='metrics-channel').find_all('time')
                    datetime += time_arr[0].get_text() + \
                        ' '+time_arr[1].get_text()
                else:
                    datetime = article.find(
                        class_=dt_tim[self.site]).get('datetime')
            except Exception as e:
                if self.site in cooldown_sites and cooldown_counter < 10:
                    cooldown_counter += 1
                    print('Attempting cooldown ' +
                          str(cooldown_counter), end='\r')
                    time.sleep(120)
                    self.setArticle(self.article_num)
                    return self.getDateTime()
                print('Couldn\'t find datetime')
                print(self.getArtLink())
                print(article)
                print(e)
                datetime = '0000-00-00T00:00'
        cooldown_counter = 0
        return datetime

    # returns the hour the article was uploaded
    def getArtTime(self):
        datetime = self.getDateTime()
        if datetime == '0000-00-00T00:00':
            time = 0
        elif self.site == 'aat':
            arr = datetime.split(' ')
            time = int(arr[4].split(':')[0])
            if arr[5] == 'PM' and time != 12:
                time += 12
            elif arr[5] == 'AM' and time == 12:
                time = 0
        elif self.site == 'fb':
            arr = datetime.split(' ')
            time = int(arr[3].split(':')[0])
            if arr[3][5:7] == 'pm' and time != 12:
                time += 12
            elif arr[3][5:7] == 'am' and time == 12:
                time = 0
        elif self.site == 'ee' or self.site == 'tnp':
            time = 12
        else:
            date = datetime.split('T')
            time = int(date[1][:2])
        return time

    # return the date the article was posted
    def getArtDate(self):
        datetime = self.getDateTime()

        if datetime == '0000-00-00T00:00':
            return '00-00-0000'
        # convert written months to numbers
        elif self.site == 'aat' or self.site == 'ee' or self.site == 'tnp':
            i = 0
            if self.site == 'aat':
                i = 1
            arr = datetime.split(' ')
            date = str(months[arr[i]] + '-' +
                       arr[i+1].replace(',', '').zfill(2) + '-' + arr[i+2])
            return date
        # convert written shortened months to nummbers
        elif self.site == 'fb':
            i = 0
            arr = datetime.split(' ')
            date = str(short_months[arr[i]] + '-' +
                       arr[i+1].replace(',', '').zfill(2) + '-' + arr[i+2].replace(',', ''))
            return date
        else:
            date = datetime.split('T')
            date[0] = date[0][5:] + '-' + date[0][:4]
            return date[0]

    # returns the raw text from the article
    def getArtText(self):
        global article
        global is_set
        if not is_set:
            print('Article Not Sent')
        else:
            try:
                if self.site == 'ee' or self.site == 'aat' or self.site == 'tnp' or self.site == 'fb':
                    content = article.find(
                        class_=art_bodies[self.site]).get_text(separator=' ')
                else:
                    content = article.find(
                        id=art_bodies[self.site]).get_text(separator=' ')
            except:
                content = ''
            # if self.site == 'tr' or self.site == 'th' or self.site == 'pcg':
            content = self.filterJunk(content, 'figure')
            content = self.filterJunk(content, 'table')
            content = self.filterJunk(
                content, 'article-sharing__item', is_class=True)

        return content.lower()

    # removes junk from the provided text
    def filterJunk(self, content, name, is_class=False):
        try:
            if(is_class):
                junk = article.findAll(class_=name)
            else:
                junk = article.findAll(name)
            # print(junk)
            for i in range(len(junk)):
                if len(junk[i].get_text()) > 0:
                    content = content.replace(
                        junk[i].get_text(separator=' '), " ")
        except:
            pass
        return content

    # returns the cleaned text of the article

    def getArtFilteredText(self):
        article = self.getArtText()
        filt = article.replace(',', str(' ')).replace('.', ' ').replace('^', ' ').replace('#', ' ').replace('(', ' '). replace(')', ' '). replace('|', ' '). replace('*', ' ').replace('+', ' ').replace('$', ' $').replace(';', ' ').replace(':', ' ').replace('\\', ' ').replace('\"', ' ').replace('/', ' ').replace('<', " ").replace('>', ' ').replace('[', ' ').replace(
            ']', ' ').replace('{', ' ').replace('}', ' ').replace('_', ' ').replace('\'', str(' ')).replace(' - ', ' ').replace('~', ' ').replace('`', ' ').replace('?', ' ').replace('!', ' ').replace('\n', str(' ')).replace('\r', str(' ')).replace('–', str(' ')).replace('&', 'and').encode('utf-8').decode('ascii', 'ignore')
        while '  ' in filt:
            filt = filt.replace('  ', ' ')
        return filt.strip()

    # returns map of article data
    def getArtData(self):
        data = {}
        data['site'] = self.site
        data['link'] = self.getArtLink()
        data['date'] = self.getArtDate()
        data['time'] = self.getArtTime()
        data['text'] = self.getArtFilteredText()
        return data

    # returns array of maps of article data
    def getPageData(self, verbose=True):
        if verbose:
            print('Getting Page Data for ' +
                  self.search_term + ' on ' + self.site+' on Page: '+str(self.page_num))
        numArticles = self.getNumArticles()
        data = []
        for i in range(1, numArticles+1):
            self.setArticle(i)
            data.append(self.getArtData())

        if self.site in cooldown_sites:
            self.writeCooldownRequests()
        return data

    # returns array of full history of search term on site
    def getSiteHistory(self):
        i = 1
        data = []
        print('Getting Full Site History for ' +
              self.search_term + ' on ' + self.site)
        
        self.getNumPages()

        while self.request_limit_not_met:
            try:
                if(i <= self.num_pages):
                    print('Page: ' + str(i)+ '/'+str(self.num_pages) + '                ', end='\r')
                    self.setPage(i)
                    if not self.containsArticles() and self.site in cooldown_sites:
                        self.cooldownSetPage(i)

                else:
                    print('Last Page: ' + str(i)+ '                ')
                    break

                data += self.getPageData(verbose=False)
                i += 1
            except Exception as e:
                print(e)
                break
        if self.site in cooldown_sites:
            self.writeCooldownRequests()
        return data

    # returns array of full history of search term on site starting from the oldest
    def getSiteHistoryReverse(self):
        data = []
        print('Getting Full Site History for ' +
              self.search_term + ' on ' + self.site)
        
        self.getNumPages()
        i = self.num_pages

        while self.request_limit_not_met:
            try:
                if(i > 0):
                    print('Page: ' + str(i)+ '/'+str(self.num_pages) + '                ', end='\r')
                    self.setPage(i)
                    if not self.containsArticles() and self.site in cooldown_sites:
                        self.cooldownSetPage(i)

                else:
                    print('Last Page: ' + str(i)+ '                ')
                    break

                data += self.getPageData(verbose=False)
                i -= 1
            except Exception as e:
                print(e)
                break
        if self.site in cooldown_sites:
            self.writeCooldownRequests()
        return data

    # returns array of articles until a matching link is found for search term on site
    def getUntilMatch(self, lastLink):
        i = 1
        data = []
        counter = 0
        notFound = True
        print('Getting Until Match for ' +
              self.search_term + ' on ' + self.site)

        self.getNumPages()

        while notFound and self.request_limit_not_met:
            try:
                if(i <= self.num_pages):
                    print('Page: ' + str(i)+ '/'+str(self.num_pages) + '                ', end='\r')
                    self.setPage(i)
                    if not self.containsArticles() and self.site in cooldown_sites:
                        self.cooldownSetPage(i)

                else:
                    print('Last Page: ' + str(i)+ '                ')
                    break

                for j in self.getPageData(verbose=False):
                    # print(j['link'])
                    if j['link'] != lastLink:
                        counter += 1
                        data.append(j)
                    else:
                        print('Match Found After '+str(counter)+' Articles')
                        notFound = False
                        break
                i += 1
            except Exception as e:
                print(e)
                break
        if self.site in cooldown_sites:
            self.writeCooldownRequests()
        return data

    #saves number of requests to cooldown requests file
    def writeCooldownRequests(self):
        try:
            file = open('./log/cooldown_requests.csv', 'a')
            file.write('"'+str(datetime.datetime.now())[:10]+'","'+self.site+'","'+str(self.request_counter)+'"\n')
            file.close()

        except Exception as e:
            print(e)
        self.cleanCooldownRequests()
    
    #removes old data in the cooldown requests file
    def cleanCooldownRequests(self):
        try:
            file = open('./log/cooldown_requests.csv', 'r')
            data = csv.reader(file, delimiter=',')
            today_data=[]
            temp_requests={}#site name and index in today_data
            for row in data:
                if len(row)>0 and row[0] == str(datetime.datetime.now())[:10]:
                        #if the site has multiple entries for today keep the highest
                        if row[1] in temp_requests.keys():
                            if today_data[temp_requests[row[1]]][2] < row[2]:
                                today_data[temp_requests[row[1]]][2] = row[2]
                        else:
                            temp_requests[row[1]]=len(today_data)
                            today_data.append(row)
            file.close()
            file = open('./log/cooldown_requests.csv', 'w+', newline='')
            write = csv.writer(file)
            write.writerows(today_data)
            file.close()

            print('Cooldown Requests Cleaned')
        except Exception as e:
            print(e)

    #adds cooldown requests from today to the request counter
    def getCooldownRequests(self):
        self.cleanCooldownRequests()
        try:
            file = open('./log/cooldown_requests.csv', 'r')
            data = csv.reader(file, delimiter=',')
            for row in data:
                if row[1] == self.site:
                    self.requests=row[2]
                    break
            file.close()

        except Exception as e:
            print(e)