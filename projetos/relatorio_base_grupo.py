import cx_Oracle
import datetime

# Função para conectar ao banco de dados Oracle
def db_connect():
    return cx_Oracle.connect('USER/PASSWORD@HOST/SERVICE')

# Define a data de início da coleta
dt_inicio = datetime.date(2023,8,1)

# Define o caminho e nome do arquivo de saída com base nas datas
arq = f'relatorio/geral/relatorio_acion_base_grupo_{dt_inicio}_{datetime.date.today() - datetime.timedelta(days = 1)}.csv'

# Cria o arquivo e escreve o cabeçalho
file = open(arq, 'a')
file.write("""DATA;CLIENTE;IDSCRIPT;GRUPO;BASE;SCRIPT;TRONCO;QTD_CPF_DIA;QTD_TELEFONES_DIA;TENTATIVAS;ATENDIMENTOS;DELIGAMENTO_MANUAL;DESLIG_AUTOMATICO;ATEND_DOCS_DIA;QTD_TENTATIVAS_CPF;TENTATIVA_IMPRODUT;MACHINE;BADPHONE;BLOCK;CUSTO_ACAO;CUSTO_SMS""")
file.close

# Loop pelas datas até a data atual
while dt_inicio < datetime.date.today():
    file = open(arq, 'a')

