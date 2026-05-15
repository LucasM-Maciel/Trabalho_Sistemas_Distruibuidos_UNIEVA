# SmartTicket DB — Protótipo Acadêmico de Banco de Dados

> **Disciplina:** Banco de Dados — UNIEVANGÉLICA 2026  
> **Aluno:** Lucas Marques Maciel  
> **Objetivo:** Demonstrar, de forma didática, os principais conceitos de banco de dados relacionais, NoSQL, transações ACID, controle de concorrência, DCL e bancos móveis.

---

## Tecnologias Utilizadas

| Componente | Tecnologia | Justificativa |
|---|---|---|
| Banco SQL | **SQLite** (Python `sqlite3`) | Simples, local, sem configuração; representa a camada transacional |
| Banco NoSQL | **JSON local** (Python `json`) | Simula banco documental (MongoDB/Firestore) sem dependências externas |
| Controle de concorrência | **`threading.Lock`** | Simula bloqueio (lock) do SGBD |
| Linguagem | **Python 3** | Bibliotecas padrão — sem dependências externas |

> **Nota importante:** O arquivo JSON simula didaticamente um banco NoSQL documental.  
> Em ambiente real, este módulo seria substituído por **MongoDB** (`pymongo`), **Firebase** ou **Firestore** (`firebase-admin`).  
> O SQLite **não implementa DCL completa** (GRANT/REVOKE) como PostgreSQL ou MySQL. A lógica de controle de acesso é simulada na camada de aplicação em `auth.py`.

---

## Estrutura do Projeto

```
smartticket-db/
├── main.py               ← Demonstração completa (execute este arquivo)
├── database_sql.py       ← Camada SQL: SQLite, transações, ACID, integridade
├── database_nosql.py     ← Camada NoSQL: JSON, eventos documentais, MapReduce
├── auth.py               ← Controle de acesso por perfil (simulação de DCL)
├── concurrency_demo.py   ← Simulação de concorrência com threading.Lock
├── seed.py               ← Dados iniciais (perfis e usuários)
├── README.md             ← Este arquivo
├── RELATORIO_TECNICO.md  ← Texto técnico para uso no relatório acadêmico
├── data/
│   ├── smartticket.db         ← Banco SQLite (gerado ao executar main.py)
│   └── eventos_chamados.json  ← "Banco NoSQL" (gerado ao executar main.py)
└── diagrams/
    ├── arquitetura_geral.mmd
    ├── modelo_sql.mmd
    ├── estrutura_nosql.mmd
    ├── fluxo_transacao.mmd
    └── controle_acesso.mmd
```

Os arquivos em `data/` (`smartticket.db` e `eventos_chamados.json`) são **gerados localmente** ao rodar `main.py`; no repositório, entram em `.gitignore` na raiz do projeto para não versionar dados de execução.

---

## Como Executar

```bash
# A partir da pasta smartticket-db/
python main.py
```

Não são necessárias bibliotecas externas. Os arquivos `smartticket.db` e `eventos_chamados.json` são criados automaticamente em `data/`.

---

## Conceitos Demonstrados

### Banco SQL (SQLite)
O SQLite representa a camada relacional e transacional do sistema. Armazena dados estruturados: perfis, usuários, chamados e logs. Todas as operações de escrita usam transações explícitas com `COMMIT` e `ROLLBACK`.

### Banco NoSQL Documental (JSON)
O arquivo `eventos_chamados.json` simula uma coleção de banco NoSQL orientado a documentos. Cada evento é um documento JSON com schema flexível — tipos de evento diferentes convivem na mesma coleção, demonstrando a principal vantagem do modelo documental.

### Propriedades ACID

| Propriedade | Como é demonstrada |
|---|---|
| **Atomicidade** | `abrir_chamado(simular_erro=True)` → ROLLBACK desfaz tudo |
| **Consistência** | FOREIGN KEY impede chamado para usuário inexistente |
| **Isolamento** | `threading.Lock` serializa acessos simultâneos ao mesmo chamado |
| **Durabilidade** | Dados confirmados via COMMIT persistem no `.db` após encerramento |

### COMMIT e ROLLBACK
Ao abrir um chamado, o sistema insere dois registros na mesma transação (chamado + log SQL). Se qualquer etapa falha, `ROLLBACK` garante que nenhum dado parcial persiste — demonstrando Atomicidade.

