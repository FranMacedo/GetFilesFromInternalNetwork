'''
		FUNCTIONS TO RUN TO COLLECT INFORMATION FROM LOCAL NETWORK ON DATAFILES AVAILABLE
'''

from my_functions import connect_db, find_between, find_between_r
from glob import glob
import os
import pandas as pd
from datetime import datetime as dt
import xlsxwriter
from get_data import get_cil_data
from env_vars import is_fixo

if is_fixo:
    try:
        df_db = connect_db('energia', False)
    except Exception as e:
        import PySimpleGUI as sg

        print(f"Ocurreu um erro a tentar ligar à rede...:{e}\n\nTente Novamente mais tarde, depois de a ligação estar estabelecida.")
        sg.PopupTimed('Não é possível ligar à rede Z:...',
                      'Garanta que há uma conexão primeiro!',
                      title="ERROR Z:", auto_close_duration=10)
else:
    try:
        df_db = connect_db('energia', True)
    except Exception as e:
        import PySimpleGUI as sg

        print(f"Ocurreu um erro a aceder à base de dados local..:{e}\n\nVerifique que esta existe e está na pasta pretendida.")
        sg.PopupTimed('Ocurreu um erro a aceder à base de dados local...',
                      'Verifique que esta existe e está na pasta pretendida!',
                      title="ERROR DB", auto_close_duration=10)

db_dir = r'Z:\DATABASE'
energy_dir = os.path.join(db_dir, 'ENERGIA')
water_dir = os.path.join(db_dir, 'AGUA')
data_folder = 'DATAFILES'


def get_gestao(cil):
    '''
            returns string indicating management (gestao) of a specific cil
    '''

    try:
        return df_db.loc[df_db.cil == int(cil), 'gestao'].iloc[0]
    except IndexError:
        print(f'->{cil} sem gestao definida!')
        return None


def get_tt(cil_dir):
    '''
            returns string indicating tt (abastecimento) of a specific cil - 'BTE', 'MT', 'AT' or 'BTN'
    '''
    tt_cil = find_between_r(cil_dir, data_folder, '')

    return find_between(tt_cil, '\\', '\\')


def get_all_files_path(is_energy=True):
    '''
            returns all files of either energy folder or water folder
    '''
    if is_energy:
        files_dir = os.path.join(energy_dir, data_folder)
    else:
        files_dir = os.path.join(water_dir, data_folder)

    return glob(os.path.join(files_dir, '*/**'))


def get_files_from_dir(dir_path):
    '''
            returns a list of all files in any dir
    '''
    print(f'checking path {dir_path}...')
    files = os.listdir(dir_path)
    return files


def get_cils_dates(cil_dir):
    '''
            returns dates from files in common format "{CIL}_{YEARMONTH}.xlsx" (ex: 3874085_202004.xlsx)
    '''
    files = get_files_from_dir(cil_dir)
    files_dates = [find_between(c, '_', '.') for c in files]
    files_dates.sort()
    return files_dates


