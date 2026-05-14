# Banco de Dados — SmartTicket DB

> **Disciplina:** Banco de Dados  
> **Aluno:** Lucas Marques Maciel  
> **Instituição:** Universidade Evangélica de Goiás — UNIEVANGÉLICA  
> **Ano:** 2026

---

## Sobre este Trabalho

Trabalho acadêmico da disciplina de Banco de Dados, composto por relatório acadêmico em HTML/CSS (padrão ABNT), protótipo funcional em Python e diagramas explicativos. O tema central é a integração entre banco de dados relacional (SQL) e banco de dados não relacional (NoSQL documental), demonstrada por meio do protótipo **SmartTicket DB** — um sistema de gestão de chamados de suporte.

### Conceitos abordados

- Arquitetura de SGBD ANSI/SPARC (nível interno, conceitual e externo)
- Transações, COMMIT e ROLLBACK
- Propriedades ACID (Atomicidade, Consistência, Isolamento, Durabilidade)
- Controle de concorrência (threading.Lock como simulação de bloqueio 2PL)
- Recuperação de falhas (logs, undo, redo)
- Segurança e DCL (GRANT/REVOKE simulados via perfis de aplicação)
- Integridade referencial (chaves estrangeiras, PRAGMA foreign_keys)
- Bancos de dados distribuídos (Teorema CAP, PACELC, replicação)
- Bancos de dados móveis (sincronização offline, cache local)
- NoSQL documental (MongoDB/Firebase/Firestore — simulado via JSON)
- MapReduce conceitual (contagem de eventos por tipo)

---

## Estrutura da Pasta

```
Relatório-Banco-De-Dados/
├── index.html           ← Relatório acadêmico (abrir no navegador → Ctrl+P → PDF)
├── style.css            ← Estilo ABNT (A4, Times New Roman, margens ABNT)
├── README.md            ← Este arquivo
├── base.txt             ← Base teórica de referência utilizada na elaboração
└── smartticket-db/      ← Protótipo funcional em Python
    ├── main.py
    ├── database_sql.py
    ├── database_nosql.py
    ├── auth.py
    ├── concurrency_demo.py
    ├── seed.py
    ├── README.md
    ├── RELATORIO_TECNICO.md
    ├── data/
    └── diagrams/
```

---

## Como visualizar o relatório

1. Abra `index.html` no Google Chrome ou Microsoft Edge.
2. Para exportar como PDF: `Ctrl+P` → Destino: **Salvar como PDF** → Papel: A4 → Orientação: Retrato → Margens: **Nenhuma** → Desmarcar cabeçalhos e rodapés → Salvar.

## Como executar o protótipo

```bash
cd smartticket-db
python main.py
```

Não são necessárias bibliotecas externas. Requer Python 3.10 ou superior.

---

Para mais detalhes sobre o protótipo, consulte o [`smartticket-db/README.md`](smartticket-db/README.md).
