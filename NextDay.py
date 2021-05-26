import calendar


class NextDay():
    def __init__(self, indate):
        self.date = indate
        self.year = int(self.date[6:])
        self.month = int(self.date[:2])
        self.day = int(self.date[3:5])
        self.date = str(self.year) + '-' + \
            str(self.month).zfill(2) + '-' + str(self.day).zfill(2)

    def getNextDay(self):
        cal = calendar.Calendar()
        get = False
        found = False
        for i in cal.itermonthdates(self.year, self.month):
            if get:
                found = True
                self.date = str(i)
                self.year = int(self.date[:4])
                self.month = int(self.date[5:7])
                self.day = int(self.date[8:])
                get = False
                break
            if(str(i) == self.date):
                get = True
        if not found:
            if self.month == 12:
                self.year += 1
            self.month = int((self.month+1) % 12)
            if self.month == 0:
                self.month = 12
            self.day = 1
            self.date = str(self.year) + '-' + \
                str(self.month).zfill(2) + '-' + str(self.day).zfill(2)

    # for good friday

    def calc_easter(self, yr):
        # Returns Easter as a date object.
        a = yr % 19
        b = yr // 100
        c = yr % 100
        d = (19 * a + b - b // 4 - ((b - (b + 8) // 25 + 1) // 3) + 15) % 30
        e = (32 + 2 * (b % 4) + 2 * (c // 4) - d - (c % 4)) % 7
        f = d + e - 7 * ((a + 11 * d + 22 * e) // 451) + 114
        mo = f // 31
        da = f % 31 + 1
        return str(mo).zfill(2) + '-' + str(da).zfill(2)

    def getNextCalDay(self):
        self.getNextDay()
        return str(str(self.month).zfill(2) + '/' + str(self.day).zfill(2) + '/' + str(self.year))

    def getNext(self):
        cal = calendar.Calendar()
        # skip past weekends
        if int(calendar.weekday(self.year, self.month, self.day)) == 4:
            self.getNextDay()
        if int(calendar.weekday(self.year, self.month, self.day)) == 5:
            self.getNextDay()

        # normal get next day
        self.getNextDay()

        # weekday dependent holiday exceptions
        # MLK Jr self.day
        if self.month == 1 and calendar.weekday(self.year, self.month, self.day) == 0:
            count = 0
            for x in cal.itermonthdays2(self.year, 1):
                if x[0] > 0:
                    if x[1] == 0:
                        count += 1
                if count == 3:
                    if self.day == int(x[0]):
                        self.getNextDay()
                        break
        # Washington's Birthday
        if self.month == 2 and calendar.weekday(self.year, self.month, self.day) == 0:
            count = 0
            for x in cal.itermonthdays2(self.year, 2):
                if x[0] > 0:
                    if x[1] == 0:
                        count += 1
                if count == 3:
                    if self.day == int(x[0]):
                        self.getNextDay()
                        break
        # Good Friday
        if self.month >= 3 and self.month <= 4:
            easter_day = self.calc_easter(self.year)
            gfrimonth = int(easter_day[1])
            gfriday = int(easter_day[3:])
            # print(easter_day[3:])
            if int(easter_day[3:]) > 2:
                gfriday -= 2
            else:
                gfrimonth -= 1
                gfriday = 31-(2-int(easter_day[3:]))
            # print(gfriday)
            # print(gfrimonth)
            if self.day == gfriday and self.month == gfrimonth:
                self.getNextDay()
                self.getNextDay()
                self.getNextDay()

        # Memorial self.day
        if self.month == 5 and calendar.weekday(self.year, self.month, self.day) == 0:
            tempDay = 0
            for x in cal.itermonthdays2(self.year, 5):
                if x[0] > 0:
                    if x[1] == 0:
                        tempDay = x[0]
            if self.day == tempDay:
                self.getNextDay()
        # labor self.day
        if self.month == 9 and calendar.weekday(self.year, self.month, self.day) == 0:
            for x in cal.itermonthdays2(self.year, 9):
                if x[0] > 0:
                    if x[1] == 0:
                        if self.day == int(x[0]):
                            self.getNextDay()
        # thanksgiving
        if self.month == 11 and calendar.weekday(self.year, self.month, self.day) == 3:
            count = 0
            for x in cal.itermonthdays2(self.year, 11):
                if x[0] > 0:
                    if x[1] == 3:
                        count += 1
                if count == 4:
                    if self.day == int(x[0]):
                        self.getNextDay()
                        break

        # varying weekday holiday exceptions
        # new years (no change in observance)
        if self.day == 31 and self.month == 12:
            if int(calendar.weekday(self.year+1, 1, 1)) == 5:
                self.getNextDay()
                self.getNextDay()
                self.getNextDay()
        if self.day == 2 and self.month == 1:
            if int(calendar.weekday(self.year, 1, 1)) == 6:
                self.getNextDay()
        if self.day == 1 and self.month == 1:
            if int(calendar.weekday(self.year, 1, 1)) == 4:
                self.getNextDay()
                self.getNextDay()
            self.getNextDay()

        # Independence self.day
        if self.day == 3 and self.month == 7:
            if int(calendar.weekday(self.year, 7, 4)) == 5:
                self.getNextDay()
                self.getNextDay()
                self.getNextDay()
        if self.day == 5 and self.month == 7:
            if int(calendar.weekday(self.year, 7, 4)) == 6:
                self.getNextDay()
        if self.day == 4 and self.month == 7:
            if int(calendar.weekday(self.year, 7, 4)) == 4:
                self.getNextDay()
                self.getNextDay()
            self.getNextDay()

        # Christmas
        if self.day == 25 and self.month == 12:
            self.getNextDay()
            if int(calendar.weekday(self.year, 12, 25)) == 4:
                self.getNextDay()
                self.getNextDay()
        if self.day == 24 and self.month == 12:
            if int(calendar.weekday(self.year, 12, 25)) == 5:
                self.getNextDay()
                self.getNextDay()
                self.getNextDay()
        if self.day == 26 and self.month == 12:
            if int(calendar.weekday(self.year, 12, 25)) == 6:
                self.getNextDay()

        # Huricane Sandy
        if self.year == 2012 and self.month == 10 and (self.day == 29 or self.day == 30):
            if(self.day == 29):
                self.getNextDay()
            self.getNextDay()

        # George H. W. Bush died
        if self.year == 2018 and self.month == 12 and self.day == 5:
            self.getNextDay()

        # Gerald Ford Died
        if self.year == 2007 and self.month == 1 and self.day == 2:
            self.getNextDay()

        # print(self.date)
        return str(str(self.month).zfill(2) + '/' + str(self.day).zfill(2) + '/' + str(self.year))
