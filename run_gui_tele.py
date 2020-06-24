'''
        CREATES SIMPLE GUI, FOR USER TO QUERY INTERNAL REDE (Z:/) TO GET INFO REGARDING CILS AND DATAFILES AVAILABLE
'''

import PySimpleGUI as sg
from files import df_db, get_telecontagem
from datetime import datetime as dt
import pandas as pd


def turn_to_bool(s):
    s = str(s)
    return s.lower() in ['true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh', 'sim', 'ok', 'todos', 'vamos']


choices = list(set(df_db.gestao.tolist()))
layout = [
    [sg.Text('Please enter your preferences:')],
    [sg.Text('Gestão', size=(30, 1)), sg.Combo(choices, key='GESTAO', default_value='None', enable_events=True)],
    [sg.Text('CPEs ou CILs', size=(20, 1)), sg.InputText(key='CILS-OR-CPES', size=(60, 3), enable_events=True)],

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


    [sg.Button('Ok'), sg.Cancel()]
]

window = sg.Window('Get Info from Rede Z:/', layout)
while True:                  # the event loop
    event, values = window.read()
    if event == 'DATE-BEGIN':
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

    elif event == 'GESTAO':
        window['CILS-OR-CPES'].update('')

    elif event == 'CILS-OR-CPES':
        window['GESTAO'].update(value='None')

    elif event == 'Ok':
        print(values)
        if (values['GESTAO'] == 'None' or values['GESTAO'] == None) and values['CILS-OR-CPES'] == '':
            sg.PopupTimed('A Gestão e os CPEs não podem estar ambos vazios!', title='ERRO!', auto_close_duration=10)
        else:
            if values['GESTAO'] == 'None':
                values['GESTAO'] = None
            if values['CILS-OR-CPES'] == '':
                cils_or_cpes = None
            else:
                cils_or_cpes = list(values['CILS-OR-CPES'].split(','))
                cils_or_cpes = [c.strip(' \t,.*#\n ') for c in cils_or_cpes]
            print(cils_or_cpes)
            print(values['DATE-BEGIN'])
            print(pd.to_datetime(values['DATE-BEGIN']))
            ym = pd.date_range(pd.to_datetime(values['DATE-BEGIN']), pd.to_datetime(values['DATE-END']), freq='M')
            ym = [y.strftime('%Y%m') for y in ym]

            data, msg = get_telecontagem(ym, gestao=values['GESTAO'], cils_or_cpes=cils_or_cpes)
            sg.popup_scrolled(f"{data}\n\n{msg}",  size=(100, 30))
            break
    else:
        break
window.close()
