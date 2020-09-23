import openpyxl as xl

newWB = xl.Workbook()
newWS = newWB.active
stockws = xl.load_workbook('NVDA\\NVDA.xlsx', data_only=True).active

for row in stockws.rows:
    row_arr = []
    date = str(row[0].value)[5:7] + '/' + \
        str(row[0].value)[8:10] + '/' + str(row[0].value)[:4]
    row_arr = [date, str(row[1].value)]
    newWS.append(row_arr)
newWB.save('NVDA\\NVDA.xlsx')
