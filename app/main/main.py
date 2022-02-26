import logging
import os
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
        ['Row', 'Patient ID', 'Billing Code', 'Duration', 'Readings']

    report_tab_layout = [
        [sg.Text(
            'Load the first daily file.',
            key='-REPORT_TEXT_1')],
        [sg.Text(
            'The data will change as the daily files are loaded.',  
            key='-REPORT_TEXT_2')],
        [sg.Table(
            values=[],
            headings=report_header,
            max_col_width=25,
            auto_size_columns=True,
            visible_column_map=report_visible_column_map,
            display_row_numbers=False,
            justification='center',
            alternating_row_color='lightyellow',
            row_height=20,
            key='-DATA_TABLE-',
            tooltip='This table shows current number of readings for each patient')],
        [sg.Btn('Load Daily', key='-BTN_LOAD_DAILY-', pad=5, button_color=('white', 'blue3')),
            sg.Btn('Save CSV', key='-BTN_SAVE_CSV-', pad=5, disabled=True, button_color=('white', 'blue3'), 
                disabled_button_color=('white', 'grey')),
            ],
        ]

    # metrics_tab_layout = [[sg.Text('This is inside the metrics tab')]]

    layout = [[
        [sg.Menu(menu_def, key='-MENU-')],
        [sg.Text(
            f"Status: Master account table loaded", relief=sg.RELIEF_SUNKEN,
            size=(55, 1), pad=(0, 3), key='-STATUS-')],
        sg.TabGroup([[
            sg.Tab('Create Report', report_tab_layout),
            # sg.Tab('Metrics', metrics_tab_layout)
            ]], tab_background_color='LightBlue', selected_background_color='White', key='-TAB-')
    ]]

    load_master_data()

    window = sg.Window(
        'Executive Monthly Account Report Summary (eMARS)',
        layout, default_element_size=(40, 1),
        resizable=True, finalize=True)

    # --- Menu Loop --- #
    while True:
        refresh_table_info(window)
        event, values = window.read()
        logger.info(f"Menu event, values = '{event}', {values}")
        if event == sg.WIN_CLOSED or event == 'Exit' or event is None:
            break
        elif event == 'Load a daily report' or event == '-BTN_LOAD_DAILY-':
            filename = load_daily_report()
            if filename == 'used':
                window['-STATUS-'].update(f"File has already been loaded. Please try again.")
            else:
                window['-STATUS-'].update(f"Daily report '{filename}' was loaded")
                window['-BTN_SAVE_CSV-'].update(disabled=False)
            window['-REPORT_TEXT_1'].update('You may load addition daily reports')
        elif event == 'Save CSV' or event == '-BTN_SAVE_CSV-':
            save_csv()
        elif event == 'About...':
            sg.popup(legal_fine_print, title="About eMARS")

    # All done - exiting
    save_config(config)
    window.close()


@utils.log_wrap
def refresh_table_info(window):
    logger.info(__name__ + ".refresh_table_info()")

    monthly_list_summary = get_monthly_list_summary()
    logger.info(f"number of non-zero readings: {len(monthly_list_summary)}")
    if len(monthly_list_summary) > 0:
        window['-DATA_TABLE-'].update(monthly_list_summary)
