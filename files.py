'''
		FUNCTIONS TO RUN TO COLLECT INFORMATION FROM LOCAL NETWORK ON DATAFILES AVAILABLE
'''

from my_functions import connect_db, find_between, find_between_r
from glob import glob
import os
import pandas as pd
from datetime import datetime as dt
import xlsxwriter
df_db = connect_db('energia', False)
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
			i+=1

	writer = pd.ExcelWriter(file_dir, engine='xlsxwriter')
	df.to_excel(writer, sheet_name='Sheet1')
	workbook  = writer.book

	format1 = workbook.add_format({'bg_color': '#FFC7CE',
                               'font_color': '#9C0006'})

	# format2 = workbook.add_format({'bg_color': '#C6EFCE',
 #                               'font_color': '#006100'})

	worksheet = writer.sheets['Sheet1']
	start_row = 1
	start_col = 1
	end_row = df.shape[0]
	end_col = df.shape[1]
	worksheet.conditional_format(start_row, start_col, end_row, end_col, {'type':'cell', 'criteria':'=', 'value':'FALSE', 'format':format1})
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


def get_cils( gestao='ALL', detail=False, format_detail=True, excel=True):

	"""
		returns (ENERGIA) info from Rede (Z:). Can be df, list or dict.
		if gestao != ALL => same thing, only for specific management/gestao;
		if detail=True => dict with gestao, abastecimento, and datafiles available;
		if format_detail =True => pandas df with same info as before stage;
		if excel =True => same info as format_detail, but also writes it in excel file, in 'files' folder;
	"""

	all_files = get_all_files_path(True)
	all_cils = [find_between_r(f, '\\', '') for f in all_files]

	if gestao.upper() not in ['', 'ALL', 'TODOS', 'TODAS', 'TODO', 'TODA']:
		has_gestao=True
		cils_gestao = df_db.loc[df_db.gestao == gestao, 'cil'].tolist()
		if not cils_gestao:

			cils_gestao = df_db.loc[df_db.gestao == gestao.upper(), 'cil'].tolist()
			if not cils_gestao:
				msg = f'{gestao} não foi detectada como gestao válida na nossa db...'
				print(msg)
				return None, msg
				
			gestao=gestao.upper()
		all_cils = [str(c) for c in cils_gestao if str(c) in all_cils]
		all_files = [a for a in all_files if find_between_r(a, '\\', '') in all_cils]

		if not all_cils:
			msg = f'{gestao} sem datafiles na db...'
			print(msg)
			return None, msg
	else:
		gestao=False

	if not detail:
		return all_cils, ''

	if detail:
		all_cils_detail = {cil: {'gestao':get_gestao(cil), 'abastecimento':get_tt(cil_dir), 'all_dates': get_cils_dates(cil_dir)} for cil, cil_dir in zip(all_cils, all_files)}
		if format_detail:
			all_dates = [v['all_dates'] for k,v in all_cils_detail.items()]
			all_dates = [a for sub in all_dates for a in sub]
			all_dates = list(set(all_dates))
			all_dates.sort()
			df =  pd.DataFrame.from_dict(all_cils_detail).transpose()
			df = df.reindex(df.columns.tolist() + all_dates, axis=1)
			df[all_dates]=False
			for i,r in df.iterrows():
				cil_dates = df.loc[i, 'all_dates']
				for d in cil_dates:
					df.loc[i, d] = True
			if excel:
				msg = write_to_excel(df, gestao)
				return df, msg
			return df, ''
		return all_cils_detail, ''

	return None, 'ocorreu algum erro!'


