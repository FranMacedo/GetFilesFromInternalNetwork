'''
        CREATES SIMPLE GUI, FOR USER TO QUERY INTERNAL REDE (Z:/) TO GET INFO REGARDING CILS AND DATAFILES AVAILABLE
'''

import PySimpleGUI as sg
from files import df_db, get_cils, get_telecontagem
from datetime import datetime as dt
import pandas as pd

from reports import create_reports

is_tele = False
is_info = False
is_report = False

def turn_to_bool(s):
    s = str(s)
    return s.lower() in ['true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh', 'sim', 'ok', 'todos', 'vamos']



def validate_gestao_cpes(gestao, cils_or_cpes):
    print(gestao)   
    if gestao == 'None' and not cils_or_cpes:
        sg.PopupTimed('A Gestão e os CPEs não podem estar ambos vazios!', title='ERRO!', auto_close_duration=10)
        return False
    if gestao not in df_db.gestao.tolist() and gestao != 'None':
        sg.PopupTimed('Gestão Inválida!', title='ERRO!', auto_close_duration=10)
        return False

    return True

choices = list(set(df_db.gestao.tolist()))
choices = ['ALL'] + choices
tab_info = [
    [sg.Text('Get Information About available files in local Rede (Z:)')],
    [sg.Text('Gestão', size=(30, 1)), sg.Combo(choices, key='GESTAO', default_value='None', enable_events=True)],
    [sg.Text('CPEs ou CILs', size=(20, 1)), sg.InputText(key='CILS-OR-CPES', size=(60, 3), enable_events=True)],

    [sg.Text('With details (gestão, tt and files)?', size=(30, 1)),
     sg.Radio('Yes', "DETAIL", key="DETAIL-TRUE", default=True, enable_events=True),
     sg.Radio('No', "DETAIL", key="DETAIL-FALSE", enable_events=True)],

    [sg.Text('Format to pandas df?', size=(30, 1)),
        sg.Radio('Yes', "FORMAT", key="FORMAT-TRUE", default=True, enable_events=True),
        sg.Radio('No', "FORMAT", key="FORMAT-FALSE", enable_events=True)],

    [sg.Text('Write to excel?', size=(30, 1)),
     sg.Radio('Yes', "EXCEL", key="EXCEL-TRUE", default=True, enable_events=True),
     sg.Radio('No', "EXCEL", key="EXCEL-FALSE", enable_events=True)],


    [sg.Button('Get Info', key='OK_INFO')]
]

tab_tele = [
    [sg.Text('Get Telecontagem Files from local Rede (Z:)')],
    [sg.Text('Gestão', size=(30, 1)), sg.Combo(choices, key='GESTAO_TELE', default_value='None', enable_events=True)],
    [sg.Text('CPEs ou CILs', size=(20, 1)), sg.InputText(key='CILS-OR-CPES_TELE', size=(60, 3), enable_events=True)],

    [
        sg.Text('', size=(20, 1)),
        sg.Text('Data de Inicio', size=(20, 1), justification='center'),
        sg.Text('Data de Fim', size=(20, 1), justification='center')
    ],

    [
        sg.Text('Intervalo de Datas', size=(20, 1)),
        sg.In('2013-01', key='DATE-BEGIN', enable_events=True, visible=False),
        sg.CalendarButton('2013-01', target='DATE-BEGIN', pad=None,
                          button_color=('red', 'white'), key='DATE-BEGIN-BTN', format=('%Y-%m'), size=(20, 1)),
        sg.In(dt.now().date().strftime('%Y-%m'), key='DATE-END', enable_events=True, visible=False),
        sg.CalendarButton(dt.now().date().strftime('%Y-%m'), target='DATE-END', pad=None,
                          button_color=('red', 'white'), key='DATE-END-BTN', format=('%Y-%m'), size=(20, 1))
    ],

    [sg.Button('Get Telecontagem', key='OK_TELE')]
]

tab_report = [
    [sg.Text('Create Reports')],
    [sg.Text('Gestão', size=(30, 1)), sg.Combo(choices, key='GESTAO_REPORT', default_value='None', enable_events=True)],
    [sg.Text('CPEs ou CILs', size=(20, 1)), sg.InputText(key='CILS-OR-CPES_REPORT', size=(60, 3), enable_events=True)],
    [sg.Text('Months - format must be year-month (ex: 2020-04, 2020-05)', size=(20, 1)), sg.InputText(key='REPORT-DATES', size=(60, 3))],

    [sg.Button('Create Reports', key='OK_REPORT')]
]


layout = [[sg.TabGroup([
                        [sg.Tab('Telecontagem', tab_tele, tooltip='gets Telecontagem data from Rede Z:'), 
                        sg.Tab('Information', tab_info, tooltip='Gathers Info from Rede Z:'),
                        sg.Tab('Report', tab_report, tooltip='Creates reports with telecontagem from Rede Z:'),
                        ]
        ])],    
        [sg.Text('', size=(70, 2)), sg.Cancel(button_color=('black', 'red'))]]    

