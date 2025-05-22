# Relatório de Ações por Grupo - Oracle Dialer

Este script coleta diariamente registros de chamadas de um sistema baseado em Oracle e gera um relatório consolidado agrupado por `grupo`, `script` e `base`, contendo métricas operacionais e de custo.

---

## ✅ Funcionalidades

- Conecta-se ao banco Oracle via `cx_Oracle`.
- Executa uma query SQL estruturada com múltiplos CTEs (common table expressions).
- Gera um relatório `.csv` diário com dados por grupo de acionamento.
- Calcula estatísticas como:
  - Qtd. de CPFs, telefones, tentativas, atendimentos, falhas
  - Custo por ligação e SMS

---

## 🧾 Estrutura do CSV gerado

O arquivo gerado possui colunas como:

- `DATA`, `CLIENTE`, `IDSCRIPT`, `GRUPO`, `BASE`, `SCRIPT`, `TRONCO`
- `QTD_CPF_DIA`, `QTD_TELEFONES_DIA`, `TENTATIVAS`, `ATENDIMENTOS`, `BADPHONE`
- `CUSTO_ACAO`, `CUSTO_SMS`, `TENTATIVA_IMPRODUT`, `MACHINE`, `BLOCK`

---

## 🛠️ Requisitos

- Python 3.8+
- cx_Oracle
- Oracle Client (InstantClient recomendado)

---

## 🚀 Como usar

1. Atualize a string de conexão na função `db_connect()`:
   ```python
   return cx_Oracle.connect('usuario/senha@host/servico')
   ```

2. Execute o script:
   ```bash
   python relatorio_base_grupo.py
   ```

3. O CSV será salvo na pasta:
   ```
   relatorio/geral/
   ```

---

## 📦 Saída esperada

Exemplo de nome do arquivo de saída:
```
relatorio_acion_base_grupo_2023-08-01_2024-05-22.csv
```

---

## 🔐 Segurança

Evite colocar credenciais fixas em produção. Utilize variáveis de ambiente ou `.env`.

---

## 👨‍💻 Autor

Este script foi desenvolvido para fins de análise de campanhas e desempenho de discagens em contextos corporativos.
