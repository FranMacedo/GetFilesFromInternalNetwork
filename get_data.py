import pandas as pd
from dateutil.relativedelta import relativedelta
import os
from datetime import datetime as dt
from datetime import timedelta

db_dir = r'Z:\DATABASE'
energy_dir = os.path.join(db_dir, 'ENERGIA')
energy_data_folder = os.path.join(energy_dir, 'DATAFILES')


def datetime_df(df):
    """
    df - dataframe no formato dos ficheiros que vieram do site online.edpdistribuicao.pt.

    Cria um index da df no formato datetime. O problema é que ainda não lida muito bem
    com a mudança de horas, pois no formato do site online.edpdistribuicao.pt eles acrescentam, nos
    dias de mudança de horas, 1 hora, ficando o dia com 25 horas.
    Também acho que tiram uma hora no mes oposto (31 de Março e 27 de Outubro).

    AINDA NÃO RESOLVI ISTO, MAS O VASCO APAGAVA TAMBÉM ESTES VALORES EXTRA.
    """

    # MUDANÇA DE HORA! PARA JÁ APAGADA, TAL COMO O VASCO FAZIA
    df = df.query('Hora not in ["24:15", "24:30", "24:45", "25:00"]')

    df['Data_Hora'] = pd.to_datetime(
        df['Data'] + ' ' + df['Hora'], format='%Y/%m/%d %H:%M')
    df = df.set_index('Data_Hora')
    df.sort_index(inplace=True)
    # if data_max is not None and data_max in df.Data:
    #     df = df.loc[df.Data != data_max, :]

    missing_vals = pd.date_range(start=df.index.min(
    ), end=df.index.max(), freq='15min').difference(df.index)
    print(missing_vals)
    # valor arbitrário, para interpolar caso os dias em falta sejam só 15
    if not missing_vals.empty:
        if len(missing_vals) <= 15:
            df = df[~df.index.duplicated()]
            df = df.reindex(pd.date_range(
                start=df.index[0], end=df.index[-1], freq='15min'))

            df.iloc[:, 1].interpolate(inplace=True)
            df.iloc[:, 3].interpolate(inplace=True)
            df.iloc[:, 4].interpolate(inplace=True)

            df.loc[df.index.isin(missing_vals), 'Data'] = df.index[df.index.isin(
                missing_vals)].strftime('%Y/%m/%d')
            df.loc[df.index.isin(missing_vals), 'Hora'] = df.index[df.index.isin(
                missing_vals)].strftime('%H:%M')
    # algumas vêm com duplicados pelos vistos?
    df = df.loc[~df.index.duplicated(keep='first')]
    df.columns = ['Data', 'Hora', 'Potência Ativa',
                  'Potência Reativa Indutiva', 'Potência Reativa Capacitiva']
    return df


def process_df_edp(df_total, ym):
    """
    Process dataframe with n excel files in edp format together, cleaning data and missing values, date format,
     removing extra data
    """
    df_total.sort_values(by='Data', inplace=True)
    # df_total = df_total.set_index('Data_Hora')

    # Substituir já as 24h, não vale a pena deixar para depois, visto que isto é um erro e não estraga
    data_max = None
    if not df_total.loc[df_total['Hora'] == '24:00', 'Hora'].empty:
        df_total.loc[df_total['Hora'] == '24:00', 'Hora'] = '23:59'
        df_total['Data'] = pd.to_datetime(df_total['Data'], format='%Y/%m/%d')
        data_max = (df_total.Data.max() +
                    timedelta(days=1)).strftime('%Y/%m/%d')
        df_total.loc[df_total['Hora'] == '23:59', 'Data'] = df_total.loc[
            df_total['Hora'] == '23:59', 'Data'] + timedelta(
            days=1)
        df_total.loc[df_total['Hora'] == '23:59', 'Hora'] = '00:00'

        # data maxima 1 dia à frente da data maxima disponivel, de modo a mais a frente tira-la daqui.
        # foi criada sem querer durante a movmentacao das 24:00h para 00:00h do dia seguinte.

        # Volta a por a data em string
        df_total['Data'] = df_total['Data'].dt.strftime('%Y/%m/%d')

    if data_max is not None and data_max in df_total.Data.tolist():
        df_total = df_total.loc[df_total.Data != data_max, :]
    df_total = datetime_df(df_total)

    df_total['ym'] = [str(d.year).zfill(4) + str(d.month).zfill(2)
                      for d in df_total.index]
    df_total = df_total.loc[df_total.ym.isin(ym)]
    df_total.drop('ym', axis=1, inplace=True)
    print(df_total)

    return df_total


def check_files_rede(cil, tt, all_dates):
    try:
        # Teste rápido para ver se há conecção com a rede
        os.listdir(energy_data_folder)
    except FileNotFoundError:
        print("-- Erro na ligação com a rede Z:. Verifique a ligação!")
        return []
    try:
        path = f"{energy_data_folder}\\{tt}\\{cil}"
        files_to_use = os.listdir(path)
    except (FileNotFoundError, OSError):
        print("-- " + str(cil) + " Sem dados")
        return []
    files_to_use.sort()
    files_to_use = [f for f in files_to_use if any(d in f for d in all_dates)]

    return files_to_use


def get_cil_data(cil, tt, ym):
    """
        union of files from REDE Z:.
    """
    print(f"- a reunir dados do {cil} nos meses {ym}")
    files_to_use = check_files_rede(cil, tt, ym)

    path = f"{energy_data_folder}\\{tt}\\{cil}"
    if not files_to_use:
        return None, False
    for file in files_to_use:
        # file = files_to_use[0]
        file_path = path + '\\' + file
        try:
            df = pd.read_excel(file_path, skiprows=9)
        except PermissionError:
            time.sleep(2)
            try:
                df = pd.read_excel(file_path, skiprows=9)
            except PermissionError:
                time.sleep(2)
                try:
                    df = pd.read_excel(file_path, skiprows=9)
                except PermissionError:
                    print(f'\n\nERRRO no ficheiro {file_path}')
                    continue
        df = df.iloc[:, :5]
        df.columns = ["Data", "Hora", "Potência Ativa",
                      "Potência Reativa Indutiva",  "Potência Reativa Capacitiva"]
        if files_to_use.index(file) == 0:
            df_total = df
        else:
            df_total = pd.concat([df_total, df], join='inner', axis=0)

    df_total = process_df_edp(df_total, ym)
    if df_total.empty:
        return None, False

    return df_total, True
