import csv
from datetime import date, datetime

monthlyList = []
with open('data/monthly_report.csv', mode='r') as csv_file:
    monthlyDict = csv.DictReader(csv_file)
    line_count = 0
    for row in monthlyDict:
        if line_count == 0:
            print(f'Column names are {", ".join(row)}')
            line_count += 1
        # print(f'{row}')
        monthlyList.append(row)
        line_count += 1
    print(f'Processed {line_count} lines.')

with open('data/daily_report.csv', mode='r') as csv_file:
    dailyCSV = csv.reader(csv_file)
    dailyList = []
    buildID = False
    dateFlag = False
    rowDict = {}
    for i, row in enumerate(dailyCSV, 1):
        # print(f'{i:4}. raw data {row}')
        if row[0] == '' and dateFlag:
            if buildID:
                buildID = False
                dateFlag = False
                rowDict = {}
            continue
        elif not buildID and not dateFlag and row[0] != '':
            patientID = row[0]
            print(f"\t{i:4}. Found patient ID = {patientID}")
            buildID = True
            continue
        elif buildID:
            try:
                rowDate = datetime.strptime(row[0], '%Y-%m-%d')
                rowDict['Patient ID'] = patientID
                rowDict['date'] = row[0]
                dailyList.append(rowDict)
                # print(f"\trowDict: {rowDict}")
                dateFlag = True
            except Exception as e:
                # print(f"\t{i:4}. {row[0]}  {e}")
                continue
    
print(dailyList)
print(monthlyList)

histogramCount = {}
for item in dailyList:
    try:
        histogramCount[item['Patient ID']] += 1
    except KeyError as err:
        histogramCount[item['Patient ID']] = 1
print(f"readings per Patient ID = {histogramCount}")

mergeData = []
for patient in monthlyList:
    mergeDict = patient
    try:
        mergeDict['readings'] = histogramCount[patient['Patient ID']]
    except KeyError as err:
        mergeDict['readings'] = 0
    # print(f"patient record: {mergeDict}")
    mergeData.append(mergeDict)

with open('data/merge_report.csv', mode='w') as csv_out:
    fieldnames = ['Patient ID', 'Billing Code', 'Duration', 'readings']
    writer = csv.DictWriter(csv_out, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(mergeData)
