"""
main.py — SmartTicket DB: Demonstração Acadêmica Completa

Executa um roteiro completo que demonstra, de forma didática:
    1. Inicialização do banco SQL e NoSQL
    2. Criação de perfis e usuários
    3. Abertura de chamado com COMMIT
    4. Tentativa de abertura com ROLLBACK (falha simulada)
    5. Tentativa de operação com usuário inexistente (integridade referencial)
    6. Controle de acesso por perfil (simulação de DCL)
    7. Atualização de status por técnico
    8. Simulação de concorrência com threading.Lock
    9. Sincronização mobile (evento NoSQL)
    10. Contagem MapReduce dos eventos por tipo

Execute com:
    python main.py
"""

import os
import sys

# Garante que os módulos são encontrados ao rodar de qualquer diretório
sys.path.insert(0, os.path.dirname(__file__))

# Força UTF-8 no terminal do Windows para exibir caracteres especiais
if hasattr(sys.stdout, "reconfigure") and sys.stdout.encoding:
    if sys.stdout.encoding.lower() != "utf-8":
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except (OSError, ValueError):
            pass

from database_sql import (
    atualizar_status,
    listar_chamados,
    abrir_chamado,
    registrar_log_avulso,
)
from database_nosql import (
    registrar_evento,
    listar_eventos_por_chamado,
    mapreduce_contar_por_tipo,
)
from auth import verificar_permissao
from seed import popular_banco
from concurrency_demo import simular_concorrencia


def secao(titulo: str) -> None:
    print(f"\n{'─' * 60}")
    print(f"  {titulo}")
    print(f"{'─' * 60}")


def limpar_dados() -> None:
    """Remove arquivos de execuções anteriores para garantir saída limpa."""
    db = os.path.join(os.path.dirname(__file__), "data", "smartticket.db")
    nosql = os.path.join(os.path.dirname(__file__), "data", "eventos_chamados.json")
    for arq in (db, nosql):
        if os.path.exists(arq):
            os.remove(arq)


# ─────────────────────────────────────────────
# INÍCIO DA DEMONSTRAÇÃO
# ─────────────────────────────────────────────

print("\n" + "═" * 60)
print("         SmartTicket DB — Protótipo Acadêmico")
print("         Banco de Dados — UNIEVANGÉLICA 2026")
print("═" * 60)

# 1. INICIALIZAÇÃO
secao("1. INICIALIZAÇÃO DO BANCO")
limpar_dados()
ids = popular_banco()
print("✔ Banco SQL inicializado (SQLite + PRAGMA foreign_keys = ON)")
print("✔ Perfis criados:  admin, tecnico, cliente")
print("✔ Usuários criados:")
print("    • Admin Sistema  (admin@smartticket.dev)")
print("    • Técnico João   (joao@smartticket.dev)")
print("    • Técnica Maria  (maria@smartticket.dev)")
print("    • Cliente Lucas  (lucas@smartticket.dev)")

id_lucas = ids["usuarios"]["lucas"]

# 2. ABRIR CHAMADO COM SUCESSO (COMMIT)
secao("2. ABERTURA DE CHAMADO — COMMIT (Atomicidade + Durabilidade)")
id_chamado = abrir_chamado(
    id_usuario=id_lucas,
    titulo="Erro ao acessar painel do cliente",
    descricao="Ao tentar acessar o painel, a tela exibe erro 403.",
)
registrar_evento(
    id_chamado,
    tipo="criacao_chamado",
    origem="sistema",
    dados_extras={"titulo": "Erro ao acessar painel do cliente", "status": "aberto"},
)
registrar_evento(
    id_chamado,
    tipo="anexo_simulado",
    origem="Cliente Lucas",
    dados_extras={
        "nome_arquivo": "screenshot_erro_403.png",
        "tipo_mime": "image/png",
        "bytes_aprox": 84200,
    },
)
print(f"✔ Chamado #{id_chamado} aberto com sucesso.")
print("  → INSERT chamado + INSERT log_sql executados na mesma transação.")
print("  → COMMIT confirmado: dados persistidos no SQLite (Durabilidade).")

# 3. CHAMADO COM FALHA SIMULADA (ROLLBACK)
secao("3. FALHA SIMULADA — ROLLBACK (Atomicidade)")
print("Tentando abrir chamado com erro proposital após INSERT...")
try:
    abrir_chamado(
        id_usuario=id_lucas,
        titulo="Chamado que nunca existirá",
        descricao="Este chamado será desfeito pelo ROLLBACK.",
        simular_erro=True,
    )
except RuntimeError as e:
    print(f"✘ Erro capturado: {e}")
    print("  → ROLLBACK executado: nenhum dado parcial foi salvo (Atomicidade).")
    registrar_evento(
        None,
        tipo="rollback_simulado",
        origem="sistema",
        dados_extras={"motivo": "Erro proposital para demonstração de ROLLBACK"},
    )

# 4. INTEGRIDADE REFERENCIAL
secao("4. INTEGRIDADE REFERENCIAL (Consistência)")
print("Tentando criar chamado para usuário ID 9999 (inexistente)...")
try:
    abrir_chamado(9999, "Chamado inválido", "Usuário não existe.")
