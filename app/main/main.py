import logging
import os
from re import MULTILINE
import PySimpleGUI as sg

import app.utils6L.utils6L as utils
from app.main.config import getargs, get_config, save_config, get_version

from app.main.data_ctlr import load_master_data, get_monthly_list_summary, load_daily_report, save_csv

logger_name = os.environ["LOGGER_NAME"]
logger = logging.getLogger(logger_name)

@utils.log_wrap
def menu():
    logger.info(__name__ + ".menu()")

    legal_fine_print = f'{get_version()} \
        \n\nThe eMARS SOFTWARE IS PROVIDED "AS IS" \
        \nSee the MIT Open Source License \
        \nhttps://opensource.org/licenses/MIT \
        \n\neMARS uses PySimpleGUI \
        \nVersion: {sg.version}\n'
    logger.info(legal_fine_print)

    args = getargs()
    config = get_config()

    sg.ChangeLookAndFeel(config["theme"]["lookandfeel"])
    # sg.SetOptions(element_padding=(0, 0), font=config["theme"]["font"], auto_size_text=True)
    sg.SetOptions(element_padding=(2, 2), font=12, auto_size_text=True)

    # ------ GUI Defintion ------ #

    menu_def = [
        ['File',
            ['Exit']],
        ['Build report',
            ['Load a daily report']],
        ['Help',
            ['Instructions', 'About...']],
    ]

    if args.index:
        report_visible_column_map = None
    else:
        report_visible_column_map = \
            [False, True, True, True, True]

    report_header = \
        ['Row', 'Patient Name    ', 'Billing Code', 'Duration', 'Readings']

    report_tab_layout = [
        [sg.Text(
            'Load the first daily file.',
            key='-REPORT_TEXT_1-')],
        [sg.Text(
            'The Readings data will change as the Reading History files are loaded.',  
            key='-REPORT_TEXT_2-')],
        [sg.Table(
            values=[],
            headings=report_header,
            max_col_width=70,
            auto_size_columns=True,
            visible_column_map=report_visible_column_map,
            display_row_numbers=False,
            justification='center',
            alternating_row_color='lightyellow',
            row_height=20,
            key='-DATA_TABLE-',
            tooltip='This table shows current number of readings for each patient')],
        [sg.Btn('Load Daily', key='-BTN_LOAD_DAILY-', pad=5, button_color=('white', 'blue3')),
            sg.Btn('Save CSV', key='-BTN_SAVE_CSV-', pad=5, button_color=('white', 'blue3'), visible=False),
            ]
        ]

    log_tab_layout = [[sg.Text('This tab will log the Account Summary Report creation actions.')],
        [sg.Multiline(size=(70,20), key="-LOG-", reroute_stdout=True, disabled=True)
    ]]

    layout = [[
        [sg.Menu(menu_def, key='-MENU-')],
        [sg.Text(
            f"Load Master account table", relief=sg.RELIEF_SUNKEN,
            size=(70, 1), pad=(0, 3), key='-STATUS-')],
        sg.TabGroup([[
            sg.Tab('Create Report', report_tab_layout),
            sg.Tab('Log', log_tab_layout)
            ]], tab_background_color='LightBlue', selected_background_color='White', key='-TAB-')
    ]]


    window = sg.Window(
        'Executive Monthly Account Report Summary (eMARS)',
        layout, default_element_size=(40, 1),
        resizable=True, finalize=True)
    load_master_data(window)

    # --- Menu Loop --- #
    while True:
        refresh_table_info(window)
        event, values = window.read()
        logger.info(f"Menu event, values = '{event}', {values}")
        if event == sg.WIN_CLOSED or event == 'Exit' or event is None:
            break
        elif event == 'Load a daily report' or event == '-BTN_LOAD_DAILY-':
            load_daily_report(window)
            window['-BTN_SAVE_CSV-'].update(visible=True)
        elif event == 'Save CSV' or event == '-BTN_SAVE_CSV-':
            save_csv(window)
        elif event == 'About...':
            sg.popup(legal_fine_print, title="About eMARS")

    # All done - exiting
    save_config(config)
    window.close()


@utils.log_wrap
def refresh_table_info(window):
    logger.info(__name__ + ".refresh_table_info()")

    monthly_list_summary = get_monthly_list_summary()
    logger.info(f"number of readings: {len(monthly_list_summary)}")
    if len(monthly_list_summary) > 0:
        window['-DATA_TABLE-'].update(monthly_list_summary)