def write_to_excel(df, gestao=False):
    '''
            Writes df (with info of what dates each cil has) to excel, in 'files folder'.
            Creates 'files' folder if it doesn't exist.
            Conditional formatting to paint red if dates are not in rede.
    '''

    current_dir = os.getcwd()
    today = dt.now().strftime('%Y_%m_%d')
    files_dir = os.path.join(current_dir, 'files')
    if not os.path.exists(files_dir):
        os.mkdir(files_dir)
    if gestao:
        f_name = f'df_{gestao}_{today}'
    else:
        f_name = f'df_{today}'

    file_dir = os.path.join(files_dir, f'{f_name}.xlsx')

    if os.path.exists(file_dir):
        i = 1
        while True:
            file_dir = os.path.join(files_dir, f'{f_name}_({i}).xlsx')
            if not os.path.exists(file_dir):
                break
            i += 1

    writer = pd.ExcelWriter(file_dir, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Sheet1')
    workbook = writer.book

    format1 = workbook.add_format({'bg_color': '#FFC7CE',
                                   'font_color': '#9C0006'})

    # format2 = workbook.add_format({'bg_color': '#C6EFCE',
 #                               'font_color': '#006100'})

    worksheet = writer.sheets['Sheet1']
    start_row = 1
    start_col = 1
    end_row = df.shape[0]
    end_col = df.shape[1]
    worksheet.conditional_format(start_row, start_col, end_row, end_col, {
                                 'type': 'cell', 'criteria': '=', 'value': 'FALSE', 'format': format1})
    try:
        writer.save()
    except Exception as e:
        print(f'something went wrong: {e}')
        return
    print(f'''


					!!!!!! SUCCESS !!!!!
	data writen in {file_dir}


		'''
          )
    return f'data writen in {file_dir}'


def get_cils(gestao='ALL', cils_or_cpes=None, detail=False, format_detail=True, excel=True):
    """
            returns (ENERGIA) info from Rede (Z:). Can be df, list or dict.
            if gestao != ALL => same thing, only for specific management/gestao;
            if detail=True => dict with gestao, abastecimento, and datafiles available;
            if format_detail =True => pandas df with same info as before stage;
            if excel =True => same info as format_detail, but also writes it in excel file, in 'files' folder;
    """
    print('\n\ngestao: ', gestao, '\n\n')
    all_files = get_all_files_path(True)
    all_cils = [find_between_r(f, '\\', '') for f in all_files]
    if not gestao:

        cils_gestao = [df_db.loc[df_db.cpe == str(c), 'cil'].values[0]
                       if 'PT' in str(c) else int(c) for c in cils_or_cpes]
        all_cils = [str(c) for c in cils_gestao if str(c) in all_cils]
        all_files = [{'cil': find_between_r(a, '\\', ''), 'dir': a}
                     for a in all_files if find_between_r(a, '\\', '') in all_cils]
    elif gestao.upper() not in ['', 'ALL', 'TODOS', 'TODAS', 'TODO', 'TODA']:
        has_gestao = True
        cils_gestao = df_db.loc[df_db.gestao == gestao, 'cil'].tolist()
        if not cils_gestao:

            cils_gestao = df_db.loc[df_db.gestao == gestao.upper(), 'cil'].tolist()
            if not cils_gestao:
                msg = f'{gestao} não foi detectada como gestao válida na nossa db...'
                print(msg)
                return None, msg

            gestao = gestao.upper()
        all_cils = [str(c) for c in cils_gestao if str(c) in all_cils]
        all_files = [{'cil': find_between_r(a, '\\', ''), 'dir': a}
                     for a in all_files if find_between_r(a, '\\', '') in all_cils]

        if not all_cils:
            msg = f'{gestao} sem datafiles na db...'
            print(msg)
            return None, msg
    else:
        gestao = False

    if not detail:
        return all_cils, ''

    if detail:
        all_cils_detail = {cil_obj['cil']: {'gestao': get_gestao(cil_obj['cil']), 'abastecimento': get_tt(
            cil_obj['dir']), 'all_dates': get_cils_dates(cil_obj['dir'])} for cil_obj in all_files}
        if format_detail:
            all_dates = [v['all_dates'] for k, v in all_cils_detail.items()]
            all_dates = [a for sub in all_dates for a in sub]
            all_dates = list(set(all_dates))
            all_dates.sort()
            df = pd.DataFrame.from_dict(all_cils_detail).transpose()
            print(df)
            df.to_csv('df.csv')
            df = df.reindex(df.columns.tolist() + all_dates, axis=1)
            d_cil_cpe = df_db[['cil', 'cpe']].copy()
            d_cil_cpe['cil'] = d_cil_cpe['cil'].map(str)
            df = pd.merge(df, d_cil_cpe, left_index=True, right_on='cil', how='left')
            cols = df.columns.tolist()
            cols = cols[-2:] + cols[:-2]
            df = df[cols]
            df[all_dates] = False
            for i, r in df.iterrows():
                cil_dates = df.loc[i, 'all_dates']
                for d in cil_dates:
                    df.loc[i, d] = True

            if excel:
                msg = write_to_excel(df, gestao)
                return df, msg
            return df, ''
        return all_cils_detail, ''

    return None, 'ocorreu algum erro!'


def get_telecontagem(ym, gestao=None, cils_or_cpes=None):
    if not gestao and not cils_or_cpes:
        print('É necessario pelo menos 1 cpe selecionado..')
        return 'ERRO', 'É necessario pelo menos 1 cpe selecionado..'

    if gestao:
        if not isinstance(gestao, str):
            print('Gestão está no formato errado... Tem que ser texto/string!')
            return 'ERRO', 'Gestão está no formato errado... Tem que ser texto/string!'
        df = df_db.loc[df_db.gestao == gestao]
    elif cils_or_cpes:
        if isinstance(cils_or_cpes, str):
            cils_or_cpes = [cils_or_cpes]
        cpes = [c if 'PT' in str(c) else df_db.loc[df_db.cil == int(c), 'cpe'].values[0] for c in cils_or_cpes]
        df = df_db.loc[df_db.cpe.isin(cpes)]
    current_dir = os.getcwd()
    files_dir = os.path.join(current_dir, 'telecontagem')
    if not os.path.exists(files_dir):
        os.mkdir(files_dir)

    for i, row in df.iterrows():

        df, result = get_cil_data(row.cil, row.abastecimento, ym)
        if result:
            df.to_excel(os.path.join(files_dir, f'{row.cpe}.xlsx'))

    return 'DONE', 'Verifique a pasta telecontagem'
