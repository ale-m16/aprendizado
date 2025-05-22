import cx_Oracle
import datetime

# Função para conectar ao banco de dados Oracle
def db_connect():
    return cx_Oracle.connect('USER/PASSWORD@HOST/SERVICE')

# Define a data inicial do relatorio
dt_inicio = datetime.date(2025,1,1)

# Caminho e nome do arquivo CSV de saída
arq = fr'\\SERVIDOR\Users\USER\RESULTADOS\2025\RELATORIO DISCAGENS TEMPO\relatorio_acion_base_grupo_TEMPO_{dt_inicio}_{datetime.date.today() - datetime.timedelta(days = 1)}.csv'

# Cria o cabeçalho do arquivo CSV com os nomes das colunas
file = open(arq, 'a')
file.write("""DATA;CLIENTE;IDSCRIPT;GRUPO;BASE;SCRIPT;TRONCO;QTD_CPF_DIA;QTD_TELEFONES_DIA;TENTATIVAS;ATENDIMENTOS;DELIGAMENTO_MANUAL;GOL;DESLIG_AUTOMATICO;ATEND_DOCS_DIA;QTD_TENTATIVAS_CPF;TENTATIVA_IMPRODUT;MACHINE;BADPHONE;BLOCK;CUSTO_ACAO;CUSTO_SMS;tempo_0_9;tempo_10;LOW_07;UP_07;LOW_03;UP_03;tempo_medio;tempo_medio_GOL""")
file.close

# Laço que percorre cada dia desde a data inicial até a data atual
while dt_inicio < datetime.date.today():
    file = open(arq, 'a')

    # Consulta SQL com múltiplas CTEs que extrai, organiza e agrega dados de chamadas
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

base_tp_0_9 AS (SELECT IDSCRIPT, GRUPO, BASE, count (idexec) AS tempo_0_9
                      FROM base_geral2
                      WHERE FLUXO like '%Atendido%'
                      and tempo < 10
                      or FLUXO like '%GOL%'
                      and tempo < 10
                      GROUP BY IDSCRIPT, GRUPO, BASE),

base_tp_10 AS (SELECT IDSCRIPT, GRUPO, BASE, count (idexec) AS tempo_10
                      FROM base_geral2
                      WHERE FLUXO like '%Atendido%'
                      and tempo >= 10
                      or FLUXO like '%GOL%'
                      and tempo >= 10
                      GROUP BY IDSCRIPT, GRUPO, BASE),

base_tp_medio AS (SELECT IDSCRIPT, GRUPO, BASE, avg(TEMPO) as tempo_medio
                      FROM base_geral2
                      WHERE FLUXO like '%Atendido%'
                      or FLUXO like '%GOL%'
                      GROUP BY IDSCRIPT, GRUPO, BASE),

base_tp_medio1 AS (SELECT IDSCRIPT, GRUPO, BASE, avg(TEMPO) as tempo_medio_gol
                      FROM base_geral2
                      WHERE FLUXO like '%GOL%'
                      GROUP BY IDSCRIPT, GRUPO, BASE),

base_tp_low07 AS (SELECT count(IDEXEC) as low_07, IDSCRIPT, GRUPO, BASE
                      FROM base_geral2
                      WHERE FLUXO like '%Atendido%'
                      and TEMPO < 7
                      or FLUXO like '%GOL%'
                      and TEMPO < 7
                      GROUP BY IDSCRIPT, GRUPO, BASE),

base_tp_up07 AS (SELECT count(IDEXEC) as up_07, IDSCRIPT, GRUPO, BASE
                      FROM base_geral2
                      WHERE FLUXO like '%Atendido%'
                      and TEMPO >= 7
                      or FLUXO like '%GOL%'
                      and TEMPO >= 7
                      GROUP BY IDSCRIPT, GRUPO, BASE),

base_tp_low03 AS (SELECT count(IDEXEC) as low_03, IDSCRIPT, GRUPO, BASE
                      FROM base_geral2
                      WHERE FLUXO like '%Atendido%'
                      and TEMPO < 3
                      or FLUXO like '%GOL%'
                      and TEMPO < 3
                      GROUP BY IDSCRIPT, GRUPO, BASE),

base_tp_up03 AS (SELECT count(IDEXEC) as up_03, IDSCRIPT, GRUPO, BASE
                      FROM base_geral2
                      WHERE FLUXO like '%Atendido%'
                      and TEMPO >= 3
                      or FLUXO like '%GOL%'
                      and TEMPO >= 3
                      GROUP BY IDSCRIPT, GRUPO, BASE),

