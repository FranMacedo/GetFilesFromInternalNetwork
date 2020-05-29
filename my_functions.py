'''
        FUNCTIONS USED ALLOOOOOOOOOVER THE PLACE
'''

# import pyodbc
import pandas as pd
import ctypes

MessageBox = ctypes.windll.user32.MessageBoxW
import time
import sys
from datetime import timedelta, date, datetime
import os
import calendar
import numpy as np
# import pyodbc


import sqlite3
from sqlite3 import Error
#
#

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn



def connect_db(table_name, local=True):
    """ read table from db_file as a dataframe
    :param db_file: database file
    :param table_name: table name
    :return: pandas data frame
    """
    if local:
        db_file = "C:/Users/Vasco Abreu - PC/Desktop/database/instalacoes.db"
    else:
        db_file = "Z:/DATABASE/instalacoes.db"
    conn = create_connection(db_file)
    df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    return df

# OLD
# def conect_db(agua_ou_energia, local=False):
#     """
#     Conecta a base de dados de agua ou à base de dados de energia
#     se local for True (por defeito é False) vai ler a base de dados ao desktop, que é mais rapido.
#     :param agua_ou_energia: string que indique se é água ou energia
#     :return: dataframe com os dados referentes às instalações
#     """
#     if local:
#         path = 'C:\\Users\\Vasco Abreu - PC\\Desktop'
#     else:
#         path = 'Z:\\DATABASE'
#     if agua_ou_energia.upper() in ['AGUA', 'WATER', 'ÁGUA', 'AGU', 'A']:
#         path_agua = path + '\\AGUA\\Instalacoes_waterbeep.accdb;'
#         conn_str = (
#                 r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
#                 r'DBQ=' + path_agua)
#     else:
#         path_energia = path + '\\ENERGIA\\Tabeladeinstalacoes.accdb;'
#
#         conn_str = (
#                 r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
#                 r'DBQ=' + path_energia)
#     try:
#         cnxn = pyodbc.connect(conn_str)
#         Z_or_Y = 'Z'
#
#     except pyodbc.Error:
#         MessageBox(None, 'Erro na conexão com a rede (Z:):\nPor favor, verifique que consegue estabelecer uma conexão '
#                          'antes de correr o programa.', 'Error', 0)
#         print('Erro na conexão com a rede (Z:):\nPor favor, verifique que consegue estabelecer uma conexão '
#               'antes de correr o programa.')
#         time.sleep(10)
#         sys.exit()
#
#     crsr = cnxn.cursor()
#     crsr.execute("SELECT * FROM Tabeladeinstalacoes")
#     df = pd.DataFrame.from_records(crsr.fetchall())
#     df.columns = [column[0] for column in crsr.description]
#     return df


def find_between(s, first, last):
    """
        procura o last a partir do inicio

    :param s: string
    :param first: primeiro caracter para encontrar
    :param last: ultimo caracter para encontrar
    :return:
    """

    try:
        start = s.index(first) + len(first)
        end = s.index(last, start)
        return s[start:end]
    except ValueError:
        return ""


def find_between_r(s, first, last):
    """
        procura o last a partir do fim

    :param s: string
    :param first: ultimo caracter para encontrar
    :param last: primeiro caracter para encontrar
    :return:
    """

    try:
        start = s.rindex(first) + len(first)
        end = s.rindex(last, start)
        return s[start:end]
    except ValueError:
        return ""


def translate_enum(month):
    if len(month) > 3:
        return {
            "Janeiro": "1",
            "Fevereiro": "2",
            "Março": "3",
            "Abril": "4",
            "Maio": "5",
            "Junho": "6",
            "Julho": "7",
            "Agosto": "8",
            "Setembro": "9",
            "Outubro": "10",
            "Novembro": "11",
            "Dezembro": "12"
        }[month]
    else:
        month = month.upper()
        return {
            "JAN": "1",
            "FEV": "2",
            "MAR": "3",
            "ABR": "4",
            "MAI": "5",
            "JUN": "6",
            "JUL": "7",
            "AGO": "8",
            "SET": "9",
            "OUT": "10",
            "NOV": "11",
            "DEZ": "12"
        }[month]




def turn_int(n):
    try:
        return int(n)
    except ValueError:
        pass
def num_mes(month):
    month = str(month).zfill(2)

    return {
        "01": "Janeiro",
        "02": "Fevereiro",
        "03": "Março",
        "04": "Abril",
        "05": "Maio",
        "06": "Junho",
        "07": "Julho",
        "08": "Agosto",
        "09": "Setembro",
        "10": "Outubro",
        "11": "Novembro",
        "12": "Dezembro"
    }[month]


def num_mes_abv(month):
    month = str(month).zfill(2)
    return {
        "01": "Jan",
        "02": "Fev",
        "03": "Mar",
        "04": "Abr",
        "05": "Mai",
        "06": "Jun",
        "07": "Jul",
        "08": "Ago",
        "09": "Set",
        "10": "Out",
        "11": "Nov",
        "12": "Dez"
    }[month]


