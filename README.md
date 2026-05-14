# Trabalhos Acadêmicos — UniEVANGÉLICA

**Instituição:** Universidade Evangélica de Goiás — UniEVANGÉLICA  
**Autor:** Lucas Marques Maciel  
**Ano:** 2026

---

## Visão Geral

Este repositório reúne os trabalhos acadêmicos do curso. Cada trabalho está organizado em sua própria pasta, com um `README.md` interno que detalha o conteúdo, os arquivos e as instruções específicas daquele projeto.

---

## Trabalhos

### 1. Sistemas Distribuídos e Redes de Computadores ✅

**Pasta:** [`relatorio-sistemas-distribuidos/`](./relatorio-sistemas-distribuidos/)  
**Disciplina:** Sistemas Distribuídos e Redes de Computadores

Trabalho composto por duas partes:

**Relatório Acadêmico (`index.html`)** — estudo teórico e analítico com os seguintes tópicos:
- Fundamentação teórica: transparência, escalabilidade, consistência, replicação e Arquitetura Orientada a Serviços (SOA)
- Estudo de caso do **Google Docs**: Transformação Operacional (OT), sincronização cliente-servidor, componentes do ecossistema Google (Bigtable, Chubby, Spanner)
- Proposta de arquitetura conceitual em camadas para aplicação colaborativa distribuída

**Implementação Prática (`server.py` + `client.py`)** — aplicação de chat distribuído em Python com:

| Conceito | Implementação |
|---|---|
| Arquitetura cliente-servidor | Topologia em estrela com servidor central TCP |
| Comunicação assíncrona | `threading.Thread` dedicada por conexão/recepção |
| Sincronização (Mutex) | `threading.Lock` protegendo o dicionário de clientes |
| Tolerância a falhas básica | Tratamento de exceções isolado por thread |

> Para detalhes completos, instruções de execução e exemplos, veja o [`README` da pasta](./relatorio-sistemas-distribuidos/README.md).

---

### 2. Empreendedorismo e Inovação ✅

**Pasta:** [`Trabalho_Empreendedorismo_Inovação_Unieva/`](./Trabalho_Empreendedorismo_Inovação_Unieva/)  
**Disciplina:** Empreendedorismo e Inovação

Relatório acadêmico em HTML com formatação ABNT, exportável como PDF, cobrindo:

- **Fundamentação Teórica:** perfil empreendedor (Schumpeter, 1942), distinção entre invenção, inovação e difusão (Rogers, 2003; OCDE, 2018), tipos de inovação (incremental, radical, disruptiva) e indicadores de esforço e resultado
- **Estudo de Caso — Nubank:** análise da inovação disruptiva no setor financeiro brasileiro, da infraestrutura em nuvem à democratização do crédito
- **Projeto Conceitual — SmartTicket:** proposta de plataforma de gestão de chamados baseada em IA, Machine Learning e NLP para automação da triagem de incidentes em ambientes corporativos de TI
- **Plano Esquemático:** tabela com 5 etapas de desenvolvimento, responsáveis, prazos, recursos e indicadores de acompanhamento

> Para detalhes completos, estrutura de arquivos e instruções de exportação em PDF, veja o [`README` da pasta](./Trabalho_Empreendedorismo_Inovação_Unieva/README.md).

---

### 3. Banco de Dados ✅

**Pasta:** [`Relatório-Banco-De-Dados/`](./Relatório-Banco-De-Dados/)  
**Disciplina:** Banco de Dados

Trabalho composto por relatório acadêmico em HTML/CSS (padrão ABNT) e protótipo funcional em Python. O tema central é a integração entre banco de dados relacional (SQL) e banco de dados não relacional (NoSQL documental), demonstrada pelo protótipo **SmartTicket DB** — sistema de gestão de chamados de suporte.

**Relatório Acadêmico (`index.html`)** — cobrindo:
- Arquitetura de SGBD ANSI/SPARC (nível interno, conceitual e externo) e independência de dados
- Transações, COMMIT e ROLLBACK; propriedades ACID
- Controle de concorrência (bloqueio 2PL, MVCC) e recuperação de falhas (WAL, undo/redo)
- Segurança, integridade referencial e DCL (GRANT, REVOKE)
- Bancos distribuídos (Teorema CAP, PACELC, replicação, fragmentação)
- Bancos móveis (sincronização offline, Firebase/Firestore) e paradigma NoSQL documental
- MapReduce conceitual; estudo de caso em sistemas de delivery

**Protótipo SmartTicket DB (`smartticket-db/`)** — implementado em Python com:

| Conceito | Implementação |
|---|---|
| Banco SQL transacional | SQLite com `PRAGMA foreign_keys = ON` |
| Banco NoSQL documental | Arquivo JSON (simula MongoDB/Firestore) |
| Transações ACID | `COMMIT` e `ROLLBACK` explícitos |
| Integridade referencial | Chaves estrangeiras entre 4 tabelas |
| Controle de acesso (DCL) | Matriz de permissões por perfil em `auth.py` |
| Controle de concorrência | `threading.Lock` (simulação de bloqueio 2PL) |
| Sincronização mobile | Eventos `atualizacao_offline` + `sincronizacao_mobile` |
| MapReduce | Contagem de eventos por tipo sobre coleção JSON |

> Para detalhes completos, estrutura de arquivos, instruções de execução e exemplo de saída, veja o [`README` da pasta](./Relatório-Banco-De-Dados/README.md).

---

## Estrutura do Repositório

```
📦 Trabalho_Sistemas_Distruibuidos_UNIEVA
│
├── 📄 README.md                                      ← Este arquivo
├── 📄 LICENSE
├── 📄 .gitignore
│
├── 📁 relatorio-sistemas-distribuidos/               ← Trabalho 1 — SD
│   ├── 📄 README.md
│   ├── 🐍 server.py
│   ├── 🐍 client.py
│   ├── 🌐 index.html
│   ├── 🎨 style.css
│   └── 🖼️ fig1.svg / fig2.svg / fig3.svg
│
├── 📁 Trabalho_Empreendedorismo_Inovação_Unieva/     ← Trabalho 2 — Empreendedorismo
│   ├── 📄 README.md
│   ├── 🌐 index.html
│   └── 🎨 style.css
│
└── 📁 Relatório-Banco-De-Dados/                      ← Trabalho 3 — Banco de Dados
    ├── 📄 README.md
    ├── 🌐 index.html
    ├── 🎨 style.css
    └── 📁 smartticket-db/
        ├── 🐍 main.py
        ├── 🐍 database_sql.py
        ├── 🐍 database_nosql.py
        ├── 🐍 auth.py
        ├── 🐍 concurrency_demo.py
        ├── 🐍 seed.py
        ├── 📄 README.md
        ├── 📄 RELATORIO_TECNICO.md
        ├── 📁 data/
        └── 📁 diagrams/
```