except Exception as e:
    print(f"✘ SGBD bloqueou a operação: {type(e).__name__}")
    print("  → FOREIGN KEY violation: chamados.id_usuario → usuarios.id_usuario")
    print("  → ROLLBACK automático: banco permanece consistente.")
    registrar_log_avulso(None, "violacao_integridade",
                          "Tentativa de chamado para usuário inexistente (ID 9999)")
    registrar_evento(
        None,
        tipo="violacao_integridade",
        origem="sistema",
        dados_extras={"usuario_solicitado": 9999, "erro": "FOREIGN KEY constraint"},
    )

# 5. CONTROLE DE ACESSO (DCL / GRANT e REVOKE)
secao("5. CONTROLE DE ACESSO — Simulação de DCL")
print("Testando permissões por perfil (equivale a GRANT/REVOKE do PostgreSQL):\n")

testes = [
    ("admin",   "administrar",      True),
    ("tecnico", "atualizar_status",  True),
    ("tecnico", "administrar",       False),
    ("cliente", "abrir_chamado",     True),
    ("cliente", "resolver_chamado",  False),
]

for perfil, acao, esperado in testes:
    resultado = verificar_permissao(perfil, acao)
    icone = "✔" if resultado == esperado else "✘"
    status = "PERMITIDO" if resultado else "NEGADO"
    print(f"  {icone} perfil='{perfil}' + acao='{acao}' → {status}")

print("\nSimulando cliente tentando resolver chamado:")
perfil_lucas = "cliente"
acao_tentada = "resolver_chamado"
if not verificar_permissao(perfil_lucas, acao_tentada):
    print(f"✘ Acesso negado: '{perfil_lucas}' não pode '{acao_tentada}'")
    registrar_evento(
        id_chamado,
        tipo="acesso_negado",
        origem="cliente",
        dados_extras={
            "usuario": "Cliente Lucas",
            "acao_tentada": acao_tentada,
            "motivo": "Perfil cliente não tem permissão para resolver_chamado",
        },
    )
    print("  → Tentativa registrada no log NoSQL (Segurança + Auditoria).")

# 6. ATUALIZAÇÃO POR TÉCNICO
secao("6. ATUALIZAÇÃO DE STATUS — Técnico João")
if verificar_permissao("tecnico", "atualizar_status"):
    atualizar_status(id_chamado, "em atendimento", nome_executor="Técnico João")
    registrar_evento(
        id_chamado,
        tipo="mudanca_status",
        origem="Técnico João",
        dados_extras={"status_anterior": "aberto", "novo_status": "em atendimento"},
    )
    print(f"✔ Chamado #{id_chamado} atualizado para 'em atendimento'.")
    print("  → UPDATE + INSERT log_sql em transação única (COMMIT).")

# 7. CONCORRÊNCIA
secao("7. CONTROLE DE CONCORRÊNCIA — threading.Lock")
simular_concorrencia(id_chamado)

# 8. SINCRONIZAÇÃO MOBILE
secao("8. SINCRONIZAÇÃO MOBILE (Banco Distribuído / Offline)")
print("Simulando técnico registrando atualização offline via app mobile...")
registrar_evento(
    id_chamado,
    tipo="atualizacao_offline",
    origem="app_mobile_maria",
    dados_extras={
        "tecnico": "Técnica Maria",
        "acao": "Diagnóstico realizado sem conexão",
        "modo": "offline",
        "pendente_sincronizacao": True,
    },
)
print("  → Evento salvo localmente (cache offline).")

print("\nSimulando sincronização quando a rede retornou...")
registrar_evento(
    id_chamado,
    tipo="sincronizacao_mobile",
    origem="servidor_central",
    dados_extras={
        "tecnico": "Técnica Maria",
        "status_sync": "sucesso",
        "conflitos_resolvidos": 0,
        "mensagem": "Dados offline sincronizados com o servidor central.",
    },
)
atualizar_status(id_chamado, "resolvido", nome_executor="Técnica Maria (sync)")
print("  → Evento 'sincronizacao_mobile' persistido no NoSQL.")
print("  → Status do chamado atualizado para 'resolvido'.")
print("  → Equivale ao comportamento do Firebase Firestore offline persistence.")

# 9. MAPREDUCE
secao("9. MapReduce Conceitual — Contagem de Eventos por Tipo")
print("Fase MAP: extraindo o campo 'tipo' de cada documento da coleção...")
print("Fase REDUCE: somando ocorrências por tipo...\n")
contagem = mapreduce_contar_por_tipo()
total = sum(contagem.values())
for tipo, qtd in sorted(contagem.items(), key=lambda x: -x[1]):
    barra = "█" * qtd
    print(f"  {tipo:<30} {barra} ({qtd})")
print(f"\n  Total de eventos registrados: {total}")
print("  → Em produção, este MapReduce seria executado em cluster")
print("     (Hadoop/Spark) sobre milhões de documentos distribuídos.")

# 10. RESUMO FINAL
secao("10. RESUMO FINAL — Estado do Sistema")
chamados = listar_chamados()
print(f"Chamados no banco SQL: {len(chamados)}")
for c in chamados:
    print(f"  #{c['id_chamado']} [{c['status']}] '{c['titulo']}' — {c['usuario']}")

eventos_chamado = listar_eventos_por_chamado(id_chamado)
print(f"\nEventos NoSQL do chamado #{id_chamado}: {len(eventos_chamado)}")
for ev in eventos_chamado:
    print(f"  [{ev['tipo']}] origem={ev['origem']}")

print("\n" + "═" * 60)
print("  Demonstração concluída com sucesso.")
print("  Todos os conceitos do enunciado foram demonstrados.")
print("═" * 60 + "\n")
