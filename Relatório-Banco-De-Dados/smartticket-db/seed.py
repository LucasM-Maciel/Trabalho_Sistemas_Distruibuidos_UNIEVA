"""
seed.py — Dados Iniciais do SmartTicket DB

Popula o banco com perfis e usuários de exemplo.
Execute diretamente para resetar os dados de demonstração.
"""

from database_sql import inserir_perfil, inserir_usuario, inicializar_banco


def popular_banco() -> dict:
    """
    Cria perfis e usuários iniciais.

    Returns:
        Dicionário com IDs dos recursos criados.
    """
    inicializar_banco()

    # --- Perfis (equivalem a roles no PostgreSQL: CREATE ROLE ...) ---
    id_admin   = inserir_perfil("admin")
    id_tecnico = inserir_perfil("tecnico")
    id_cliente = inserir_perfil("cliente")

    # --- Usuários de exemplo ---
    id_admin_user  = inserir_usuario("Admin Sistema",  "admin@smartticket.dev",   id_admin)
    id_joao        = inserir_usuario("Técnico João",   "joao@smartticket.dev",    id_tecnico)
    id_maria       = inserir_usuario("Técnica Maria",  "maria@smartticket.dev",   id_tecnico)
    id_lucas       = inserir_usuario("Cliente Lucas",  "lucas@smartticket.dev",   id_cliente)

    return {
        "perfis": {
            "admin":   id_admin,
            "tecnico": id_tecnico,
            "cliente": id_cliente,
        },
        "usuarios": {
            "admin":  id_admin_user,
            "joao":   id_joao,
            "maria":  id_maria,
            "lucas":  id_lucas,
        },
    }


if __name__ == "__main__":
    ids = popular_banco()
    print("Perfis criados:", ids["perfis"])
    print("Usuários criados:", ids["usuarios"])
