from utils import (
    Cor, cabecalho, linha, msg_erro, msg_info, entrada, pausar,
    badge_usuario, pode_moderar, LARGURA, limpar_tela
)

# ─────────────────────────────────────────
#  TELA DE BOAS-VINDAS / SPLASH
# ─────────────────────────────────────────
def tela_boas_vindas():
    limpar_tela()
    print()
    print(f"  {Cor.AZUL}{'═' * (LARGURA - 4)}{Cor.RESET}")
    print()
    print(f"  {Cor.BOLD}{Cor.BRANCO}  🏙️   S I S T E M A   C R A T O{Cor.RESET}")
    print()
    print(f"  {Cor.DIM}  Portal de Ocorrências e Notícias da Cidade do Crato{Cor.RESET}")
    print(f"  {Cor.DIM}  Ceará — Brasil{Cor.RESET}")
    print()
    print(f"  {Cor.AZUL}{'═' * (LARGURA - 4)}{Cor.RESET}")
    print()

# ─────────────────────────────────────────
#  MENU INICIAL — Cadastro / Login / Continuar
# ─────────────────────────────────────────
def menu_inicial() -> str:
    """
    Retorna: 'cadastro' | 'login' | 'continuar'
    """
    tela_boas_vindas()

    print(f"  {Cor.BOLD}Como deseja continuar?{Cor.RESET}\n")
    print(f"  {Cor.AMARELO}[1]{Cor.RESET} Criar conta")
    print(f"  {Cor.AMARELO}[2]{Cor.RESET} Entrar (login)")
    print(f"  {Cor.AMARELO}[3]{Cor.RESET} Continuar sem login")
    print(f"\n  {Cor.DIM}[0] Sair do sistema{Cor.RESET}")
    print()

    while True:
        cmd = entrada("  Escolha: ", obrigatorio=False).strip()
        if cmd == "1":
            return "cadastro"
        if cmd == "2":
            return "login"
        if cmd == "3":
            return "continuar"
        if cmd == "0":
            return "sair"
        msg_erro("Opção inválida. Digite 1, 2, 3 ou 0.")
