import logging
import os

import app.utils6L.utils6L as utils
from app.main.config import getargs, get_config, save_config, get_version
import PySimpleGUI as sg

# from app.main.address_ctlr import link_address_to_company, get_address_list
# from app.main.address_ctlr import delete_address
# from app.main.company_ctlr import get_company_address_table_data, get_company_list
# from app.main.company_ctlr import company_details, get_company_selection
# from app.main.company_ctlr import add_new_company, edit_company, delete_company
# from app.main.job_ctlr import add_job, get_job_data

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

    # args = getargs()
    config = get_config()

    sg.ChangeLookAndFeel(config["theme"]["lookandfeel"])
    # sg.SetOptions(element_padding=(0, 0), font=config["theme"]["font"], auto_size_text=True)
    sg.SetOptions(element_padding=(0, 0), font=12, auto_size_text=True)

    # ------ GUI Defintion ------ #

    # company_submenu = [
    #     'Add new company',
    #     'Get company selection',
    #     'Delete company',
    #     'Edit company']
    report_submenu = [
        'Load Account Master',
        'Load a daily report']

    menu_def = [
        ['File',
            ['Choose data folder', 'Save', 'Properties', 'Exit']],
        ['Build report',
            ['Load reports', report_submenu,
                'Create Excel spreadsheet', 'create_spreadsheet']],
        ['Help',
            ['Instructions', 'About...']],
    ]

    # if args.index:
    #     company_address_visible_column_map = None
    #     job_action_visible_column_map = None
    # else:
    #     company_address_visible_column_map = \
    #         [False, True, False, True, True, True, True, True]
    #     job_action_visible_column_map = \
    #         [False, True, True, True, True, True, True, True, True, True]

    # company_address_header = \
    #     ['Id', 'Name', 'Id', 'Street', 'City', 'State', 'Zip', 'Jobs']

    # company_address_data = get_company_address_table_data()

    # company_tab_layout = [
    #     [sg.CB(
    #         'Address', default=True,
    #         enable_events=True, key='-CB_ADDRESS-')],
    #     [sg.Text(
    #         120*' ',
    #         key='-NBR_COMPANIES-')],
    #     [sg.Table(
    #         values=company_address_data,
    #         headings=company_address_header,
    #         right_click_menu=['', company_submenu],
    #         max_col_width=25,
    #         auto_size_columns=True,
    #         visible_column_map=company_address_visible_column_map,
    #         display_row_numbers=False,
    #         justification='left',
    #         alternating_row_color='lightyellow',
    #         row_height=20,
    #         key='-COMPANY_TABLE-', enable_events=True,
    #         tooltip='This table shows company and address information')]
    # ]

    networking_tab_layout = [[sg.Text('This is inside the networking tab')]]

    metrics_tab_layout = [[sg.Text('This is inside the metrics tab')]]

    layout = [[
        [sg.Menu(menu_def, key='-MENU-')],
        [sg.Text(
            f"Status: Normal", relief=sg.RELIEF_SUNKEN,
            size=(55, 1), pad=(0, 3), key='-STATUS-')],
        sg.TabGroup([[
            sg.Tab('Networking', networking_tab_layout),
            sg.Tab('Metrics', metrics_tab_layout)
            ]], tab_background_color='LightBlue', selected_background_color='White', key='-TAB-')
    ]]

    window = sg.Window(
        'Executive Monthly Account Report Summary (eMARS)',
        layout, default_element_size=(40, 1),
        resizable=True, finalize=True)

    # --- Menu Loop --- #
    while True:
        refresh_all_table_info(window)
        event, values = window.read()
        logger.info(f"Menu event, values = '{event}', {values}")
        if event == sg.WIN_CLOSED or event == 'Exit' or event is None:
            break
        # elif event == 'Delete address':
        #     delete_address(window, values['-LB_Address-'])
        # elif event == 'Add New Job':
        #     add_job()
        elif event == 'About...':
            sg.popup(legal_fine_print, title="About eMARS")

    # All done - exiting
    save_config(config)
    window.close()


@utils.log_wrap
def refresh_all_table_info(window):
    logger.info(__name__ + ".refresh_all_table_info()")
