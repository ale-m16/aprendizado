# 📞 Relatório de Acionamento - Extração Oracle

Este script conecta-se a uma base Oracle e gera um relatório consolidado das tentativas de discagem, atendimentos, falhas e custos, por dia, desde 06/03/2023 até o dia anterior ao atual.

---

## 🔧 O que o script faz?

- Conecta ao banco Oracle com `cx_Oracle`.
- Executa uma consulta SQL com múltiplas CTEs para:
  - Contar tentativas, atendimentos, falhas
  - Calcular custo por chamada
  - Consolidar em um relatório final com várias colunas relevantes
- Exporta os resultados em um arquivo CSV para cada dia processado.

---

## 📂 Estrutura do Arquivo CSV

As colunas exportadas incluem:

```
DATA; CLIENTE; CAMPANHA_IDSCRIPT; SCRIPT; CANAIS_TELEFONIA; SEGMENTOS_BASE; QTD_BASE; ...
TENTATIVAS; QTD_CPF; QTD_TENTATIVAS_CPF; ...; CUSTO_ACAO; RESULTADO
```

---

## ⚠️ Observação importante

> Há um erro na linha abaixo que precisa ser corrigido:
```python
hoje = datetime.datetime.today('YYYY-MM-DD')
```
A função `today()` não aceita formato como parâmetro. Use:
```python
hoje = datetime.datetime.today().strftime('%Y-%m-%d')
```

---

## ▶️ Como usar

1. Atualize a função `db_connect()` com as credenciais corretas:
```python
return cx_Oracle.connect('USER/PASSWORD@HOST/SERVICE')
```

2. Execute o script:
```bash
python relatorio_acionamento.py
```

3. Os dados serão salvos no diretório `relatorio1/` com um nome de arquivo baseado na data atual.

---

## 📦 Requisitos

Consulte `requirements-relatorio_acionamento.txt` para dependências.

---

## 🧱 Dependências do banco

- Tabelas:
  - `DISCADOR_OWNER.DIALERCALLS`
  - `PANEAS_OWNER.TRONCOS`

---

## 📝 Licença

Uso interno e adaptável conforme a necessidade.