def join_one_excel(cil, date_begin, date_end, path_out='C:\\Users\\Vasco Abreu - PC\\Downloads'):
    """
    Junta exceis mensais de telecontagem em um só excel,
    preservando só as colunas da data, hora e potencia ativa.
    :param cil: int ou string, tanto faz
    :param date_begin: string, formato "ano-mes-dia" (ex "2018-12-01")
    :param date_end: string, formato "ano-mes-dia" (ex "2019-11-30")
    :param path_out: pasta para onde vai o ficheiro junto, tem por default a pasta dos downloads
    :return:
    """
    df_db = conect_db('energia')
    tt = df_db.loc[df_db.CIL == int(cil), 'Abastecimento'].values[0]
    path = "Z:\\DATABASE\\ENERGIA\\DATAFILES"
    cil_path = path + '\\' + tt + '\\' + str(cil)
    files_cil = os.listdir(cil_path)

    date_range = pd.date_range(date_begin, date_end, freq='MS').strftime("%Y%m").tolist()
    files_dates = [f for f in files_cil if find_between(f, '_', '.') in date_range]
    files_dates.sort()
    max_date = find_between(max(files_dates), '_', '.xlsx')
    year_max = max_date[:4]
    month_max = max_date[4:6]
    day_max = calendar.monthrange(int(year_max), int(month_max))[1]
    date_end = year_max + '-' + month_max + '-' + str(day_max)

    min_date = find_between(min(files_dates), '_', '.xlsx')
    year_min = min_date[:4]
    month_min = min_date[4:6]
    day_min = calendar.monthrange(int(year_min), int(month_min))[1]
    date_begin = year_min + '-' + month_min + '-' + str(day_min)

    df_total = pd.DataFrame()
    for file in files_dates:
        file_path = cil_path + '\\' + file
        df = pd.read_excel(file_path, skiprows=9, usecols="A,B,C")
        df_total = df_total.append(df)

    df_total.to_excel(path_out + '\\' + str(cil) + '_' + date_begin + '_' + date_end + '.xlsx', index=False)

    return df_total


def data_Pascoa(ano):
    a = ano % 19
    b = ano // 100
    c = ano % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    mes = (h + l - 7 * m + 114) // 31
    dia = ((h + l - 7 * m + 114) % 31) + 1

    data = date(ano, mes, dia)

    return (data)


def cria_feriados(ano, municipio):
    ano = int(ano)
    feriados = ["01-01", "04-25", "05-01", "06-10", "08-15", "10-05", "11-01", "12-01", "12-08", "12-25"]

    if municipio in ["Lisboa", "Cascais"]:
        feriados = feriados + ["06-13"]
    elif municipio == 'Amadora':
        feriados = feriados + ["09-11"]
    elif municipio == 'Porto':
        feriados = feriados + ["06-24"]
    elif municipio == 'Loures':
        feriados = feriados + ["07-26"]
    elif municipio == 'Mafra':
        feriados = feriados + ["05-10"]
    elif municipio == 'Sintra':
        feriados = feriados + ["06-29"]

    feriados = [str(ano) + '-' + f for f in feriados]
    feriados = [f.split('-') for f in feriados]
    feriados = [date(int(f[0]), int(f[1]), int(f[2])) for f in feriados]

    pascoa = data_Pascoa(ano)
    sexta_santa = pascoa - timedelta(days=2)

    carnaval = pascoa - timedelta(days=47)
    # tem que ser 3a feira
    if carnaval.weekday() != 1:
        diff = 1 - carnaval.weekday()
        carnaval = carnaval + timedelta(days=diff)

    corpo_cristo = pascoa + timedelta(days=60)
    # tem que ser 5a feira
    if corpo_cristo.weekday() != 3:
        diff = 3 - corpo_cristo.weekday()
        corpo_cristo = corpo_cristo + timedelta(days=diff)

    feriados = feriados + [pascoa, sexta_santa, carnaval, corpo_cristo]

    return feriados


def num_semana(day):
    day = str(day).zfill(2)
    return {
        "00": "Segunda-Feira",
        "01": "Terça-Feira",
        "02": "Quarta-Feira",
        "03": "Quinta-Feira",
        "04": "Sexta-Feira",
        "05": "Sábado",
        "06": "Domingo",
    }[day]


def num_semana_abv(day):
    day = str(day).zfill(2)
    return {
        "00": "Seg",
        "01": "Ter",
        "02": "Qua",
        "03": "Qui",
        "04": "Sex",
        "05": "Sab",
        "06": "Dom",
    }[day]


def num_semana_nr(day):
    day = str(day).zfill(2)
    return {
        "00": "2ª Feira",
        "01": "3ª Feira",
        "02": "4ª Feira",
        "03": "5ª Feira",
        "04": "6ª Feira",
        "05": "Sábado",
        "06": "Domingo",
    }[day]

def try_int(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return np.nan
    
def try_date(ano, mes, dia):
    try:
        datetime(ano, mes, 1)
    except TypeError:
        return np.nan

#
# for cil in cils_err:
#     tt = df_err.loc[df_err.CIL == cil, 'Abastecimento'].values[0]
#     path = "Z:\\DATABASE\\energia\\datafiles\\{0}\\{1}".format(tt, cil)
#     new_path = "Z:\\DATABASE\\energia\\datafiles\\{0}\\{1}".format(tt, str(cil)[:-1])
#     print(path)
#     print(new_path)
#     os.rename(path, new_path)

