import cx_Oracle
import datetime

# Função para conectar ao banco de dados Oracle
def db_connect():
    return cx_Oracle.connect('USER/PASSWORD@HOST/SERVICE')

# Define a data inicial do relatorio
dt_inicio = datetime.date(2023,7,1)

# Caminho e nome do arquivo CSV de saída
arq = f'relatorio/CUSTO-{dt_inicio}_{datetime.date.today()  - datetime.timedelta(days = 1)}.csv'

# Cria o cabeçalho do arquivo CSV com os nomes das colunas
file = open(arq, 'a')
file.write("""DATA;CLIENTE;IDSCRIPT;TRONCO;TEMPO;TEMPO_MEDIO;CUSTO_ACAO;CUSTO_SMS""")
file.close

# Laço que percorre cada dia desde a data inicial até a data atual
while dt_inicio < datetime.date.today():
    file = open(arq, 'a')

    # Consulta SQL com múltiplas CTEs para agregar dados de tempo e custo das chamadas
    command = f"""  
WITH
base_geral AS (SELECT * FROM DISCADOR_OWNER.DIALERCALLS_FULL WHERE SUBSTR(DATA, 1, 10) = '{str(dt_inicio)}'),

base_tempo AS (SELECT IDSCRIPT, SUM(TEMPO) AS TEMPO FROM  base_geral
                        GROUP BY IDSCRIPT),

base_tempo_m as (SELECT IDSCRIPT, to_number(substr(avg(TEMPO), 1, 4)) AS TEMPO FROM  base_geral
                        GROUP BY IDSCRIPT),

base_custo AS (SELECT IDSCRIPT, idexec, TEMPO, CASE WHEN TEMPO > 0 AND TEMPO <= 30 THEN 0.0275 ELSE (CEIL(TEMPO / 6) * 0.0055) END AS CUSTO
FROM base_geral GROUP BY IDSCRIPT, idexec, tempo),

base_custo1 AS ( SELECT IDSCRIPT, sum(custo) AS custo FROM base_custo GROUP BY IDSCRIPT),

base_sms AS (SELECT IDSCRIPT, idexec, st_out, CASE WHEN st_out = 'Sent SMS' THEN 0.07 ELSE 0 END AS CUSTO_SMS
FROM base_geral),

base_sms1 AS (SELECT IDSCRIPT, sum(custo_sms) AS custo_sms FROM base_sms GROUP BY IDSCRIPT),

relatorio AS (SELECT a.idscript AS idscript, a.TEMPO AS TEMPO, c.tempo as tempo_medio,
                k.custo AS custo, l.custo_sms AS custo_sms
                FROM base_tempo a
                left join base_tempo_m c on a.IDSCRIPT = c.IDSCRIPT
                LEFT JOIN base_custo1 k ON a.IDSCRIPT = k.IDSCRIPT
                LEFT JOIN base_sms1 l ON a.IDSCRIPT = l.IDSCRIPT),

relatorio_v2 AS (SELECT idscript, TEMPO, tempo_medio, custo, custo_sms
                 FROM RELATORIO),

relatorio_v3 AS (SELECT idscript, TEMPO, tempo_medio, custo, custo_sms
FROM relatorio_v2),

nomes_v1 AS (SELECT DISTINCT substr(DATA, 1, 10) AS data, IDSCRIPT FROM base_geral),
nomes_v2 AS (SELECT ROW_NUMBER() OVER (PARTITION BY IDSCRIPT ORDER BY IDSCRIPT) AS rownumber, nomes_v1.* FROM nomes_v1),
nomes_v3 AS (SELECT * FROM nomes_v2 WHERE rownumber = 1),

relatorio_v4 AS ( SELECT
        substr(b.DATA, 1, 10) AS DATA,
        d.cliente AS CLIENTE,
        a.idscript AS Idscript,
        d.TRONCO as tronco,
        a.TEMPO AS TEMPO,
        a.tempo_medio as tempo_medio,
        a.custo AS custo_acao,
        custo_sms
    FROM relatorio_v3 a
    LEFT JOIN nomes_v3 b ON a.idscript = b.IDSCRIPT
    LEFT JOIN PANEAS_OWNER.TRONCOS d ON a.idscript = d.IDSCRIPT
    group by A.idscript, substr(b.DATA, 1, 10), d.cliente, d.TRONCO, a.TEMPO, a.tempo_medio, a.custo, custo_sms)

SELECT * FROM relatorio_v4"""

    print('capturando dados')
    con = db_connect()
    cur = con.cursor()
    cur.execute(command)
    dados = cur.fetchall()
    con.close()
    print('preparando o arquivo')
    for iten in dados:
        # Formata e limpa os dados antes de escrever no CSV
        iten = '\n' + str(iten)
        iten = iten.replace(')', '').replace('(', '').replace(',', ';').replace('None', '').replace('.', ',').replace(
            "'", '')
        file.write(iten)

    file.close()
    dt_inicio += datetime.timedelta(days=1)  # Avança um dia no loop
    print(str(dt_inicio))
