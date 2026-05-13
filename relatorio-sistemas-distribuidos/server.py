"""
servidor.py — Servidor TCP de Chat Distribuído
===============================================
Disciplina: Sistemas Distribuídos e Redes de Computadores
Autor: Lucas Marques Maciel — UniEVANGÉLICA, 2026

Conceitos aplicados:
  - Arquitetura cliente-servidor (COULOURIS et al., 2013)
  - Comunicação assíncrona via threads (TANENBAUM; VAN STEEN, 2007)
  - Sincronização de recursos compartilhados com threading.Lock (Mutex)
  - Tolerância a falhas básica via tratamento de exceções por thread

Como executar:
  python server.py
  (porta padrão: 5000)
"""

import socket
import threading

# ──────────────────────────────────────────────
# Configuração do servidor
# ──────────────────────────────────────────────
HOST = "0.0.0.0"   # Aceita conexões de qualquer interface de rede
PORT = 5000        # Porta TCP de escuta

# Estrutura compartilhada: dicionário {socket: apelido}
# Representa todos os clientes atualmente conectados.
# Acessada por múltiplas threads simultaneamente, por isso é
# protegida por um Lock (exclusão mútua / Mutex).
clientes = {}
lock = threading.Lock()


def broadcast(mensagem: str, remetente: socket.socket) -> None:
    """
    Distribui uma mensagem para todos os clientes conectados,
    exceto o remetente original.

    O Lock é adquirido antes de iterar sobre o dicionário para
    evitar condições de corrida (race conditions) caso outra thread
    modifique a lista durante a iteração.
    """
    with lock:
        # Cria uma cópia dos itens para evitar erro se o dict mudar
        destinatarios = list(clientes.items())

    for conn, apelido in destinatarios:
        if conn is remetente:
            continue
        try:
            conn.sendall(mensagem.encode("utf-8"))
        except OSError:
            # Se o envio falhar, a thread daquele cliente cuidará
            # da remoção; aqui apenas ignoramos o erro.
            pass


def tratar_cliente(conn: socket.socket, endereco: tuple) -> None:
    """
    Função executada em uma thread dedicada para cada cliente.

    Responsável por:
      1. Receber o apelido de identificação do cliente.
      2. Registrar o cliente na estrutura compartilhada (protegida por Lock).
      3. Receber mensagens em loop e redistribuí-las via broadcast.
      4. Remover o cliente da estrutura ao detectar desconexão ou erro.
    """
    apelido = None
    try:
        # Primeira mensagem recebida é o apelido escolhido pelo cliente
        dados = conn.recv(1024)
        if not dados:
            conn.close()
            return

        apelido = dados.decode("utf-8").strip()

        # Registra o novo cliente com proteção do Lock
        with lock:
            clientes[conn] = apelido

        print(f"[+] {apelido} conectou-se de {endereco[0]}:{endereco[1]}")
        broadcast(f"[Servidor] {apelido} entrou no chat.\n", conn)

        # Loop principal de recebimento de mensagens
        while True:
            dados = conn.recv(4096)
            if not dados:
                # Conexão encerrada pelo cliente de forma limpa
                break

            texto = dados.decode("utf-8").strip()
            print(f"[{apelido}] {texto}")
            broadcast(f"[{apelido}] {texto}\n", conn)

    except (ConnectionResetError, ConnectionAbortedError, OSError):
        # Captura desconexões abruptas sem derrubar o servidor
        pass

    finally:
        # Bloco de limpeza: executado mesmo em caso de exceção.
        # Remove o cliente da estrutura compartilhada (com Lock) e
        # fecha o socket, preservando os demais participantes.
        with lock:
            if conn in clientes:
                del clientes[conn]

        conn.close()

        if apelido:
            print(f"[-] {apelido} desconectou-se.")
            broadcast(f"[Servidor] {apelido} saiu do chat.\n", None)


def iniciar_servidor() -> None:
    """
    Inicializa o socket TCP, aguarda conexões e delega cada
    cliente a uma thread independente.
    """
    # AF_INET  → família de endereços IPv4
    # SOCK_STREAM → protocolo TCP (orientado à conexão)
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Permite reutilizar a porta imediatamente após reinício do servidor
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    servidor.bind((HOST, PORT))
    servidor.listen()

    print(f"[Servidor] Aguardando conexões em {HOST}:{PORT} ...")
    print("[Servidor] Pressione Ctrl+C para encerrar.\n")

    try:
        while True:
            conn, endereco = servidor.accept()

            # Cria uma thread exclusiva para o cliente recém-conectado.
            # daemon=True garante que a thread encerre junto com o processo
            # principal ao pressionar Ctrl+C.
            thread = threading.Thread(
                target=tratar_cliente,
                args=(conn, endereco),
                daemon=True
            )
            thread.start()

            with lock:
                total = len(clientes)
            print(f"[Servidor] Nova conexão de {endereco}. "
                  f"Threads ativas: {threading.active_count() - 1} | "
                  f"Clientes registrados: {total}")

    except KeyboardInterrupt:
        print("\n[Servidor] Encerrando servidor...")
    finally:
        servidor.close()
        print("[Servidor] Socket fechado. Até logo!")


if __name__ == "__main__":
    iniciar_servidor()