window = sg.Window('Get Info from Rede Z:/', layout)
while True:                  # the event loop
    event, values = window.read()

    if event in ["DETAIL-TRUE", "DETAIL-FALSE"]:
        with_detail = turn_to_bool(event.split('-')[1])

        if not with_detail:
            window['FORMAT-TRUE'].update(value=False)
            window['FORMAT-FALSE'].update(value=True)
            window['EXCEL-TRUE'].update(value=False)
            window['EXCEL-FALSE'].update(value=True)

    elif event in ["FORMAT-TRUE", "FORMAT-FALSE", "EXCEL-TRUE", "EXCEL-FALSE"]:
        with_format = turn_to_bool(event.split('-')[1])

        if with_format:
            window['DETAIL-TRUE'].update(value=True)
            window['DETAIL-FALSE'].update(value=False)

    elif event == 'GESTAO':
        window['CILS-OR-CPES'].update('')

    elif event == 'CILS-OR-CPES':
        window['GESTAO'].update(value='None')

    elif event == 'OK_INFO':
        print(values)
        res = validate_gestao_cpes(values['GESTAO'], values['CILS-OR-CPES'])

        if res:
            if values['GESTAO'] == 'None':
                values['GESTAO'] = None
            if values['CILS-OR-CPES'] == '':
                cils_or_cpes = None
            else:
                cils_or_cpes = list(values['CILS-OR-CPES'].split(','))
                cils_or_cpes = [c.strip(' \t,.*#\n ') for c in cils_or_cpes]
            print(cils_or_cpes)


            is_info=True
            sg.PopupTimed('A informação será reunida em breve...', title='Download Ready', auto_close_duration=3)
            break

    elif event == 'DATE-BEGIN':
        if values['DATE-END'] and pd.to_datetime(values['DATE-END']) < pd.to_datetime(values['DATE-BEGIN']):
            sg.PopupTimed('A data de inicio não pode ser depois da data de fim!',
                          title='Erro nas datas!', auto_close_duration=3)
        else:
            window['DATE-BEGIN-BTN'].update(values['DATE-BEGIN'])
    elif event == 'DATE-END':

        print(pd.to_datetime(values['DATE-END']))
        if values['DATE-BEGIN'] and pd.to_datetime(values['DATE-END']) < pd.to_datetime(values['DATE-BEGIN']):
            sg.PopupTimed('A data de fim não pode ser antes da data de inicio!',
                          title='Erro nas datas!', auto_close_duration=3)
        else:
            window['DATE-END-BTN'].update(values['DATE-END'])

    elif event == 'GESTAO_TELE':
        window['CILS-OR-CPES_TELE'].update('')

    elif event == 'CILS-OR-CPES_TELE':
        window['GESTAO_TELE'].update(value='None')

    elif event == 'GESTAO_REPORT':
        window['CILS-OR-CPES_REPORT'].update('')

    elif event == 'CILS-OR-CPES_REPORT':
        window['GESTAO_REPORT'].update(value='None')

    elif event == 'OK_TELE':
        print(values)
        res = validate_gestao_cpes(values['GESTAO_TELE'], values['CILS-OR-CPES_TELE'])

        if res:

            if values['GESTAO_TELE'] == 'None':
                values['GESTAO_TELE'] = None
            if values['CILS-OR-CPES_TELE'] == '':
                cils_or_cpes = None
            else:
                cils_or_cpes = list(values['CILS-OR-CPES_TELE'].split(','))
                cils_or_cpes = [c.strip(' \t,.*#\n ') for c in cils_or_cpes]
            print(cils_or_cpes)
            print(values['DATE-BEGIN'])
            print(pd.to_datetime(values['DATE-BEGIN']))
            ym = pd.date_range(pd.to_datetime(values['DATE-BEGIN']), pd.to_datetime(values['DATE-END']), freq='M')
            ym = [y.strftime('%Y%m') for y in ym]

            is_tele=True        
            sg.PopupTimed('A Telecontagem será reunida em breve...', title='Download Ready', auto_close_duration=3)
            break
    elif event == 'OK_REPORT':
        print(values)
        res = validate_gestao_cpes(values['GESTAO_REPORT'], values['CILS-OR-CPES_REPORT'])

        if res:
            if values['GESTAO_REPORT'] not in ['None', None]:
                cils = df_db.loc[df_db.gestao == values['GESTAO_REPORT'], 'cil'].tolist()
                cils = [str(c) for c in cils]
            else:

                cils_or_cpes = list(values['CILS-OR-CPES_REPORT'].split(','))
                cils_or_cpes = [c.strip(' \t,.*#\n ') for c in cils_or_cpes]
                cils = [df_db.loc[df_db.cpe == c, 'cil'].values[0] if 'PT' in str(c) else c for c in cils_or_cpes]
                cils = [str(c) for c in cils]

                if ',' in values['REPORT-DATES']:
                    dates = list(values['REPORT-DATES'].split(','))

                if ';' in values['REPORT-DATES']:
                    dates = list(values['REPORT-DATES'].split(';'))
                else:
                    dates = list(values['REPORT-DATES'].split())

                dates = [d.strip(' \t,.*#\n ') for d in dates]
            is_report=True
            break


    else:
        break
window.close()

if is_info:
    data, msg = get_cils(gestao=values['GESTAO'], cils_or_cpes=cils_or_cpes,
        detail=values['DETAIL-TRUE'], format_detail=values['FORMAT-TRUE'], excel=values['EXCEL-TRUE'])
    sg.popup_scrolled(f"{data}\n\n{msg}",  size=(100, 30), auto_close_duration=30, title='Info gathered')

if is_tele:
    print(cils_or_cpes)
    data, msg = get_telecontagem(ym, gestao=values['GESTAO_TELE'], cils_or_cpes=cils_or_cpes)
    sg.popup_scrolled(f"{data}\n\n{msg}",  size=(100, 30), auto_close_duration=30, title='Telecontagem gathered')

if is_report:
    print(dates)
    print(cils)
    for c in cils:
        for d in dates:
            res, msg  = create_reports(['3874085'], ['2020-04'])
            print(res)
            print(msg)