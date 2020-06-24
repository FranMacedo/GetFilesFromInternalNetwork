import subprocess

def create_reports(cils, dates):
    """
    :param cils: lista de strings
    :param dates: lista de strings, no formato ano-mes (ex: 2019-03)
    :return:
    """

    if isinstance(cils, str):
        cils = [cils]
    if isinstance(dates, str):
        dates = [dates]

    print(cils)
    print(dates)

    cp = subprocess.run(
        ["C:\\Program Files\\R\\R-3.6.1\\bin\\Rscript", "--vanilla",
         "C:\\Users\\Vasco Abreu - PC\\Documents\\R Projects\\GestorRemoto\\py_run.R",
         ','.join(str(line) for line in cils), ','.join(str(line) for line in dates)],
        encoding="ISO-8859-1",
        universal_newlines=True,
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE)

    # print(cp.stdout) # O que o R imprime
    # cp.stderr # Os erros
    # print(cp.returncode) # se correu bem ou não

    if cp.returncode == 0:
        header = "RELATÓRIOS GERADOS"
        text = ["Relatório para o CIL {0} para a data {1} criado.".format(cil, data) for cil, data in zip(cils, dates)]
        return True, {'header': header, 'text': text, 'full': cp.stdout}

    else:
        header = "ERRO A CRIAR RELATÓRIOS"
        text = cp.stderr[56:]
        return False, {'header': header, 'text': text, 'full': cp.stderr}
