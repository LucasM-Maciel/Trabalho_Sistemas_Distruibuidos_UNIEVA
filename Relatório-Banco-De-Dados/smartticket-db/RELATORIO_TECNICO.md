# Relatório Técnico — SmartTicket DB

**Disciplina:** Banco de Dados  
**Aluno:** Lucas Marques Maciel  
**Instituição:** Universidade Evangélica de Goiás — UNIEVANGÉLICA  
**Ano:** 2026

---

## 1. Objetivo do Protótipo

O SmartTicket DB é um protótipo acadêmico de sistema de gestão de chamados (tickets de suporte), desenvolvido em Python com SQLite e JSON local. O objetivo é demonstrar, de forma executável e didática, a integração entre uma camada relacional (SQL) e uma camada documental (NoSQL), cobrindo os principais conceitos exigidos pela disciplina de Banco de Dados: propriedades ACID, transações, controle de concorrência, segurança e integridade, bancos distribuídos e móveis, e MapReduce conceitual.

---

## 2. Arquitetura Geral do Sistema

O sistema é composto por duas camadas de persistência:

**Camada SQL (SQLite):** responsável pelos dados estruturados e transacionais. Armazena perfis de usuário, cadastros, chamados e logs relacionais. Garante integridade referencial via chaves estrangeiras e executa operações com as propriedades ACID completas.

**Camada NoSQL Documental (JSON):** responsável pelos eventos flexíveis associados a cada chamado. Armazena logs de criação, mudanças de status, tentativas de acesso negado, atualizações offline e eventos de sincronização mobile. Em ambiente de produção, esta camada seria implementada com MongoDB, Firebase ou Firestore.

A separação entre as camadas reflete um padrão arquitetural comum em sistemas modernos: dados transacionais em SGBD relacional, logs e eventos em banco documental de alta disponibilidade.

---

## 3. Modelagem SQL

O modelo relacional é composto por quatro tabelas:

**perfis:** armazena os papéis do sistema (admin, tecnico, cliente). Equivale a roles em SGBDs como PostgreSQL.

**usuarios:** armazena os usuários vinculados a perfis. A chave estrangeira `id_perfil → perfis.id_perfil` garante que todo usuário possui um perfil válido.

**chamados:** armazena os tickets de suporte. A chave estrangeira `id_usuario → usuarios.id_usuario` garante que todo chamado pertence a um usuário existente. O campo `status` registra o ciclo de vida: aberto → em atendimento → resolvido.

**logs_sql:** registra ações relevantes sobre chamados, formando uma trilha de auditoria relacional. A chave estrangeira `id_chamado → chamados.id_chamado` mantém a rastreabilidade.

A instrução `PRAGMA foreign_keys = ON` é executada em toda conexão, ativando a verificação de integridade referencial no SQLite, que por padrão a desabilita para compatibilidade histórica.

---

## 4. Modelagem NoSQL

A coleção `eventos_chamado` no arquivo JSON segue o modelo documental: cada documento é um objeto JSON independente com os campos `id_evento`, `id_chamado`, `tipo`, `origem`, `timestamp` e `dados`.

O campo `dados` é completamente flexível (schema-less), permitindo que diferentes tipos de evento coexistam na mesma coleção sem alteração de estrutura. Um evento de `criacao_chamado` carrega título e status inicial; um evento de `sincronizacao_mobile` carrega informações de conectividade e resolução de conflitos; um evento de `acesso_negado` carrega o perfil do usuário e a ação tentada.

Esta flexibilidade é a principal característica que diferencia bancos documentais dos relacionais e justifica seu uso para logs, histórico de alterações e eventos de aplicação.

---

## 5. Demonstração de Transações e Propriedades ACID

A abertura de um chamado é implementada como uma transação atômica: o sistema insere o registro na tabela `chamados` e, na mesma transação, insere o log correspondente em `logs_sql`. Se qualquer etapa falha, o `ROLLBACK` desfaz todas as operações — nenhum dado parcial persiste no banco.

As propriedades ACID são demonstradas individualmente:

- **Atomicidade:** a função `abrir_chamado(simular_erro=True)` lança uma exceção intencionalmente após a inserção do chamado, antes da inserção do log. O `ROLLBACK` garante que nenhum registro parcial persiste.

- **Consistência:** a tentativa de criar um chamado para um `id_usuario` inexistente é rejeitada pela restrição de chave estrangeira, mantendo o banco em estado válido.

- **Isolamento:** duas threads tentam atualizar o mesmo chamado simultaneamente. O `threading.Lock` serializa o acesso, evitando condições de corrida. Em um SGBD completo, este controle seria implementado pelo protocolo de bloqueio em duas fases (2PL — *Two-Phase Locking*).

- **Durabilidade:** após o `COMMIT`, os dados persistem no arquivo `.db` e no JSON mesmo que o processo Python seja encerrado imediatamente. A execução repetida do `main.py` (sem limpeza prévia) preservaria todos os dados da execução anterior.

---

## 6. Controle de Acesso e DCL

Em SGBDs relacionais completos, a DCL (*Data Control Language*) controla o acesso por meio dos comandos `GRANT` (conceder privilégios) e `REVOKE` (revogar privilégios), aplicados a usuários ou papéis (*roles*).

