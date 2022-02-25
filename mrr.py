import csv
import os
import sys

from datetime import date, datetime

DATA_FOLDER = 'data/'
used_files = set()

def getFilename(promptMsg):
    dirList = os.listdir(DATA_FOLDER)
    loop = True
    while loop:
        for i, dirItem in enumerate (dirList, 1):
            if dirItem.endswith(".csv"):
                print(f"{i:2}. {dirItem}")
        try:
            itemText = input(promptMsg)
            if itemText == 'Quit' or itemText.lower() == 'q':
                sys.exit()
            elif itemText == 'Next' or itemText.lower() == 'n':
                return 'Merge'

            itemNbr = int(itemText)
            if itemNbr < 1 or itemNbr > len(dirList):
                raise ValueError
            else:
                filename = dirList[itemNbr - 1]
        except Exception as err:
            print(f"You must input a number from 1 to {len(dirList)}. Please try again.")
            continue

        if filename in used_files:
            print(f"\nFile '{filename}' has already been used.  Please select a different file.")
        else:
            used_files.add(filename)
            loop = False

    return filename

def processReport():
    print("Enter 'quit' or 'Q' to exit.")
    monthlyFilename = getFilename("Enter the number for the monthy data file or 'quit' to exit: ")
    # print(monthlyFilename)

    monthlyList = []
    with open(os.path.join(DATA_FOLDER, monthlyFilename), mode='r') as csv_file:
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

    loop = True
    while (loop):
        print("\nEnter 'Next' or 'N' to create the consolidated report.")
        print("Enter 'quit' or 'Q' to abort the process.")
        dailyFilename = getFilename("Enter a report number to add another daily report: ")
        if dailyFilename == 'Merge':
            loop = False
            continue
        # print(dailyFilename)

        with open(os.path.join(DATA_FOLDER, dailyFilename), mode='r') as csv_file:
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
            
        # print(dailyList)
        # print(monthlyList)

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

    print("\nSaving the consolidated report.")
    with open('data/merge_report.csv', mode='w') as csv_out:
        fieldnames = ['Patient ID', 'Billing Code', 'Duration', 'readings']
        writer = csv.DictWriter(csv_out, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(mergeData)

if __name__ == "__main__":
    processReport()
