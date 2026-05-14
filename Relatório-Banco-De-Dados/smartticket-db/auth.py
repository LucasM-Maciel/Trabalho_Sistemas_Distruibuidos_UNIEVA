"""
auth.py — Controle de Acesso por Perfil (Simulação de DCL)

Em SGBDs completos como PostgreSQL e MySQL, a DCL (Data Control Language)
utiliza comandos como GRANT e REVOKE para conceder ou revogar privilégios
a usuários sobre objetos do banco (tabelas, views, sequências).

Exemplo em PostgreSQL:
    GRANT SELECT, UPDATE ON chamados TO role_tecnico;
    REVOKE DELETE ON chamados FROM role_cliente;

Como o SQLite não implementa controle de usuários e papéis da mesma forma,
este módulo simula a lógica de DCL na camada de aplicação:
cada perfil tem permissões definidas em um dicionário,
e a função verificar_permissao age como um "guarda" que substitui
a verificação que, em ambiente real, seria feita pelo SGBD.
"""

# Matriz de permissões por perfil
# Equivale às políticas de GRANT/REVOKE definidas para cada papel (role)
PERMISSOES = {
    "admin": {
        "abrir_chamado",
        "consultar_chamado",
        "atualizar_status",
        "resolver_chamado",
        "administrar",
    },
    "tecnico": {
        "abrir_chamado",
        "consultar_chamado",
        "atualizar_status",
    },
    "cliente": {
        "abrir_chamado",
        "consultar_chamado",
    },
}


def verificar_permissao(perfil: str, acao: str) -> bool:
    """
    Verifica se um perfil tem permissão para executar uma ação.

    Em ambiente real com PostgreSQL, o SGBD faria essa verificação
    automaticamente antes de executar o comando SQL. Aqui simulamos
    o mesmo comportamento na camada de aplicação.

    Args:
        perfil: Nome do perfil (admin, tecnico, cliente)
        acao:   Ação que se deseja executar

    Returns:
        True se permitido, False caso contrário
    """
    permissoes_do_perfil = PERMISSOES.get(perfil, set())
    return acao in permissoes_do_perfil


def exigir_permissao(perfil: str, acao: str) -> None:
    """
    Lança PermissionError se o perfil não tiver permissão para a ação.
    Conveniente para uso inline antes de operações críticas.
    """
    if not verificar_permissao(perfil, acao):
        raise PermissionError(
            f"Acesso negado: perfil '{perfil}' não tem permissão para '{acao}'. "
            f"(Equivalente a: REVOKE {acao.upper()} FROM role_{perfil})"
        )
