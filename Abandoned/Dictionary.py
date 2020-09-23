from openpyxl import Workbook
from openpyxl import load_workbook
import csv
import operator


class Dictionary:
    def __init__(self, file, text):
        self.file = file
        reader = csv.reader(open(file, 'r', encoding='utf-8'))
        try:
            self.dic = {rows[1]: int(rows[0]) for rows in reader}
        except:
            self.dic = {}
        # +print(self.dic)
        self.arr = text.split(' ')
        # print(self.arr[1])

    # takes numer of words after each to include in dictionary
    def addWordsSort(self, contLen):
        for i in range(len(self.arr)-contLen):
            strang = ' '
            if strang.join(self.arr[i:i+contLen]) in self.dic:
                self.dic[strang.join(self.arr[i:i+contLen])] += 1
            else:
                self.dic[strang.join(self.arr[i:i+contLen])] = 1
        sorted_dic = dict(sorted(
            self.dic.items(), key=operator.itemgetter(1), reverse=True))
        with open(self.file, 'w', newline='', encoding='utf-8') as output:
            writer = csv.writer(output)
            for key, value in sorted_dic.items():
                writer.writerow([value, key])

    def printDict(self):
        reader = csv.reader(open(self.file, 'r', encoding='utf-8'))
        for rows in reader:
            print(', '.join(rows))
        # with open(self.file, 'a', newline='', encoding='utf-8') as dic:
        #     dik = csv.reader(dic, delimiter=' ', quotechar='|')
        #     for row in dik:
        #         print(', '.join(str(row.decode('utf-8'))))
