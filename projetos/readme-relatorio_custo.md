# 💰 Relatório de Custos - Extração Oracle

Este script Python conecta-se a um banco de dados Oracle, executa uma consulta SQL e gera um relatório com os dados de custo de chamadas e SMS, salvando os dados em um arquivo CSV diário.

---

## 🔧 O que o script faz?

- Conecta ao banco Oracle usando `cx_Oracle`.
- Gera um relatório por dia (de 01/07/2023 até ontem).
- Calcula métricas de custo por `IDSCRIPT`, incluindo:
  - Tempo total de chamadas
  - Tempo médio
  - Custo de ação (baseado no tempo)
  - Custo de envio de SMS
- Exporta os resultados para um arquivo `.csv`.

---

## 📂 Estrutura do Arquivo CSV

As colunas exportadas são:

```
DATA;CLIENTE;IDSCRIPT;TRONCO;TEMPO;TEMPO_MEDIO;CUSTO_ACAO;CUSTO_SMS
```

---

## ▶️ Como usar

1. Edite a função `db_connect()` para refletir as credenciais e o serviço do seu banco:
   ```python
   return cx_Oracle.connect('USER/PASSWORD@HOST/SERVICE')
   ```

2. Execute o script:
   ```bash
   python relatorio_custo.py
   ```

3. O arquivo será salvo na pasta `relatorio/`, com nome contendo o intervalo de datas.

---

## 📦 Requisitos

Verifique o arquivo `requirements-relatorio_custo.txt` para as dependências.

---

## 🧱 Dependências do banco

- Tabelas:
  - `DISCADOR_OWNER.DIALERCALLS_FULL`
  - `PANEAS_OWNER.TRONCOS`

---

## 📝 Licença

Uso interno. Adaptável sob demanda.