Exemplo em PostgreSQL:
```sql
GRANT SELECT, UPDATE ON chamados TO role_tecnico;
REVOKE DELETE ON chamados FROM role_cliente;
```

Como o SQLite não implementa gerenciamento de usuários e papéis da mesma forma, o protótipo simula esta lógica na camada de aplicação por meio do módulo `auth.py`. Cada perfil possui um conjunto de ações permitidas, e a função `verificar_permissao(perfil, acao)` atua como o mecanismo de controle que, em ambiente real, seria executado pelo SGBD antes de processar qualquer comando SQL.

Tentativas de acesso negado são registradas como eventos documentais no banco NoSQL, formando uma trilha de auditoria de segurança.

---

## 7. Integridade Referencial

A ativação de `PRAGMA foreign_keys = ON` no SQLite habilita a verificação de integridade referencial em todas as operações DML. O protótipo demonstra esta funcionalidade ao tentar criar um chamado vinculado a um usuário com ID inexistente: o SGBD rejeita a operação com `IntegrityError` e executa `ROLLBACK` automático, garantindo que a tabela `chamados` nunca contenha referências inválidas.

---

## 8. Controle de Concorrência

O controle de concorrência é implementado em `concurrency_demo.py` por meio de `threading.Lock`. Duas threads representando dois técnicos tentam atualizar o mesmo chamado simultaneamente. O `Lock` garante exclusão mútua: apenas uma thread por vez executa a seção crítica (leitura + escrita), evitando o problema de **atualização perdida** (*lost update*).

Em SGBDs de produção, o controle de concorrência é implementado pelo próprio SGBD através de protocolos como o bloqueio em duas fases (2PL) ou controle de concorrência por versão múltipla (MVCC — *Multi-Version Concurrency Control*), utilizado pelo PostgreSQL. O `threading.Lock` é uma analogia funcional que permite demonstrar o conceito de forma visível e controlada.

---

## 9. Sincronização Mobile

O protótipo simula o comportamento de bancos de dados móveis por meio de eventos NoSQL documentais. Um técnico de campo registra um diagnóstico sem conexão à internet (`atualizacao_offline`), e posteriormente o evento de sincronização com o servidor central (`sincronizacao_mobile`) é registrado com informações sobre resolução de conflitos.

Este comportamento é análogo ao oferecido pelo Firebase Firestore com persistência offline habilitada, em que o SDK armazena operações pendentes em cache local e as sincroniza automaticamente quando a conectividade é restabelecida, resolvendo conflitos por estratégia de *last-write-wins* ou por lógica customizada da aplicação (GOOGLE, 2026).

---

## 10. MapReduce Conceitual

A função `mapreduce_contar_por_tipo()` em `database_nosql.py` implementa uma analogia ao paradigma MapReduce em escala local:

- **Fase MAP:** cada documento da coleção é processado individualmente para extração do campo `tipo`.
- **Fase REDUCE:** os valores extraídos são agregados por chave, somando as ocorrências de cada tipo de evento.

Em plataformas distribuídas como Hadoop ou Spark, este mesmo padrão é executado em paralelo sobre partições de dados distribuídas em centenas de nós, permitindo o processamento de terabytes de documentos em minutos. O paradigma MapReduce é especialmente relevante para análise de logs em larga escala, que é exatamente o caso de uso simulado neste protótipo.

---

## 11. Relação com o Estudo de Caso de Delivery/Atendimento

A arquitetura do SmartTicket DB é diretamente análoga à de sistemas de atendimento e delivery como iFood ou UberEats:

- **Camada SQL transacional:** pedidos, pagamentos e transações financeiras exigem ACID rigoroso. Uma cobrança duplicada ou um pedido sem entregador vinculado são inaceitáveis — equivalem a chamados sem usuário válido no protótipo.

- **Camada NoSQL documental:** milhões de eventos de geolocalização, logs do aplicativo e mensagens entre usuários são registrados em bancos documentais de alta disponibilidade. Estes dados têm schema variável e volume incompatível com um modelo relacional rígido.

- **Concorrência:** dois entregadores aceitando o mesmo pedido simultaneamente é o equivalente exato a dois técnicos atualizando o mesmo chamado. O controle de bloqueio resolve o conflito da mesma forma.

- **Sincronização mobile:** entregadores frequentemente passam por áreas sem sinal. O aplicativo usa cache local (Firebase/Firestore) e sincroniza quando a rede retorna — comportamento diretamente simulado pelos eventos `atualizacao_offline` e `sincronizacao_mobile` do protótipo.

---

## 12. Conclusão Técnica

O SmartTicket DB demonstra que os conceitos fundamentais de banco de dados podem ser implementados de forma didática e executável com tecnologias simples (SQLite + JSON + Python). A separação entre camada SQL transacional e camada NoSQL documental reflete padrões arquiteturais reais amplamente adotados pela indústria. As demonstrações de ACID, integridade referencial, controle de concorrência, DCL por perfis e sincronização mobile cobrem o escopo completo exigido pela disciplina, com código legível, comentado e sem dependências externas.
