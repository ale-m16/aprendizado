import cx_Oracle
import datetime

# Função para conectar ao banco de dados Oracle
def db_connect():
    return cx_Oracle.connect('USER/PASSWORD@HOST/SERVICE')

# Define a data de ontem
ontem = datetime.datetime.today() - datetime.timedelta(days=1)
ontem = ontem.strftime("%Y-%m-%d")

# Caminho do arquivo de relatório CSV com base na data de ontem
arq = rf'C:\Users\User\RELATORIOS GERENCIAIS\RESULTADOS\2023\RELATORIO DIARIO (DISCAGENS)\relatorio_discagens_{ontem}.csv'

# Abre o arquivo e escreve o cabeçalho do CSV
file = open(arq, 'a')
dt_inicio = datetime.date(2023,4,14)

file.write("""DATA; CLIENTE; CAMPANHA_IDSCRIPT; SCRIPT; CANAIS_TELEFONIA; SEGMENTOS_BASE; QTD_BASE; CANAIS_ACAO; PERIODO_EXEC_DE; PERIODO_EXEC_ATE; META; CANAIS; PROPORCAO_CANAIS; TENTATIVAS; QTD_CPF; QTD_TENTATIVAS_CPF; TENTATIVAS_CANAL; QTD_N_DISCADO; QTD_TELEFONES_DIA; ATENDIMENTOS; ATEND_DOCS_DIA; DESLIG_MANUAL; N_ATENDE_OCUP; MACHINE; BADPHONE; DESLIG_AUTO; BLOCK; CONVERSAO; CONVERSAO_PORCENT; CUSTO_ACAO; RETORNO_FINANC; CUSTO_RETORNO; RESULTADO""")
file.close

# Loop pelas datas a partir de dt_inicio até hoje
while dt_inicio < datetime.date.today():
    file = open(arq, 'a')

