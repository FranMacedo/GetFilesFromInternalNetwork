'''
        PROMPT USER FOR INPUT IN CMD, TO QUERY INTERNAL REDE (Z:/) TO GET INFO REGARDING CILS AND DATAFILES AVAILABLE
'''

def turn_to_bool(s):
	s = str(s)
	return s.lower() in ['true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh', 'sim', 'ok', 'todos', 'vamos']

print(
'''
######################################################################
######################################################################
###################### CHECK FILES FROM REDE #########################
######################################################################
######################################################################
'''
)

gestao='ALL'
detail=False
format_detail=True
excel=True

print("Press ENTER if you don't want to specify a variable (and automatically choose default value)")
gestao = input('gestao ?[default="ALL"] >>>')
gestao = str(gestao)
if gestao == '':
	gestao = 'ALL'

detail_in = input('more detailed info? [default=False] >>>')
if detail_in != '':
	detail = turn_to_bool(detail_in)

if detail:
	format_detail_in = input('format to a pandas df? [default=True] >>>')
	if format_detail_in != '':
		format_detail = turn_to_bool(format_detail_in)

	if format_detail:
		excel_in = input('write to excel file? [default=True] >>>')
		if excel_in != '':
			excel = turn_to_bool(excel_in)
	else:
		excel=False
else:
	format_detail=False
	excel=False

print(f'''
-gestao: {gestao}
-get detail info: {detail}
-format to pandas df: {format_detail}
-write to excel: {excel}
''')

print('Trying to colect info....')
from files import get_cils
data = get_cils(gestao=gestao, detail=detail, format_detail=format_detail, excel=excel)

if not excel:
	print(data)