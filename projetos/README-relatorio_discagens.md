# Relatório de Discagens - Oracle Dialer Exporter

Este script coleta diariamente registros de chamadas de um sistema baseado em Oracle, gera um relatório consolidado com informações como tentativas, atendimentos, falhas, e exporta os dados para um arquivo `.csv`.

---

## ✅ Funcionalidades

- Conecta-se ao banco Oracle via `cx_Oracle`.
- Executa uma query complexa com múltiplos `CTE`s para calcular indicadores.
- Exporta os dados em formato CSV com cabeçalho fixo.
- Processa os dados desde uma data inicial definida até o dia anterior ao atual.

---

## 🧾 Estrutura do CSV gerado

Cada linha representa um resumo diário por script (campanha). Algumas colunas:

- `DATA`, `CLIENTE`, `CAMPANHA_IDSCRIPT`, `SCRIPT`
- `QTD_CPF`, `TENTATIVAS`, `ATENDIMENTOS`, `BADPHONE`, `BLOCK`, `MACHINE`
- `CUSTO_ACAO`, `CUSTO_RETORNO`, `RETORNO_FINANC` *(alguns campos podem estar vazios)*

---

## 🛠️ Requisitos

- Python 3.8+
- Oracle Client instalado (InstantClient recomendado)
- Acesso à base Oracle com permissões de leitura na tabela de chamadas

---

## 🚀 Como usar

1. Edite a string de conexão Oracle na função `db_connect()`:
   ```python
   return cx_Oracle.connect('usuario/senha@host/servico')
   ```

2. Execute o script:
   ```bash
   python relatorio_discagens.py
   ```

3. O arquivo será salvo em um diretório local conforme configurado no script.

---

## 📦 Saída esperada

Um arquivo `.csv` chamado:
```
relatorio_discagens_YYYY-MM-DD.csv
```

---

## 🔒 Segurança

Evite deixar credenciais hardcoded no código em produção. Utilize variáveis de ambiente ou um arquivo `.env`.

---

## 👨‍💻 Autor

Este script foi desenvolvido para uso em análise de discagens e pode ser adaptado a diferentes contextos corporativos ou acadêmicos.