# Comando SQL para obter e processar os dados do discador
while dt_inicio < datetime.date.today():
    file = open(arq, 'a')
    command = f"""
WITH
base_geral AS (SELECT * FROM DISCADOR_OWNER.DIALERCALLS WHERE SUBSTR(DATA, 1, 10) = '{str(dt_inicio)}'),

base_tentativas AS (SELECT idscript, count (idexec) AS tentativas FROM  base_geral GROUP BY idscript),

base_cpf AS (SELECT idscript, campanha, count( DISTINCT cpf) AS cpf FROM base_geral GROUP BY idscript, campanha),

base_atendimentos AS (SELECT idscript, count (idexec) AS atendimentos
FROM base_geral WHERE fluxo LIKE '%Atendido%' GROUP BY idscript),

base_final AS (SELECT idscript, count (idexec) AS FINAL
FROM base_geral WHERE fluxo LIKE '%GOL%' GROUP BY idscript),

base_badphone AS (SELECT idscript, count (idexec) AS BADPHONE
FROM base_geral WHERE st LIKE '%bad%' GROUP BY idscript),

base_telefonia AS ( SELECT idscript, count (idexec) AS telefonia
FROM base_geral WHERE fluxo LIKE '%Telefonia%' OR fluxo LIKE '%Fora%' GROUP BY idscript),

base_machine AS ( SELECT idscript, count (idexec) AS machine
FROM base_geral WHERE fluxo LIKE '%Machine%' GROUP BY idscript),

base_block AS ( SELECT idscript, count (idexec) AS block
FROM base_geral WHERE fluxo LIKE '%Block%' GROUP BY idscript),

base_telefones AS ( SELECT idscript, COUNT( DISTINCT telefone)  AS telefones
FROM base_geral GROUP BY idscript),

base_custo AS (SELECT idscript, idexec, TEMPO, CASE WHEN TEMPO > 0 AND TEMPO <= 30 THEN 0.0275 ELSE (((CEIL(TEMPO/6))/10) * 0.0550) END AS CUSTO
FROM base_geral GROUP BY idscript, idexec, tempo),

base_custo1 AS ( SELECT idscript, sum(custo) AS custo FROM base_custo GROUP BY idscript),

relatorio AS (SELECT a.idscript AS idscript, i.campanha AS campanha, a.tentativas AS tentativas, b.atendimentos AS atendimentos, c.FINAL AS FINAL, 
d.badphone AS badphone, e.telefonia AS telefonia, f.machine AS machine, g.block AS block, i.cpf AS cpf, j.telefones AS telefones, k.custo AS custo
FROM base_tentativas a LEFT JOIN base_atendimentos b ON a.idscript = b.idscript LEFT JOIN base_final c ON a.idscript = c.idscript
LEFT JOIN base_badphone d ON a.idscript = d.idscript
LEFT JOIN base_telefonia e ON a.idscript = e.idscript
LEFT JOIN base_machine f ON a.idscript = f.idscript
LEFT JOIN base_block g ON a.idscript = g.idscript 
LEFT JOIN base_cpf i ON a.idscript = i.idscript
LEFT JOIN base_telefones J ON a.idscript = j.idscript
LEFT JOIN base_custo1 k ON a.idscript = k.idscript),


relatorio_v2 AS (SELECT idscript, campanha, tentativas, cpf, CASE WHEN atendimentos IS NULL THEN 0 ELSE atendimentos END AS atendimentos, custo, telefones,
CASE WHEN FINAL IS NULL THEN 0 ELSE FINAL END AS FINAL, badphone, telefonia, machine, block FROM RELATORIO),


relatorio_v3 AS (SELECT idscript, campanha, tentativas, cpf, (atendimentos + final) AS atendimentos, FINAL, telefones, badphone, telefonia, machine, block, custo
FROM relatorio_v2),

nomes_v1 AS (SELECT DISTINCT substr(DATA, 1, 10) AS data, idscript, script FROM base_geral),
nomes_v2 AS (SELECT ROW_NUMBER() OVER (PARTITION BY idscript ORDER BY idscript) AS rownumber, nomes_v1.* FROM nomes_v1),
nomes_v3 AS (SELECT * FROM nomes_v2 WHERE rownumber = 1),

relatorio_v4 AS ( SELECT substr(b.DATA, 1, 10) AS DATA, '' AS cliente, a.idscript AS campanha_idscript, a.campanha AS campanha, b.script AS script, '' AS canais_telefonia, '' AS segmentos_base, '' qtd_base, '' AS canais_acao, '' AS periodo_exec_de, '' AS periodo_exec_ate,
'' AS meta, '' AS canais, '' AS proporcao_canais, a.tentativas AS tentativas, a.cpf AS qtd_cpf, CASE when a.cpf = '0' THEN '0' ELSE substr((a.tentativas / a.cpf), 1, 4) end AS qtd_tentativas_cpf, '' AS tentativas_canal,
'' AS qtd_n_discado, a.telefones AS qtd_telefones_dia, a.atendimentos AS atendimentos, CASE when a.cpf = '0' THEN '0' ELSE (substr((a.atendimentos / a.cpf), 1, 4)) END AS atend_docs_dia, c.atendimentos AS deslig_manual,
a.telefonia AS n_atende_ocup, a.machine AS machine, a.badphone AS badphone, a.FINAL AS deslig_auto, a.block AS block,
'' AS conversao, '' AS conversao_porcent, a.custo AS custo_acao, '' AS retorno_financ, '' AS custo_retorno, '' AS resultado
FROM relatorio_v3 a LEFT JOIN nomes_v3 b ON a.idscript = b.idscript LEFT JOIN base_atendimentos c ON a.idscript = c.idscript)

SELECT * FROM relatorio_v4;"""

    print('capturando dados')
    con = db_connect()
    cur = con.cursor()
    cur.execute(command)
    dados = cur.fetchall()
    con.close()
    print('preparando o arquivo')
    for iten in dados:
        iten = '\n'+str(iten)
        iten = iten.replace(')', '').replace('(', '').replace(',', ';').replace('None', '').replace('.', ',').replace("'", '')
        file.write(iten)
    file.close()
    dt_inicio += datetime.timedelta(days=1)
    print(str(dt_inicio))