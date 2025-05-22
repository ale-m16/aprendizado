# 📊 Relatório de Discagens - Script de Extração Oracle

Este script Python conecta-se a uma base Oracle, executa uma consulta SQL com múltiplas CTEs e gera um relatório diário de tentativas e resultados de chamadas telefônicas, salvando os dados em um arquivo CSV.

---

## 🔧 O que o script faz?

- Conecta ao banco Oracle usando `cx_Oracle`.
- Gera um relatório por dia (de 01/01/2025 até ontem).
- Executa uma consulta SQL com diversas métricas como:
  - Tentativas de chamadas
  - Atendimentos
  - Máquinas detectadas
  - Telefones inválidos
  - Custos (ligações e SMS)
  - Tempos médios de atendimento
- Exporta o resultado para um arquivo `.csv`.

---

## 📂 Estrutura do Arquivo CSV

As colunas exportadas são:

```
DATA;CLIENTE;IDSCRIPT;GRUPO;BASE;SCRIPT;TRONCO;QTD_CPF_DIA;QTD_TELEFONES_DIA;TENTATIVAS;ATENDIMENTOS;
DELIGAMENTO_MANUAL;GOL;DESLIG_AUTOMATICO;ATEND_DOCS_DIA;QTD_TENTATIVAS_CPF;TENTATIVA_IMPRODUT;MACHINE;
BADPHONE;BLOCK;CUSTO_ACAO;CUSTO_SMS;tempo_0_9;tempo_10;LOW_07;UP_07;LOW_03;UP_03;tempo_medio;tempo_medio_GOL
```

---

## ▶️ Como usar

1. Altere a string de conexão no método `db_connect()`:
   ```python
   return cx_Oracle.connect('USER/PASSWORD@HOST/SERVICE')
   ```

2. Certifique-se de que o caminho de rede (`\\SERVIDOR\Users\...`) esteja acessível.

3. Execute o script:
   ```bash
   python relatorio_discagens.py
   ```

4. O relatório será salvo automaticamente no diretório especificado.

---

## 📦 Requisitos

Verifique as dependências no arquivo `requirements-relatorio_discagens.txt`.

---

## 🧱 Dependências do banco

- Tabelas:
  - `DISCADOR_OWNER.DIALERCALLS_FULL`
  - `PANEAS_OWNER.TRONCOS`

---

## 📌 Observações

- O script pode levar tempo para processar muitos dias.
- Ideal para rodar em ambiente de agendamento (como `cron` ou Agendador de Tarefas do Windows).
- O SQL usa muitas CTEs para organizar métricas específicas por grupo, script e base.

---

## 📝 Licença

Uso interno. Adaptável sob demanda.