### DCL / Controle de Acesso (GRANT e REVOKE)
O módulo `auth.py` define uma matriz de permissões por perfil, simulando o comportamento de `GRANT` e `REVOKE` na camada de aplicação:

```python
# Equivale a: GRANT SELECT, UPDATE ON chamados TO role_tecnico;
"tecnico": {"abrir_chamado", "consultar_chamado", "atualizar_status"}

# Equivale a: REVOKE resolver_chamado FROM role_cliente;
"cliente": {"abrir_chamado", "consultar_chamado"}
```

Tentativas não autorizadas (por exemplo `resolver_chamado` ou `atualizar_status` com perfil **cliente**) são bloqueadas e registradas como `acesso_negado` no JSON. Clientes só **consultam** os próprios chamados (`consultar_chamado` + `listar_chamados_por_usuario`) e podem registrar eventos tipo **`mensagem`** no NoSQL.

### Integridade Referencial
`PRAGMA foreign_keys = ON` ativa as restrições de chave estrangeira no SQLite. Tentar criar um chamado para um `id_usuario` inexistente gera `IntegrityError` e aciona ROLLBACK automático.

### Controle de Concorrência
`concurrency_demo.py` lança duas threads simultâneas (`Técnico João` e `Técnica Maria`) tentando atualizar o mesmo chamado. O `threading.Lock` garante que apenas uma thread por vez executa a seção crítica, evitando o problema de **atualização perdida** (*lost update*).

### Sincronização Mobile
O sistema registra eventos do tipo `atualizacao_offline` e `sincronizacao_mobile` no banco NoSQL, simulando o comportamento de bancos móveis como Firebase/Firestore: o técnico registra dados sem conexão, e a sincronização ocorre quando a rede é restabelecida.

### MapReduce Conceitual
A função `mapreduce_contar_por_tipo()` em `database_nosql.py` conta eventos por tipo:
- **Fase MAP:** extrai o campo `tipo` de cada documento da coleção.
- **Fase REDUCE:** soma as ocorrências por tipo.

Esta operação é uma analogia simplificada ao paradigma MapReduce (Hadoop/Spark), que em produção processaria bilhões de documentos em cluster distribuído.

---

## Saída Esperada

```
════════════════════════════════════════════════════════════
         SmartTicket DB — Protótipo Acadêmico
         Banco de Dados — UNIEVANGÉLICA 2026
════════════════════════════════════════════════════════════

  1. INICIALIZAÇÃO DO BANCO
✔ Banco SQL inicializado (SQLite + PRAGMA foreign_keys = ON)
✔ Perfis criados:  admin, tecnico, cliente
✔ Usuários criados: Admin Sistema, Técnico João, Técnica Maria, Cliente Lucas

  2. ABERTURA DE CHAMADO — COMMIT
✔ Chamado #1 aberto com sucesso.
  → COMMIT confirmado: dados persistidos no SQLite (Durabilidade).

  3. FALHA SIMULADA — ROLLBACK
✘ Erro capturado: Falha simulada para demonstrar ROLLBACK
  → ROLLBACK executado: nenhum dado parcial foi salvo (Atomicidade).

  4. INTEGRIDADE REFERENCIAL
✘ SGBD bloqueou a operação: IntegrityError
  → FOREIGN KEY violation: chamados.id_usuario → usuarios.id_usuario

  5. CONTROLE DE ACESSO — Simulação de DCL
✔ perfil='admin' + acao='administrar' → PERMITIDO
✔ perfil='tecnico' + acao='atualizar_status' → PERMITIDO
✔ perfil='cliente' + acao='resolver_chamado' → NEGADO

  7. CONTROLE DE CONCORRÊNCIA — threading.Lock
  [Técnico João]  Bloqueio adquirido — atualizando para 'em atendimento'
  [Técnica Maria] Esperando... bloqueio adquirido em seguida.
  Nenhuma atualização foi perdida graças ao controle de concorrência.

  9. MapReduce Conceitual
  criacao_chamado     █ (1)
  atualizacao_concorrente ██ (2)
  sincronizacao_mobile █ (1)
  ...
  Total de eventos registrados: 12
```

---

## Observação Acadêmica

Este projeto é um **protótipo didático**, desenvolvido com fins exclusivamente acadêmicos. O objetivo é demonstrar os fundamentos de banco de dados de forma clara e executável, não criar um sistema pronto para produção. As simplificações (SQLite no lugar de PostgreSQL, JSON no lugar de MongoDB) são intencionais e devidamente documentadas.
