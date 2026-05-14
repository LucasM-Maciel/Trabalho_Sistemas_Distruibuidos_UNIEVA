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

### 3. Banco de Dados ⏳ *em breve*

**Pasta:** a ser criada  
**Disciplina:** Banco de Dados

> Este trabalho ainda não está disponível neste repositório.

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
│   ├── 📄 README.md                                  ← Detalhes do trabalho
│   ├── 🐍 server.py
│   ├── 🐍 client.py
│   ├── 🌐 index.html
│   ├── 🎨 style.css
│   └── 🖼️ fig1.svg / fig2.svg / fig3.svg
│
└── 📁 Trabalho_Empreendedorismo_Inovação_Unieva/     ← Trabalho 2 — Empreendedorismo
    ├── 📄 README.md                                  ← Detalhes do trabalho
    ├── 🌐 index.html
    ├── 🎨 style.css
    └── 📄 copia.txt
```