base_completo AS (SELECT IDSCRIPT, GRUPO, BASE, count (idexec) AS completo
                      FROM base_geral2
                      WHERE FLUXO_OUT like '%Completo%'
                      GROUP BY IDSCRIPT, GRUPO, BASE),

base_custo AS (SELECT IDSCRIPT,  GRUPO, BASE, idexec, TEMPO, CASE WHEN TEMPO > 0 AND TEMPO <= 30 THEN 0.0275 ELSE (CEIL(TEMPO / 6) * 0.0055) END AS CUSTO
               FROM base_geral2
               GROUP BY IDSCRIPT, GRUPO, BASE, idexec, tempo),

base_custo1 AS ( SELECT IDSCRIPT, GRUPO, BASE, sum(custo) AS custo
                 FROM base_custo
                 GROUP BY IDSCRIPT, GRUPO, BASE),

base_sms AS (SELECT IDSCRIPT, GRUPO, BASE, idexec, st_out, CASE WHEN st_out like '%Sent SMS%' THEN 0.07 ELSE 0 END AS CUSTO_SMS
             FROM base_geral2),

base_sms1 AS (SELECT IDSCRIPT, GRUPO, BASE, sum(custo_sms) AS custo_sms
              FROM base_sms
              GROUP BY IDSCRIPT, GRUPO, BASE),

relatorio AS (SELECT (a.data) as data, A.GRUPO AS GRUPO, a.idscript AS idscript, a.BASE AS BASE,
                a.tentativas AS tentativas, b.atendimentos AS atendimentos, c.FINAL AS FINAL,
                d.badphone AS badphone, e.telefonia AS telefonia, f.machine AS machine, g.block AS block,
                h.cpf AS cpf, i.telefones AS telefones, j.custo AS custo, k.custo_sms AS custo_sms,
                L.tempo_0_9 as tempo_0_9, m.tempo_10 as tempo_10, P.low_07 AS LOW_07, Q.up_07 AS UP_07, r.low_03 as low_03, S.up_03 AS UP_03,
                n.tempo_medio as tempo_medio, t.tempo_medio_gol as tempo_medio_gol, o.completo as completo

                FROM base_tentativas a
                LEFT JOIN base_atendimentos b ON a.GRUPO = b.GRUPO
                LEFT JOIN base_final c ON a.GRUPO = c.GRUPO
                LEFT JOIN base_badphone d ON a.GRUPO = d.GRUPO
                LEFT JOIN base_telefonia e ON a.GRUPO = e.GRUPO
                LEFT JOIN base_machine f ON a.GRUPO = f.GRUPO
                LEFT JOIN base_block g ON a.GRUPO = g.GRUPO
                LEFT JOIN base_cpf h ON a.GRUPO = h.GRUPO
                LEFT JOIN base_telefones i ON a.GRUPO = i.GRUPO
                LEFT JOIN base_custo1 j ON a.GRUPO = j.GRUPO
                LEFT JOIN base_sms1 k ON a.GRUPO = k.GRUPO
                LEFT JOIN base_tp_0_9 L ON A.GRUPO = L.GRUPO
                LEFT JOIN base_tp_10 M ON A.GRUPO = M.GRUPO
                LEFT JOIN base_tp_medio N ON A.GRUPO = N.GRUPO
                LEFT JOIN base_completo O ON A.GRUPO = O.GRUPO
                LEFT JOIN base_tp_low07 P ON A.GRUPO = P.GRUPO
                LEFT JOIN base_tp_up07 Q ON A.GRUPO = Q.GRUPO
                LEFT JOIN base_tp_low03 R ON A.GRUPO = R.GRUPO
                LEFT JOIN base_tp_up03 S ON A.GRUPO = S.GRUPO
                LEFT JOIN base_tp_medio1 t ON A.GRUPO = T.GRUPO
                                              ),


