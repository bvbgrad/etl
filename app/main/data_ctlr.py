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
account_set = set()
patient_set = set()
dailyList = set()
used_files = set()

@utils.log_wrap
def load_master_data(window):
    logger.info(__name__ + ".get_master_data()")

    monthly_filename = sg.popup_get_file('Select the monthly report')
    if monthly_filename is None or monthly_filename == '':
        sys.exit()

    global monthly_filename_remember
    global account_set
    global patient_set
    monthly_filename_remember = monthly_filename

    print(f"Log intiated at: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"Master Account file loaded: {monthly_filename}")

    with open(monthly_filename, mode='r') as csv_file:
        monthlyDict = csv.DictReader(csv_file)
        for i, row in enumerate(monthlyDict):
            if i == 0:
                logger.info(f'Base column names are {", ".join(row)}')
    # Add the readings column to the Monthly list row
            account_set.add(row['Patient ID'])
            patient_set.add(row['Patient Name'])

            csv_row = {}
            csv_row['Patient Name'] = row['Patient Name']
            csv_row['Billing Code'] = row['Billing Code']
            csv_row['Duration'] = row['Duration']
            csv_row['readings'] = 0
            monthly_list.append(csv_row)
    logger.info(f'Monthly list has {len(monthly_list)} patient accounts.')
    
    window['-STATUS-'].update(f"Master Account file loaded with {len(monthly_list)} patient accounts.")
    return csv_file.name

@utils.log_wrap
def get_monthly_list():
    logger.info(__name__ + ".get_monthly_list()")
    return monthly_list


@utils.log_wrap
def get_monthly_list_summary():
    logger.info(__name__ + ".get_monthly_list_summary()")

    monthly_list_summary = []
    for i, item in enumerate(monthly_list, 1):
        account_row = (i, item['Patient Name'], item['Billing Code'], item['Duration'], item['readings'])
        monthly_list_summary.append(account_row)
    logger.info(f"The monthly patient summary has {len(monthly_list_summary)} items")
    return monthly_list_summary


@utils.log_wrap
def get_monthly_summary_csv_data():
    logger.info(__name__ + ".get_monthly_summary_csv_data()")

    monthly_list_summary = []
    for item in monthly_list:
        monthly_list_summary.append(item)
    logger.info(f"The monthly account readings summary has {len(monthly_list_summary)} items")
    return monthly_list_summary


@utils.log_wrap
def load_daily_report(window):
    logger.info(__name__ + ".load_daily_report()")    

    daily_filename = sg.popup_get_file('Select a daily report')
    if daily_filename is None or daily_filename == '':
        window['-STATUS-'].update(f"No daily file was selected.")
        return

    if daily_filename in used_files:
        logger.info(f"File '{daily_filename}' has already been used.")
        sg.popup_ok(f"'{daily_filename}'\nhas already been used.")
        window['-STATUS-'].update(f"Loading of {daily_filename} failed")
        window['-REPORT_TEXT_1-'].update(f"File has already been loaded. Please try again.")
        return
    else:
        used_files.add(daily_filename)

    print(f"Loaded daily report '{daily_filename}'")
    global dailyList
    global monthly_list

    daily_rows = []
    with open(daily_filename, mode='r') as csv_file:
        dailyCSV = csv.reader(csv_file)
        for i, row in enumerate(dailyCSV, 1):
            row[0] = row[0].replace('/', '-')
            daily_rows.append(row)

    newPatientAccount = False
    bDate = False
    for i, row in enumerate(daily_rows, 1):
        if row[0] in account_set:
            newPatientAccount = True
            continue
        if newPatientAccount:
            patientName = row[0]
            newPatientAccount = False
            bDate = True
            continue
        if bDate:
            date_format = '%Y-%m-%d'
            try:
                rowDate = datetime.strptime(row[0], date_format)
            except Exception:
    # switch to alternate date format if default date format fails on birth date
                date_format = '%m-%d-%Y'
            bDate = False
            continue
        if not newPatientAccount and not bDate:
            try:
                rowDate = datetime.strptime(row[0], date_format)
                readingDate = rowDate.strftime('%Y-%m-%d')
                dailyList.add((patientName, readingDate,))
            except Exception:
                continue

    # print(dailyList)
    # print(monthlyList)

    histogram_count = {}
    for patientName, readingDate in dailyList:
        try:
            histogram_count[patientName] += 1
        except KeyError:
            histogram_count[patientName] = 1
    logger.info(f"readings per Patient ID = {histogram_count}")

    for patientName, new_count in histogram_count.items():
        bFound = False
        for i, list_item in enumerate(monthly_list):
            patient = list_item['Patient Name']
            old_count = list_item['readings']
            if patientName == patient:
                monthly_list[i]['readings'] = new_count
                logger.info(f"Updated monthly list record {patient} from {old_count} to {new_count}")
                bFound = True
                break
        if not bFound:
            logger.warn(f"Patient '{patientName}' in daily report but not in master account list")
            sg.popup_ok(f"Please add patient '{patientName}' to the master account list.")

    window['-STATUS-'].update(f"Summary report updated.")
    window['-REPORT_TEXT_1-'].update('You may continue to add daily reports')
    return csv_file.name


@utils.log_wrap
def save_csv(window):
    logger.info(__name__ + ".save_csv()")
    logger.info("Saving the consolidated report.")

    monthly_list_summary = get_monthly_summary_csv_data()
    if len(monthly_list_summary) == 0:
        window['-STATUS-'].update('Summary report is empty. Nothing to save.')
        return

    save_folder = sg.popup_get_folder('Choose folder for saving merged report')
    if save_folder is None or save_folder == '':
        window['-STATUS-'].update("'Save CSV' operation canceled.")
        return

    global monthly_filename_remember
    dir_name = os.path.dirname(monthly_filename_remember)
    file_name = os.path.join(dir_name, 'account_summary.csv')

    with open(file_name, mode='w', newline='') as csv_out:
        fieldnames = ['Patient Name', 'Billing Code', 'Duration', 'readings']
        writer = csv.DictWriter(csv_out, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(monthly_list_summary)

    print(f"Summary report saved to '{file_name}'.  It has {len(monthly_list_summary)} rows.")
    print(f"Summary report saved at: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    file_name = os.path.join(dir_name, 'account_summary.log')
    with open(file_name, mode='w') as log_out:
        log_text = window['-LOG-'].get()
        log_out.writelines(log_text)
    
    window['-STATUS-'].update(f"'CSV and Log files saved in '{save_folder}'")

