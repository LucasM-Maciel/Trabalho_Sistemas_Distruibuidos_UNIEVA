"""
database_nosql.py — Camada NoSQL Documental (Simulação via JSON)

Este módulo simula um banco de dados NoSQL orientado a documentos,
como MongoDB, Firebase ou Firestore, usando um arquivo JSON local.

Por que essa simulação é didaticamente válida?
    - MongoDB armazena documentos em BSON (superset de JSON).
    - Firestore armazena documentos em coleções com campos flexíveis.
    - Aqui usamos JSON puro, que é a representação legível de BSON.

Vantagens do modelo documental demonstradas aqui:
    - Schema flexível: eventos de tipos diferentes coexistem na mesma coleção.
    - Dados aninhados: campo "dados" aceita qualquer estrutura.
    - Alta velocidade de escrita: ideal para logs e eventos.
    - Escalabilidade horizontal: em produção, coleções distribuídas em shards.

Em ambiente real, substitua este módulo por:
    from pymongo import MongoClient  # MongoDB
    import firebase_admin            # Firebase/Firestore
"""

import json
import os
import uuid
from datetime import datetime

NOSQL_PATH = os.path.join(os.path.dirname(__file__), "data", "eventos_chamados.json")


def _carregar() -> dict:
    """Lê o arquivo JSON (equivale a abrir uma conexão com MongoDB)."""
    if not os.path.exists(NOSQL_PATH):
        return {"eventos_chamado": []}
    with open(NOSQL_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _salvar(dados: dict) -> None:
    """Persiste o arquivo JSON (equivale a um write no MongoDB)."""
    os.makedirs(os.path.dirname(NOSQL_PATH), exist_ok=True)
    with open(NOSQL_PATH, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


def registrar_evento(id_chamado: int | None, tipo: str, origem: str,
                     dados_extras: dict | None = None) -> str:
    """
    Registra um evento documental para um chamado.

    A flexibilidade do campo 'dados' é a principal vantagem do NoSQL:
    um evento de 'criacao_chamado' tem dados diferentes de
    um evento de 'sincronizacao_mobile' ou 'acesso_negado',
    e todos coexistem na mesma coleção sem quebrar o schema.

    Returns:
        ID único do evento registrado.
    """
    banco = _carregar()
    id_evento = str(uuid.uuid4())
    evento = {
        "id_evento": id_evento,
        "id_chamado": id_chamado,
        "tipo": tipo,
        "origem": origem,
        "timestamp": datetime.now().isoformat(),
        "dados": dados_extras or {},
    }
    banco["eventos_chamado"].append(evento)
    _salvar(banco)
    return id_evento


def listar_eventos_por_chamado(id_chamado: int) -> list:
    """Retorna todos os eventos de um chamado específico."""
    banco = _carregar()
    return [e for e in banco["eventos_chamado"] if e["id_chamado"] == id_chamado]


def mapreduce_contar_por_tipo() -> dict:
    """
    Conta eventos por tipo — analogia ao paradigma MapReduce.

    MapReduce (Hadoop/Spark) é um modelo de processamento distribuído:
        - Fase MAP:    cada nó extrai o campo 'tipo' de cada documento.
        - Fase REDUCE: agrega (soma) as ocorrências por tipo.

    Aqui fazemos a mesma operação de forma local e simples,
    sem necessidade de cluster Hadoop ou framework distribuído.
    O conceito é idêntico: mapear atributos e reduzir por chave.
    """
    banco = _carregar()
    contagem: dict[str, int] = {}
    for evento in banco["eventos_chamado"]:
        tipo = evento.get("tipo", "desconhecido")
        contagem[tipo] = contagem.get(tipo, 0) + 1
    return contagem