relatorio_v2 AS (SELECT data, idscript, GRUPO, BASE, tentativas, cpf, CASE WHEN atendimentos IS NULL THEN 0 ELSE atendimentos END AS atendimentos, custo, telefones,
                CASE WHEN FINAL IS NULL THEN 0 ELSE FINAL END AS FINAL,
                CASE WHEN completo      IS NULL THEN 0 ELSE completo    END AS completo,
                badphone, telefonia, machine, block, custo_sms,
                CASE WHEN tempo_0_9     IS NULL THEN 0 ELSE tempo_0_9   END AS tempo_0_9,
                CASE WHEN tempo_10      IS NULL THEN 0 ELSE tempo_10    END AS tempo_10,
                CASE WHEN LOW_07        IS NULL THEN 0 ELSE LOW_07      END AS LOW_07,
                CASE WHEN UP_07         IS NULL THEN 0 ELSE UP_07       END AS UP_07 ,
                CASE WHEN LOW_03        IS NULL THEN 0 ELSE LOW_03      END AS LOW_03,
                CASE WHEN UP_03         IS NULL THEN 0 ELSE UP_03       END AS UP_03 ,
                CASE WHEN tempo_medio   IS NULL THEN 0 ELSE tempo_medio END AS tempo_medio,
                CASE WHEN tempo_medio_gol IS NULL THEN 0 ELSE tempo_medio_gol END AS tempo_medio_gol

                    FROM RELATORIO),


relatorio_v3 AS (SELECT data, idscript, GRUPO, BASE, tentativas, cpf, (atendimentos + final) AS atendimentos,
                        FINAL, completo, telefones, badphone, telefonia, machine, block, custo, custo_sms,
                        tempo_0_9, tempo_10, LOW_07, UP_07, LOW_03, UP_03, tempo_medio, tempo_medio_gol

                FROM relatorio_v2),

nomes_v1 AS (SELECT DISTINCT substr(DATA, 1, 10) AS data, IDSCRIPT, GRUPO, base, script FROM base_geral2),
nomes_v2 AS (SELECT ROW_NUMBER() OVER (PARTITION BY GRUPO ORDER BY GRUPO) AS rownumber, nomes_v1.* FROM nomes_v1),
nomes_v3 AS (SELECT * FROM nomes_v2 WHERE rownumber = 1),


relatorio_v4 AS ( SELECT substr(a.DATA, 1, 10) AS DATA, d.cliente AS CLIENTE, a.grupo as grupo, a.idscript AS Idscript, a.BASE AS BASE, b.script as script,
                         d.tronco, a.tentativas AS Tentativas, a.cpf AS Qtd_cpf,
                         CASE when a.cpf = '0' THEN '0' ELSE substr((a.tentativas / a.cpf), 1, 4) end AS qtd_tentativas_cpf,
                         a.telefones AS qtd_telefones_dia, a.atendimentos AS Atendimentos,
                         c.atendimentos AS deslig_manual, CASE when a.cpf = '0' THEN '0' ELSE ((substr(((a.atendimentos / a.cpf)*100), 1, 4))||'%') END AS atend_docs_dia,
                         a.telefonia AS tentativa_improdutiva, a.machine AS machine,
                         a.badphone AS badphone, a.FINAL AS Sucesso, a.completo as completo, a.block AS block,
                         a.custo AS custo_acao, a.custo_sms as custo_sms,
                         a.tempo_0_9 as tempo_0_9, a.tempo_10 as tempo_10, A.LOW_07 AS LOW_07, A.UP_07 AS UP_07, A.LOW_03 AS LOW_03, A.UP_03 AS UP_03,
                         a.tempo_medio as tempo_medio, a.tempo_medio_gol as tempo_medio_gol

                  FROM relatorio_v3 a
                      inner join  nomes_v3 b on a.GRUPO = b.GRUPO
                      inner JOIN base_atendimentos c ON a.GRUPO = c.GRUPO
                      inner JOIN PANEAS_OWNER.TRONCOS d ON a.idscript = d.IDSCRIPT),

base_formato as ( select DATA, CLIENTE, Idscript, grupo, BASE, script, TRONCO, Qtd_cpf, qtd_telefones_dia, tentativas, Atendimentos, deslig_manual, Sucesso,
                         completo, atend_docs_dia, qtd_tentativas_cpf, tentativa_improdutiva, machine, badphone, block, custo_acao, custo_sms,
                         tempo_0_9, tempo_10, LOW_07, UP_07, LOW_03, UP_03, SUBSTR(tempo_medio, 1, 4) AS TEMPO_MEDIO, SUBSTR(tempo_medio_gol, 1, 4) AS TEMPO_MEDIO_GOL

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
        # Formata e limpa os dados antes de escrever no CSV
        iten = '\n' + str(iten)
        iten = iten.replace(')', '').replace('(', '').replace(',', ';').replace('.csv', '').replace('None', '').replace(
            '.', ',').replace("'", '').replace(' ', '')
        file.write(iten)

    file.close()
    dt_inicio += datetime.timedelta(days=1)  # Avança um dia no loop
    print(str(dt_inicio))
