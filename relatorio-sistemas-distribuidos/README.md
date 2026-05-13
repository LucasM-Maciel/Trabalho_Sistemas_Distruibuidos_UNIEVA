# Chat Distribuído — Implementação Prática

**Disciplina:** Sistemas Distribuídos e Redes de Computadores  
**Autor:** Lucas Marques Maciel  
**Instituição:** Universidade Evangélica de Goiás — UniEVANGÉLICA  
**Ano:** 2026

---

## Objetivo do Projeto

Esta implementação materializa, em escala laboratorial, os conceitos centrais da disciplina de Sistemas Distribuídos. Trata-se de uma aplicação de troca de mensagens em tempo real (chat) construída sobre o protocolo TCP, utilizando exclusivamente a biblioteca padrão do Python (sem dependências externas).

Os conceitos demonstrados incluem:

- Arquitetura cliente-servidor
- Comunicação assíncrona via threads independentes
- Sincronização de recursos compartilhados com `threading.Lock` (Mutex)
- Tolerância básica a falhas por isolamento de exceções por thread

---

## Arquitetura Cliente-Servidor

O sistema segue o modelo clássico de topologia em **estrela**:

```
Cliente 1 ──┐
Cliente 2 ──┼──► Servidor Central (TCP) ──► redistribui para todos
Cliente N ──┘
```

- O **Servidor** (`server.py`) é o nó central: aguarda conexões, aceita múltiplos clientes simultaneamente e retransmite cada mensagem recebida para todos os demais participantes.
- Cada **Cliente** (`client.py`) conecta-se ao servidor, envia mensagens digitadas pelo usuário e recebe mensagens de outros participantes.

---

## Comunicação Assíncrona com Threads

A assincronia é implementada via `threading`:

**No servidor:**  
Para cada cliente que se conecta, uma nova `thread` é criada e dedicada exclusivamente a gerenciar aquela conexão. Isso permite que o servidor atenda múltiplos clientes em paralelo sem que uma conexão bloqueie as demais.

**No cliente:**  
Uma thread secundária fica responsável por escutar e exibir as mensagens recebidas do servidor, enquanto a thread principal captura as entradas do teclado do usuário e as envia. As duas operações ocorrem de forma verdadeiramente simultânea.

---

## Sincronização com `threading.Lock`

O servidor mantém um dicionário compartilhado `clientes = {}` que mapeia cada socket ao apelido do usuário. Como múltiplas threads acessam e modificam esse dicionário concorrentemente, utiliza-se um `threading.Lock` (Mutex) para garantir exclusão mútua:

```python
with lock:
    clientes[conn] = apelido   # adição protegida
```

```python
with lock:
    del clientes[conn]         # remoção protegida
```

```python
with lock:
    destinatarios = list(clientes.items())  # leitura protegida
```

Sem esse mecanismo, operações simultâneas poderiam corromper o estado interno do servidor (*race condition*).

---

## Arquivos da Entrega

| Arquivo        | Descrição                                          |
|----------------|----------------------------------------------------|
| `index.html`   | Relatório acadêmico completo em HTML               |
| `style.css`    | Estilo ABNT para o relatório (A4, Times New Roman) |
| `fig1.svg`     | Diagrama: arquitetura conceitual do Google Docs    |
| `fig2.svg`     | Diagrama: arquitetura cliente-servidor do chat     |
| `fig3.svg`     | Diagrama: sequência do fluxo de mensagens          |
| `server.py`    | Servidor TCP multithread                           |
| `client.py`    | Cliente TCP com thread de recepção                 |
| `README.md`    | Este arquivo de documentação                       |

---

## Pré-requisitos

- Python 3.7 ou superior
- Nenhuma biblioteca externa necessária (apenas biblioteca padrão)

---

## Como Executar

### 1. Iniciar o Servidor

Abra um terminal e execute:

```bash
python server.py
```

O servidor exibirá:
```
[Servidor] Aguardando conexões em 0.0.0.0:5000 ...
[Servidor] Pressione Ctrl+C para encerrar.
```

### 2. Conectar Clientes

Abra um **novo terminal** para cada cliente e execute:

```bash
python client.py
```

O cliente solicitará um apelido:
```
Digite seu apelido: Alice
```

Repita o processo em outro terminal para um segundo cliente (ex.: `Bob`).

---

---

## Exemplo de Uso

**Terminal 1 — Servidor:**
```
[Servidor] Aguardando conexões em 0.0.0.0:5000 ...

[+] Alice conectou-se de 127.0.0.1:52341
[Alice] Olá pessoal!
[+] Bob conectou-se de 127.0.0.1:52342
[Bob] Oi Alice!
[-] Alice desconectou-se.
```

**Terminal 2 — Cliente Alice:**
```
Digite seu apelido: Alice

Conectado ao servidor 127.0.0.1:5000 como 'Alice'.
Digite sua mensagem e pressione Enter para enviar.
Para sair, digite /sair

Olá pessoal!
[Servidor] Bob entrou no chat.
[Bob] Oi Alice!
/sair
[Chat] Saindo...
[Chat] Conexão encerrada. Até logo!
```

**Terminal 3 — Cliente Bob:**
```
Digite seu apelido: Bob

Conectado ao servidor 127.0.0.1:5000 como 'Bob'.
Digite sua mensagem e pressione Enter para enviar.
Para sair, digite /sair

[Servidor] Alice entrou no chat.
[Alice] Olá pessoal!
Oi Alice!
[Servidor] Alice saiu do chat.
```

---

## Comandos do Cliente

| Comando  | Ação                                      |
|----------|-------------------------------------------|
| `/sair`  | Encerra a conexão e fecha o programa      |
| `Ctrl+C` | Interrupção de emergência (mesmo efeito)  |

---

## Limitações

- Não há autenticação de usuários; qualquer pessoa com acesso à rede pode conectar-se.
- Mensagens trafegam em texto plano (sem criptografia TLS/SSL).
- Não há persistência de mensagens; o histórico se perde ao encerrar o servidor.
- Arquitetura centralizada: o servidor é um **ponto único de falha** (*Single Point of Failure*).
- Interface exclusivamente de linha de comando (CLI).

## Melhorias Futuras

- Autenticação com login e senha (tokens JWT ou similar)
- Criptografia de ponta a ponta via TLS
- Persistência de histórico em banco de dados (SQLite, PostgreSQL ou MongoDB)
- Interface gráfica (GUI com Tkinter ou aplicação web com Flask/WebSocket)
- Replicação do servidor para eliminar o ponto único de falha
- Sistema de logs estruturados para monitoramento e rastreabilidade

---

## Referências

- COULOURIS, G. et al. *Sistemas Distribuídos: Conceitos e Projeto*. 5. ed. Porto Alegre: Bookman, 2013.
- TANENBAUM, A. S.; VAN STEEN, M. *Sistemas Distribuídos: Princípios e Paradigmas*. 2. ed. São Paulo: Pearson Prentice Hall, 2007.
