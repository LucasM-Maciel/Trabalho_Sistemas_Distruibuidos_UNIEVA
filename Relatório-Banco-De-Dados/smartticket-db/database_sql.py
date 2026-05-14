"""
database_sql.py — Camada SQL Transacional (SQLite)

SQLite representa a camada SQL/transacional do SmartTicket DB.
Em ambiente de produção, esta camada seria substituída por
PostgreSQL, MySQL ou outro SGBD completo com suporte a DCL nativa.

Conceitos ACID demonstrados aqui:
    - Atomicidade:  todo bloco com conn.execute() dentro de um
                    try/except é atômico — ou tudo vai ou nada vai.
    - Consistência: chaves estrangeiras (PRAGMA foreign_keys = ON)
                    garantem que chamados só existem para usuários válidos.
    - Isolamento:   cada conexão SQLite usa transações serializáveis
                    por padrão; em concurrency_demo.py isso é mais visível.
    - Durabilidade: após o COMMIT, dados persistem no arquivo .db mesmo
                    que o processo seja encerrado imediatamente.
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "smartticket.db")


def get_connection() -> sqlite3.Connection:
    """Retorna uma conexão com foreign keys ativadas."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    # PRAGMA foreign_keys: garante Integridade Referencial no SQLite
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def inicializar_banco() -> None:
    """
    Cria as tabelas caso não existam.
    Estrutura baseada no modelo ANSI/SPARC: nível conceitual.
    """
    conn = get_connection()
    try:
        # Transação DDL: cria o esquema do banco
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS perfis (
                id_perfil  INTEGER PRIMARY KEY AUTOINCREMENT,
                nome       TEXT    UNIQUE NOT NULL
            );

            CREATE TABLE IF NOT EXISTS usuarios (
                id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
                nome       TEXT    NOT NULL,
                email      TEXT    UNIQUE NOT NULL,
                id_perfil  INTEGER NOT NULL,
                FOREIGN KEY (id_perfil) REFERENCES perfis(id_perfil)
            );

            CREATE TABLE IF NOT EXISTS chamados (
                id_chamado  INTEGER PRIMARY KEY AUTOINCREMENT,
                id_usuario  INTEGER NOT NULL,
                titulo      TEXT    NOT NULL,
                descricao   TEXT    NOT NULL,
                status      TEXT    NOT NULL DEFAULT 'aberto',
                criado_em   TEXT    NOT NULL,
                atualizado_em TEXT,
                FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
            );

            CREATE TABLE IF NOT EXISTS logs_sql (
                id_log     INTEGER PRIMARY KEY AUTOINCREMENT,
                id_chamado INTEGER,
                acao       TEXT    NOT NULL,
                detalhes   TEXT,
                criado_em  TEXT    NOT NULL,
                FOREIGN KEY (id_chamado) REFERENCES chamados(id_chamado)
            );
        """)
        conn.commit()
    finally:
        conn.close()


def inserir_perfil(nome: str) -> int:
    """Insere um perfil e retorna seu ID."""
    conn = get_connection()
    try:
        cursor = conn.execute(
            "INSERT OR IGNORE INTO perfis (nome) VALUES (?)", (nome,)
        )
        conn.commit()
        if cursor.lastrowid:
            return cursor.lastrowid
        row = conn.execute(
            "SELECT id_perfil FROM perfis WHERE nome = ?", (nome,)
        ).fetchone()
        return row["id_perfil"]
    finally:
        conn.close()


def inserir_usuario(nome: str, email: str, id_perfil: int) -> int:
    """Insere um usuário e retorna seu ID."""
    conn = get_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO usuarios (nome, email, id_perfil) VALUES (?, ?, ?)",
            (nome, email, id_perfil),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def abrir_chamado(id_usuario: int, titulo: str, descricao: str,
                  simular_erro: bool = False) -> int:
    """
    Abre um chamado usando uma transação ACID completa.

    Demonstração de Atomicidade:
        - Insere o chamado na tabela 'chamados'
        - Insere um log na tabela 'logs_sql'
        - Se simular_erro=True, lança uma exceção após inserir o chamado
          mas antes de inserir o log — o ROLLBACK desfaz tudo.

    Returns:
        ID do chamado criado (após COMMIT bem-sucedido).

    Raises:
        Exception: Qualquer erro — com ROLLBACK, nenhum dado permanece no banco.
    """
    conn = get_connection()
    agora = datetime.now().isoformat()
    try:
        # BEGIN implícito: SQLite inicia a transação ao primeiro DML
        cursor = conn.execute(
            """INSERT INTO chamados (id_usuario, titulo, descricao, status, criado_em)
               VALUES (?, ?, ?, 'aberto', ?)""",
            (id_usuario, titulo, descricao, agora),
        )
        id_chamado = cursor.lastrowid

        # Ponto de falha intencional — demonstra ROLLBACK (Atomicidade)
        if simular_erro:
            raise RuntimeError("Falha simulada para demonstrar ROLLBACK")

        conn.execute(
            """INSERT INTO logs_sql (id_chamado, acao, detalhes, criado_em)
               VALUES (?, 'abertura', ?, ?)""",
            (id_chamado, f"Chamado '{titulo}' criado para usuário {id_usuario}", agora),
        )

        conn.commit()   # COMMIT: torna as mudanças permanentes (Durabilidade)
        return id_chamado

    except Exception:
        conn.rollback()  # ROLLBACK: desfaz tudo (Atomicidade)
        raise
    finally:
        conn.close()


def atualizar_status(id_chamado: int, novo_status: str,
                     nome_executor: str = "sistema") -> None:
    """Atualiza o status de um chamado e registra no log SQL."""
    conn = get_connection()
    agora = datetime.now().isoformat()
    try:
        conn.execute(
            "UPDATE chamados SET status = ?, atualizado_em = ? WHERE id_chamado = ?",
            (novo_status, agora, id_chamado),
        )
        conn.execute(
            """INSERT INTO logs_sql (id_chamado, acao, detalhes, criado_em)
               VALUES (?, 'atualizacao_status', ?, ?)""",
            (id_chamado, f"Status -> '{novo_status}' por {nome_executor}", agora),
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def buscar_usuario(id_usuario: int) -> sqlite3.Row | None:
    """Retorna um usuário pelo ID."""
    conn = get_connection()
    try:
        return conn.execute(
            """SELECT u.id_usuario, u.nome, u.email, p.nome AS perfil
               FROM usuarios u JOIN perfis p ON u.id_perfil = p.id_perfil
               WHERE u.id_usuario = ?""",
            (id_usuario,),
        ).fetchone()
    finally:
        conn.close()


def listar_chamados() -> list:
    """Lista todos os chamados com nome do usuário vinculado."""
    conn = get_connection()
    try:
        return conn.execute(
            """SELECT c.id_chamado, u.nome AS usuario, c.titulo,
                      c.status, c.criado_em
               FROM chamados c JOIN usuarios u ON c.id_usuario = u.id_usuario
               ORDER BY c.id_chamado""",
        ).fetchall()
    finally:
        conn.close()


def registrar_log_avulso(id_chamado: int | None, acao: str,
                          detalhes: str) -> None:
    """Registra um log SQL independente de uma transação de chamado."""
    conn = get_connection()
    agora = datetime.now().isoformat()
    try:
        conn.execute(
            """INSERT INTO logs_sql (id_chamado, acao, detalhes, criado_em)
               VALUES (?, ?, ?, ?)""",
            (id_chamado, acao, detalhes, agora),
        )
        conn.commit()
    finally:
        conn.close()
