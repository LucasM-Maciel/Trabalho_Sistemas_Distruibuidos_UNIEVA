"""
concurrency_demo.py — Simulação de Controle de Concorrência

Em sistemas multiusuário, múltiplas transações podem tentar acessar
o mesmo recurso simultaneamente. Sem controle de concorrência, problemas
como 'atualização perdida' (lost update) podem ocorrer:
    - Thread A lê o chamado (status = "aberto")
    - Thread B lê o chamado (status = "aberto")
    - Thread A escreve (status = "em atendimento")
    - Thread B escreve (status = "em atendimento") — sobrescreve A sem saber

SGBDs reais usam bloqueios (locks) e protocolos como 2PL (Two-Phase Locking)
para serializar o acesso. Aqui simulamos esse comportamento com threading.Lock,
que garante exclusão mútua — apenas uma thread por vez pode atualizar o chamado.

Isso representa o nível de Isolamento das propriedades ACID.
"""

import threading
import time
from datetime import datetime
from database_sql import atualizar_status, get_connection
from database_nosql import registrar_evento

# Lock compartilhado — simula o mecanismo de bloqueio do SGBD
_lock_chamado = threading.Lock()

# Resultados da corrida (para consulta após a demo)
resultados: list[str] = []


def tecnico_atualiza(nome_tecnico: str, id_chamado: int,
                     novo_status: str, atraso: float = 0.0) -> None:
    """
    Simula um técnico tentando atualizar o status de um chamado.

    O threading.Lock garante que apenas uma thread por vez execute
    a seção crítica (leitura + escrita), evitando condições de corrida.
    """
    time.sleep(atraso)  # Simula latência de rede/processamento diferente

    print(f"  [{nome_tecnico}] Tentando adquirir bloqueio sobre chamado #{id_chamado}...")
    with _lock_chamado:
        # Seção crítica: apenas uma thread aqui por vez
        print(f"  [{nome_tecnico}] Bloqueio adquirido — atualizando para '{novo_status}'")
        atualizar_status(id_chamado, novo_status, nome_executor=nome_tecnico)
        registrar_evento(
            id_chamado,
            tipo="atualizacao_concorrente",
            origem=nome_tecnico,
            dados_extras={"novo_status": novo_status, "timestamp": datetime.now().isoformat()},
        )
        resultados.append(f"{nome_tecnico} → '{novo_status}'")
        print(f"  [{nome_tecnico}] Atualização concluída e lock liberado.\n")


def simular_concorrencia(id_chamado: int) -> None:
    """
    Lança duas threads simultâneas tentando alterar o mesmo chamado.

    Sem o Lock, ambas poderiam ler o mesmo estado e uma sobrescreveria
    a outra sem registro — problema clássico de 'atualização perdida'.
    Com o Lock, a segunda thread espera a primeira terminar.
    """
    global resultados
    resultados = []

    print("\n=== DEMONSTRAÇÃO DE CONTROLE DE CONCORRÊNCIA ===")
    print(f"Dois técnicos tentando atualizar o chamado #{id_chamado} ao mesmo tempo.")
    print("O threading.Lock serializa o acesso (equivalente ao bloqueio do SGBD).\n")

    t1 = threading.Thread(
        target=tecnico_atualiza,
        args=("Técnico João", id_chamado, "em atendimento", 0.0),
        name="Thread-Joao",
    )
    t2 = threading.Thread(
        target=tecnico_atualiza,
        args=("Técnica Maria", id_chamado, "em atendimento", 0.05),
        name="Thread-Maria",
    )

    t1.start()
    t2.start()
    t1.join()
    t2.join()

    print("Ordem de execução registrada:")
    for i, r in enumerate(resultados, 1):
        print(f"  {i}. {r}")
    print("Nenhuma atualização foi perdida graças ao controle de concorrência.\n")
