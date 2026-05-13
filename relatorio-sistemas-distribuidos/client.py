"""
client.py — Cliente TCP de Chat Distribuído
============================================
Disciplina: Sistemas Distribuídos e Redes de Computadores
Autor: Lucas Marques Maciel — UniEVANGÉLICA, 2026

Conceitos aplicados:
  - Comunicação assíncrona: thread dedicada para recepção de mensagens
  - Protocolo TCP/IP via módulo socket (camada de transporte)
  - Tratamento de desconexão e encerramento gracioso da sessão

Como executar:
  python client.py
  (conecta em localhost:5000 por padrão)

Comandos disponíveis durante o chat:
  /sair  →  encerra a conexão e o programa
"""

import socket
import threading
import sys

# ──────────────────────────────────────────────
# Configuração de conexão
# ──────────────────────────────────────────────
HOST = "127.0.0.1"  # Endereço do servidor (localhost para testes locais)
PORT = 5000         # Deve coincidir com a porta configurada no servidor

# Evento global usado para sinalizar que o cliente deve encerrar.
# Quando disparado, tanto a thread de recepção quanto o loop principal
# param de forma coordenada.
encerrar = threading.Event()


def receber_mensagens(conn: socket.socket) -> None:
    """
    Executada em uma thread separada.
    Fica em loop aguardando dados do servidor e os exibe no terminal.

    Ao detectar desconexão (recv retorna bytes vazios) ou qualquer
    erro de rede, dispara o evento de encerramento para que o loop
    principal também termine.
    """
    while not encerrar.is_set():
        try:
            dados = conn.recv(4096)
            if not dados:
                # O servidor fechou a conexão
                print("\n[!] Conexão encerrada pelo servidor.")
                encerrar.set()
                break

            mensagem = dados.decode("utf-8")
            # Imprime a mensagem recebida e reexibe o prompt de entrada
            print(mensagem, end="", flush=True)

        except OSError:
            # Socket foi fechado localmente (pelo bloco finally do main)
            if not encerrar.is_set():
                print("\n[!] Erro na conexão com o servidor.")
                encerrar.set()
            break


def conectar() -> None:
    """
    Ponto de entrada do cliente:
      1. Solicita apelido ao usuário.
      2. Conecta ao servidor via TCP.
      3. Envia o apelido como primeira mensagem.
      4. Inicia a thread de recepção.
      5. Entra no loop de envio de mensagens pelo terminal.
    """
    apelido = input("Digite seu apelido: ").strip()
    if not apelido:
        apelido = "Anônimo"

    # Criação do socket TCP IPv4
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        conn.connect((HOST, PORT))
    except ConnectionRefusedError:
        print(f"[ERRO] Não foi possível conectar a {HOST}:{PORT}.")
        print("       Verifique se o servidor está em execução.")
        sys.exit(1)

    print(f"\nConectado ao servidor {HOST}:{PORT} como '{apelido}'.")
    print("Digite sua mensagem e pressione Enter para enviar.")
    print("Para sair, digite /sair\n")

    # Envia o apelido imediatamente após a conexão;
    # o servidor aguarda esse dado antes de registrar o cliente.
    conn.sendall(apelido.encode("utf-8"))

    # Inicia a thread de recepção em segundo plano.
    # daemon=True: a thread é encerrada automaticamente quando o
    # processo principal terminar.
    thread_recv = threading.Thread(
        target=receber_mensagens,
        args=(conn,),
        daemon=True
    )
    thread_recv.start()

    # Loop principal: captura entradas do teclado e envia ao servidor
    try:
        while not encerrar.is_set():
            try:
                mensagem = input()
            except EOFError:
                # Redirecionamento de stdin encerrado
                break

            if mensagem.strip().lower() == "/sair":
                print("[Chat] Saindo...")
                break

            if mensagem.strip() == "":
                # Não envia mensagens vazias
                continue

            try:
                conn.sendall(mensagem.encode("utf-8"))
            except OSError:
                print("[!] Falha ao enviar mensagem. Conexão perdida.")
                break

    except KeyboardInterrupt:
        print("\n[Chat] Interrompido pelo usuário.")

    finally:
        # Sinaliza encerramento e fecha o socket de forma limpa
        encerrar.set()
        conn.close()
        print("[Chat] Conexão encerrada. Até logo!")


if __name__ == "__main__":
    conectar()
