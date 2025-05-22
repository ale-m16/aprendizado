import cx_Oracle as cx  # Importa a biblioteca cx_Oracle para conectar ao banco de dados Oracle

def db_connect():
    return cx.connect('USER/PASSWORD@HOST/SERVICE')  # Função que retorna uma conexão com o banco Oracle

# Solicita ao usuário os dados de entrada
ids = int(input('Digite aqui o numero do IDSCRIPT: '))
dd = str(input('Digite o dia: '))
mm = str(input('Digite o mês: '))
aaaa = str(input('Digite o ano: '))

# Formata a data no padrão YYYY-MM-DD
data = f'{aaaa}-{mm}-{dd}'

# Define o nome do arquivo de saída com base no idscript e na data
arq = f'{ids}_{data}.csv'

# Cria o arquivo e escreve o cabeçalho das colunas
file = open(arq, 'w')
file.write('idexec; idscript; script; campanha; cpf; nome; data; tipochamada; tempo; telefone; fluxo; st; fluxo_out; st_out; arquivooriginal; audio; contrato; respostas\n')
file.close()

print(f'Nome de saída do arquivo: {arq}')
print('Executando comando....')

# Monta a consulta SQL para buscar os registros daquele script e data
command = f"SELECT * FROM discador_owner.dialercalls WHERE IDSCRIPT = '{ids}' AND substr(DATA, 1, 10) = '{data}'"

# Conecta ao banco, executa a query e busca os dados
con = db_connect()
cur = con.cursor()
cur.execute(command)
dados = cur.fetchall()
con.close()  # ← atenção: essa linha não está chamando a função corretamente

print(dados)
print('Inicio de tratamento dos dados:...')

# Abre novamente o arquivo para adicionar os dados tratados
file = open(arq, 'a')

# Itera sobre os dados retornados do banco
for i in range(len(dados)):
    print(f'Tratando dados: ({i})...')
    iten = dados[i]
    iten = str(iten) + '\n'  # Converte a tupla em string e adiciona quebra de linha
    # Realiza substituições para formatar como CSV
    iten = iten.replace('(', '').replace(')', '').replace(',', ';').replace("'", "").replace('.', ',')
    print(f'Guardando dado ({i}) no arquivo: "{arq}" ...')
    file.write(iten)

print('Fim do processamento. fechando arquivo aguarde...')
file.close()

print("""PROCESSO FINALIZADO!""")
