'''
        CREATES SIMPLE GUI, FOR USER TO QUERY INTERNAL REDE (Z:/) TO GET INFO REGARDING CILS AND DATAFILES AVAILABLE
'''

import PySimpleGUI as sg
from files import df_db, get_cils
def turn_to_bool(s):
	s = str(s)
	return s.lower() in ['true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh', 'sim', 'ok', 'todos', 'vamos']



choices = list(set(df_db.gestao.tolist()))
choices = ['ALL'] + choices
layout = [
    [sg.Text('Please enter your preferences:')],
    [sg.Text('Gestão', size=(30, 1)), sg.Combo(choices, key='GESTAO', default_value='ALL')],

    [sg.Text('With details (gestão, tt and files)?', size=(30, 1)), 
    sg.Radio('Yes', "DETAIL", key="DETAIL-TRUE", default=True, enable_events=True), 
    sg.Radio('No', "DETAIL", key="DETAIL-FALSE", enable_events=True)],
    
       [sg.Text('Format to pandas df?', size=(30, 1)), 
    sg.Radio('Yes', "FORMAT", key="FORMAT-TRUE", default=True, enable_events=True), 
    sg.Radio('No', "FORMAT", key="FORMAT-FALSE", enable_events=True)],

      [sg.Text('Write to excel?', size=(30, 1)), 
    sg.Radio('Yes', "EXCEL", key="EXCEL-TRUE", default=True, enable_events=True), 
    sg.Radio('No', "EXCEL", key="EXCEL-FALSE", enable_events=True)],


    [sg.Button('Ok'), sg.Cancel()]
]

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

    elif event == 'Ok':
    	print(values)

    	data, msg = get_cils(gestao=values['GESTAO'], detail=values['DETAIL-TRUE'], format_detail=values['FORMAT-TRUE'], excel=values['EXCEL-TRUE'])

    	sg.popup_scrolled(f"{data}\n\n{msg}",  size=(100, 30))
    	break
    else:
    	break
window.close()