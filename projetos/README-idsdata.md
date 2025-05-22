# Exportador de Registros do Dialer Oracle

Este script realiza a **extração de registros de chamadas** da tabela `discador_owner.dialercalls` de um banco Oracle, baseado no número do `idscript` e na **data desejada**. Os dados são exportados para um arquivo `.csv`.

---

## ✅ Como funciona

1. Solicita ao usuário:
   - O número do `IDScript`
   - O dia, mês e ano desejados para a consulta
2. Constrói uma **consulta SQL** que filtra os registros por `IDScript` e por data (`substr(DATA, 1, 10)`)
3. Executa a consulta no banco Oracle
4. Cria um arquivo `.csv` com o nome no formato:  