# Comando SQL para coletar e agregar os dados por data e grupo
    command = fr"""
WITH
base_geral AS (SELECT * FROM DISCADOR_OWNER.DIALERCALLS_FULL
                        WHERE SUBSTR(DATA, 1, 10) = '{str(dt_inicio)}'),

base_geral1 AS (SELECT base_geral.*, SUBSTR(ARQUIVOORIGINAL, INSTR(ARQUIVOORIGINAL, '#') + 1) AS BASE
                FROM base_geral
                        WHERE ARQUIVOORIGINAL LIKE '%#%'),

base_geral2 as (SELECT base_geral1.*, to_char(Idscript) || to_char(base) as grupo FROM base_geral1),

base_tentativas AS (SELECT TO_CHAR(TO_DATE(DATA, 'YYYY-MM-DD HH24:MI:SS'), 'DD/MM/YYYY') as data, IDSCRIPT, grupo, BASE, count (idexec) AS tentativas
                    FROM  base_geral2
                    GROUP BY IDSCRIPT, GRUPO, BASE, TO_CHAR(TO_DATE(DATA, 'YYYY-MM-DD HH24:MI:SS'), 'DD/MM/YYYY')),

base_cpf AS (SELECT IDSCRIPT, GRUPO, BASE, count( DISTINCT cpf) AS cpf
             FROM base_geral2
             GROUP BY IDSCRIPT, GRUPO, BASE),

base_atendimentos AS (SELECT IDSCRIPT, GRUPO, BASE, count (idexec) AS atendimentos
                      FROM base_geral2
                      WHERE fluxo LIKE '%Atendido%'
                      GROUP BY IDSCRIPT, GRUPO, BASE),

base_final AS (SELECT IDSCRIPT, GRUPO, BASE, count (idexec) AS FINAL
               FROM base_geral2
               WHERE fluxo LIKE '%GOL%'
               GROUP BY IDSCRIPT, GRUPO, BASE),

base_badphone AS (SELECT IDSCRIPT, GRUPO, BASE, count (idexec) AS BADPHONE
                  FROM base_geral2
                  WHERE st LIKE '%bad%'
                     or st LIKE '%failed phone%'
                     or st like '%rejected%'
                  GROUP BY IDSCRIPT, GRUPO, BASE),

base_telefonia AS ( SELECT IDSCRIPT, GRUPO, BASE, count (idexec) AS telefonia
                    FROM base_geral2
                    WHERE ST LIKE '%busy%'
                       OR ST LIKE '%no answer%'
                       or st like '%failed network%'
                    GROUP BY IDSCRIPT, GRUPO, BASE),

base_machine AS ( SELECT IDSCRIPT, GRUPO, BASE, count (idexec) AS machine
                  FROM base_geral2
                  WHERE ST LIKE '%Machine%'
                  GROUP BY IDSCRIPT, grupo, BASE),

base_block AS ( SELECT IDSCRIPT, GRUPO, BASE, count (idexec) AS block
                FROM base_geral2
                WHERE fluxo LIKE '%Block%'
                GROUP BY IDSCRIPT, GRUPO, BASE),

base_telefones AS ( SELECT IDSCRIPT, GRUPO, BASE, COUNT( DISTINCT telefone)  AS telefones
                    FROM base_geral2
                    GROUP BY IDSCRIPT, GRUPO, BASE),

base_custo AS (SELECT IDSCRIPT,  GRUPO, BASE, idexec, TEMPO, CASE WHEN TEMPO > 0 AND TEMPO <= 30 THEN 0.0275 ELSE (CEIL(TEMPO / 6) * 0.0055) END AS CUSTO
               FROM base_geral2
               GROUP BY IDSCRIPT, GRUPO, BASE, idexec, tempo),

base_custo1 AS ( SELECT IDSCRIPT, GRUPO, BASE, sum(custo) AS custo
                 FROM base_custo
                 GROUP BY IDSCRIPT, GRUPO, BASE),

base_sms AS (SELECT IDSCRIPT, GRUPO, BASE, idexec, st_out, CASE WHEN st_out = 'Sent SMS' THEN 0.07 ELSE 0 END AS CUSTO_SMS
             FROM base_geral2),

base_sms1 AS (SELECT IDSCRIPT, GRUPO, BASE, sum(custo_sms) AS custo_sms
              FROM base_sms
              GROUP BY IDSCRIPT, GRUPO, BASE),

relatorio AS (SELECT (a.data) as data, A.GRUPO AS GRUPO, a.idscript AS idscript, a.BASE AS BASE, a.tentativas AS tentativas, b.atendimentos AS atendimentos, c.FINAL AS FINAL,
d.badphone AS badphone, e.telefonia AS telefonia, f.machine AS machine, g.block AS block, i.cpf AS cpf, j.telefones AS telefones, k.custo AS custo, l.custo_sms AS custo_sms
FROM base_tentativas a
LEFT JOIN base_atendimentos b ON a.GRUPO = b.GRUPO
LEFT JOIN base_final c ON a.GRUPO = c.GRUPO
LEFT JOIN base_badphone d ON a.GRUPO = d.GRUPO
LEFT JOIN base_telefonia e ON a.GRUPO = e.GRUPO
LEFT JOIN base_machine f ON a.GRUPO = f.GRUPO
LEFT JOIN base_block g ON a.GRUPO = g.GRUPO
LEFT JOIN base_cpf i ON a.GRUPO = i.GRUPO
LEFT JOIN base_telefones J ON a.GRUPO = j.GRUPO
LEFT JOIN base_custo1 k ON a.GRUPO = k.GRUPO
LEFT JOIN base_sms1 l ON a.GRUPO = l.GRUPO),


relatorio_v2 AS (SELECT data, idscript, GRUPO, BASE, tentativas, cpf, CASE WHEN atendimentos IS NULL THEN 0 ELSE atendimentos END AS atendimentos, custo, telefones,
CASE WHEN FINAL IS NULL THEN 0 ELSE FINAL END AS FINAL, badphone, telefonia, machine, block, custo_sms FROM RELATORIO),


relatorio_v3 AS (SELECT data, idscript, GRUPO, BASE, tentativas, cpf, (atendimentos + final) AS atendimentos, FINAL, telefones, badphone, telefonia, machine, block, custo, custo_sms
FROM relatorio_v2),

nomes_v1 AS (SELECT DISTINCT substr(DATA, 1, 10) AS data, IDSCRIPT, GRUPO, base, script FROM base_geral2),
nomes_v2 AS (SELECT ROW_NUMBER() OVER (PARTITION BY GRUPO ORDER BY GRUPO) AS rownumber, nomes_v1.* FROM nomes_v1),
nomes_v3 AS (SELECT * FROM nomes_v2 WHERE rownumber = 1),


relatorio_v4 AS ( SELECT substr(a.DATA, 1, 10) AS DATA, d.cliente AS CLIENTE, a.grupo as grupo, a.idscript AS Idscript, a.BASE AS BASE, b.script as script,
                         d.tronco, a.tentativas AS Tentativas, a.cpf AS Qtd_cpf,
                         CASE when a.cpf = '0' THEN '0' ELSE substr((a.tentativas / a.cpf), 1, 4) end AS qtd_tentativas_cpf,
                         a.telefones AS qtd_telefones_dia, a.atendimentos AS Atendimentos,
                         c.atendimentos AS deslig_manual, CASE when a.cpf = '0' THEN '0' ELSE (substr((a.atendimentos / a.cpf), 1, 4)) END AS atend_docs_dia,
                         a.telefonia AS tentativa_improdutiva, a.machine AS machine,
                         a.badphone AS badphone, a.FINAL AS Sucesso, a.block AS block,
                         a.custo AS custo_acao, custo_sms
                  FROM relatorio_v3 a
                      inner join  nomes_v3 b on a.GRUPO = b.GRUPO
                      inner JOIN base_atendimentos c ON a.GRUPO = c.GRUPO
                      inner JOIN PANEAS_OWNER.TRONCOS d ON a.idscript = d.IDSCRIPT),

base_formato as ( select DATA, CLIENTE, Idscript, grupo, BASE, script, TRONCO, Qtd_cpf, qtd_telefones_dia, tentativas, Atendimentos, deslig_manual, Sucesso,
                         atend_docs_dia, qtd_tentativas_cpf, tentativa_improdutiva, machine, badphone, block, custo_acao, custo_sms
                  from relatorio_v4)

select * from  base_formato"""

    print('capturando dados')
    con = db_connect()
    cur = con.cursor()
    cur.execute(command)
    dados = cur.fetchall()
    con.close()
    print('preparando o arquivo')
    for iten in dados:
        iten = '\n'+str(iten)
        iten = iten.replace(')', '').replace('(', '').replace(',', ';').replace('.csv', '').replace('None', '').replace('.', ',').replace("'", '').replace(' ', '')
        file.write(iten)
    file.close()
    dt_inicio += datetime.timedelta(days=1)
    print(str(dt_inicio))