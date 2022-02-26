"""
"""

import app.utils6L.utils6L as utils

import csv
import logging
import os
import PySimpleGUI as sg
import sys

from datetime import date, datetime

logger_name = os.getenv("LOGGER_NAME")
logger = logging.getLogger(logger_name)

monthly_filename_remember = ''
monthly_list = []
dailyList = set()
used_files = set()

@utils.log_wrap
def load_master_data():
    logger.info(__name__ + ".get_master_data()")

    monthly_filename = sg.popup_get_file('Select the monthly report')
    if monthly_filename is None or monthly_filename == '':
        sys.exit()

    global monthly_filename_remember
    monthly_filename_remember = monthly_filename

    with open(monthly_filename, mode='r') as csv_file:
        monthlyDict = csv.DictReader(csv_file)
        for i, row in enumerate(monthlyDict):
            if i == 0:
                print(f'Base column names are {", ".join(row)}')
    # Add the readings column to the Monthly list row
    # mergeData will have the same rows and comlumns as the Monthly file plus a 'readings' value for each row 
            row['readings'] = 0
            monthly_list.append(row)
            # print(f'{row}')
        print(f'Monthly list has {len(monthly_list)} patient accounts.')
    
    return csv_file.name

@utils.log_wrap
def get_monthly_list():
    logger.info(__name__ + ".get_monthly_list()")
    return monthly_list


@utils.log_wrap
def get_monthly_list_summary():
    logger.info(__name__ + ".get_monthly_list_summary()")

    monthly_list_summary = []
    row = 1
    for item in monthly_list:
        if item['readings'] != 0:
            account_row = (row, item['Patient ID'], item['Billing Code'], item['Duration'], item['readings'])
            monthly_list_summary.append(account_row)
            row += 1
    logger.info(f"The monthly account readings summary has {len(monthly_list_summary)} items")
    return monthly_list_summary


@utils.log_wrap
def get_monthly_summary_csv_data():
    logger.info(__name__ + ".get_monthly_summary_csv_data()")

    monthly_list_summary = []
    for item in monthly_list:
        if item['readings'] != 0:
            monthly_list_summary.append(item)
    logger.info(f"The monthly account readings summary has {len(monthly_list_summary)} items")
    return monthly_list_summary


@utils.log_wrap
def load_daily_report():
    logger.info(__name__ + ".load_daily_report()")    

    daily_filename = sg.popup_get_file('Select a daily report')
    if daily_filename is None or daily_filename == '':
        return

    if daily_filename in used_files:
        logger.info(f"\nFile '{daily_filename}' has already been used.")
        return "used"
    else:
        used_files.add(daily_filename)

    global dailyList
    with open(daily_filename, mode='r') as csv_file:
        dailyCSV = csv.reader(csv_file)
        buildID = False
        dateFlag = False
        for i, row in enumerate(dailyCSV, 1):
            # print(f'{i:4}. raw data {row}')
            if row[0] == '' and dateFlag:
                if buildID:
                    buildID = False
                    dateFlag = False
            elif not buildID and not dateFlag and row[0] != '':
                patientID = row[0]
                logger.info(f"\t{i:4}. Found patient ID = {patientID}")
                buildID = True
            elif buildID:
                try:
                    rowDate = datetime.strptime(row[0], '%Y-%m-%d')
                    readingDate = rowDate.strftime('%Y-%m-%d')
                    dailyList.add((patientID, readingDate,))
                    dateFlag = True
                except Exception:
                    # print(f"\t{i:4}. {row[0]}  {e}")
                    continue
        
    # print(dailyList)
    # print(monthlyList)

    histogram_count = {}
    for patientID, readingDate in dailyList:
        try:
            histogram_count[patientID] += 1
        except KeyError:
            histogram_count[patientID] = 1
    logger.info(f"readings per Patient ID = {histogram_count}")

    global monthly_list
    for i, patient_account_summary in enumerate(monthly_list):
        patient_id = patient_account_summary['Patient ID']
        if patient_id in histogram_count:
            monthly_list[i]['readings'] = histogram_count[patient_id]
            logger.info(f"Updated monthly list record {monthly_list[i]}")

    return csv_file.name


@utils.log_wrap
def save_csv():
    logger.info(__name__ + ".save_csv()")
    logger.info("Saving the consolidated report.")

    save_folder = sg.popup_get_folder('Choose folder for saving merged report')
    if save_folder is None or save_folder == '':
        sys.exit()

    monthly_list_summary = get_monthly_summary_csv_data()

    global monthly_filename_remember
    dir_name = os.path.dirname(monthly_filename_remember)
    file_name = os.path.join(dir_name, 'account_summary.csv')

    with open(file_name, mode='w', newline='') as csv_out:
        fieldnames = ['Patient ID', 'Billing Code', 'Duration', 'readings']
        writer = csv.DictWriter(csv_out, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(monthly_list_summary)
