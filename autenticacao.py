import hashlib
from Data.database import conectar
from modulos.utils import cabecalho, pausar, agora

# ── Hash simples de senha ─────────────────────────────────────────────────────
def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

# ── Cadastro ──────────────────────────────────────────────────────────────────
def cadastrar():
    cabecalho("CADASTRO")

    nome     = input("  Nome completo: ").strip()
    email    = input("  E-mail: ").strip()
    telefone = input("  Telefone (com DDD): ").strip()
    senha    = input("  Senha: ").strip()

    if not nome or not email or not telefone or not senha:
        print("\n  Todos os campos são obrigatórios.")
        pausar()
        return None

    # Verificar se email ou telefone já existem
    with conectar() as conn:
        existe = conn.execute(
            "SELECT id FROM usuarios WHERE email=? OR telefone=?",
            (email, telefone)
        ).fetchone()

    if existe:
        print("\n  E-mail ou telefone já cadastrado.")
        pausar()
        return None

    # Verificar se é funcionário público ou moderador
    tipo  = "comum"
    orgao = None

    resp = input("\n  Você é funcionário público ou moderador? (S/N): ").strip().upper()
    if resp == "S":
        codigo = input("  Insira o código de acesso: ").strip().upper()

        with conectar() as conn:
            registro = conn.execute(
                "SELECT * FROM codigos_acesso WHERE codigo=? AND usado=0",
                (codigo,)
            ).fetchone()

        if registro:
            tipo  = registro["tipo"]
            orgao = registro["orgao"]
            with conectar() as conn:
                conn.execute("UPDATE codigos_acesso SET usado=1 WHERE codigo=?", (codigo,))
            print(f"\n  Código válido! Cadastrado como: {tipo.upper()}" + (f" — {orgao}" if orgao else ""))
        else:
            print("\n  Código inválido. Cadastrado como usuário comum.")

    # Salvar usuário
    with conectar() as conn:
        conn.execute(
            "INSERT INTO usuarios (nome,email,telefone,senha,tipo,orgao,criado_em) VALUES (?,?,?,?,?,?,?)",
            (nome, email, telefone, hash_senha(senha), tipo, orgao, agora())
        )
        usuario = dict(conn.execute("SELECT * FROM usuarios WHERE email=?", (email,)).fetchone())

    print(f"\n  Cadastro realizado com sucesso! Bem-vindo(a), {nome}!")
    pausar()
    return usuario

# ── Login ─────────────────────────────────────────────────────────────────────
def login():
    cabecalho("LOGIN")

    identificador = input("  E-mail ou telefone: ").strip()
    senha         = input("  Senha: ").strip()

    with conectar() as conn:
        row = conn.execute(
            "SELECT * FROM usuarios WHERE (email=? OR telefone=?) AND senha=?",
            (identificador, identificador, hash_senha(senha))
        ).fetchone()

    if not row:
        print("\n  E-mail/telefone ou senha incorretos.")
        pausar()
        return None

    usuario = dict(row)
    print(f"\n  Bem-vindo(a), {usuario['nome']}!")
    pausar()
    return usuario

# ── Tela inicial de acesso ────────────────────────────────────────────────────
def tela_acesso():
    while True:
        cabecalho("BEM-VINDO")
        print("  [1] Cadastrar")
        print("  [2] Login")
        print("  [3] Continuar sem login")
        print("  [0] Sair")

        op = input("\n  Escolha: ").strip()

        if op == "1":
            usuario = cadastrar()
            if usuario:
                return usuario
        elif op == "2":
            usuario = login()
            if usuario:
                return usuario
        elif op == "3":
            return None
        elif op == "0":
            import sys
            sys.exit(0)
        else:
            print("\n  Opção inválida.")
            pausar()
