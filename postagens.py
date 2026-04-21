
# ─── Criar postagem ───────────────────────────────────────────────────────────
def tela_criar_postagem(usuario):
    bairros   = _buscar_bairros()
    naturezas = _buscar_naturezas()

    dados = {
        "bairro_id":    None,
        "bairro_nome":  "",
        "local_bairro": "",
        "titulo":       "",
        "conteudo":     "",
        "natureza_id":  None,
        "natureza_nome":"",
    }

    etapa = "bairro"
    while etapa != "fim":
        if etapa == "bairro":
            etapa = _etapa_bairro(dados, bairros)
        elif etapa == "local":
            etapa = _etapa_local(dados)
        elif etapa == "titulo":
            etapa = _etapa_titulo(dados)
        elif etapa == "conteudo":
            etapa = _etapa_conteudo(dados)
        elif etapa == "natureza":
            etapa = _etapa_natureza(dados, naturezas)
        elif etapa == "confirmar":
            etapa = _etapa_confirmar(dados, usuario)
        elif etapa == "voltar":
            return

def _etapa_bairro(dados, bairros):
    pagina = 1
    por_pagina = 10
    while True:
        cabecalho("DIVULGAR OCORRÊNCIA", "Passo 1 — Bairro")
        itens, pagina, total_pag = paginar(bairros, por_pagina, pagina)

        print(barra_paginas(pagina, total_pag))
        print()
        for i, b in enumerate(itens, start=(pagina-1)*por_pagina+1):
            print(f"  {CYAN}[{i:>2}]{RESET} {b['nome']}")
        print(f"\n  {RED}[X]{RESET} Voltar")

        if total_pag > 1:
            print(f"  {DIM}[>] Próxima  [<] Anterior  [número da página]{RESET}")

        op = pedir("Escolha o bairro:").upper()
        if op == "X":
            return "voltar"
        if op == ">" and pagina < total_pag:
            pagina += 1
            continue
        if op == "<" and pagina > 1:
            pagina -= 1
            continue
        try:
            num = int(op)
            if 1 <= num <= len(bairros):
                b = bairros[num - 1]
                dados["bairro_id"]   = b["id"]
                dados["bairro_nome"] = b["nome"]
                return "local"
            # tentar ir pra página
            if 1 <= num <= total_pag:
                pagina = num
        except ValueError:
            pass
        erro("Opção inválida.")

def _etapa_local(dados):
    cabecalho("DIVULGAR OCORRÊNCIA", f"Passo 2 — Local em {dados['bairro_nome']}")
    print(f"  {DIM}Informe o logradouro, rua, avenida, praça, etc.{RESET}\n")
    local = pedir("Local específico:")
    if not local:
        return "bairro"
    dados["local_bairro"] = local
    return "titulo"

def _etapa_titulo(dados):
    cabecalho("DIVULGAR OCORRÊNCIA", "Passo 3 — Título / Assunto")
    print(f"  {DIM}Escreva um título curto que resuma a ocorrência.{RESET}")
    print(f"  {DIM}Exemplo: \"Alagamento na Rua da Vala\"{RESET}\n")
    titulo = pedir("Título:")
    if not titulo:
        return "local"
    dados["titulo"] = titulo
    return "conteudo"

def _etapa_conteudo(dados):
    cabecalho("DIVULGAR OCORRÊNCIA", "Passo 4 — Descrição")
    print(f"  {DIM}Descreva com detalhes o que aconteceu.{RESET}\n")
    print(f"  {BOLD}Conteúdo (pressione ENTER duas vezes para finalizar):{RESET}")
    linhas = []
    try:
        while True:
            linha = input("  ")
            if linha == "" and linhas and linhas[-1] == "":
                break
            linhas.append(linha)
    except (KeyboardInterrupt, EOFError):
        pass
    conteudo = "\n".join(linhas).strip()
    if not conteudo:
        aviso("Descrição vazia. Tente novamente.")
        return "conteudo"
    dados["conteudo"] = conteudo
    return "natureza"

def _etapa_natureza(dados, naturezas):
    cabecalho("DIVULGAR OCORRÊNCIA", "Passo 5 — Classificação (opcional)")
    print(f"  {DIM}Classifique a natureza desta ocorrência.{RESET}\n")
    for i, n in enumerate(naturezas, 1):
        print(f"  {CYAN}[{i}]{RESET} {n['nome']}")
    print(f"  {DIM}[0]{RESET} Não classificar")

    op = pedir("Classificação:")
    try:
        num = int(op)
        if num == 0:
            dados["natureza_id"]   = None
            dados["natureza_nome"] = "Não classificada"
        elif 1 <= num <= len(naturezas):
            dados["natureza_id"]   = naturezas[num-1]["id"]
            dados["natureza_nome"] = naturezas[num-1]["nome"]
        else:
            erro("Opção inválida.")
            return "natureza"
    except ValueError:
        erro("Digite um número.")
        return "natureza"
    return "confirmar"

def _etapa_confirmar(dados, usuario):
    while True:
        cabecalho("DIVULGAR OCORRÊNCIA", "Revisão — Confirme os dados")
        separador()
        print(f"  {BOLD}Bairro:{RESET}     {dados['bairro_nome']}")
        print(f"  {BOLD}Local:{RESET}      {dados['local_bairro']}")
        print(f"  {BOLD}Título:{RESET}     {dados['titulo']}")
        print(f"  {BOLD}Natureza:{RESET}   {dados['natureza_nome'] or 'Não classificada'}")
        separador()
        print(f"  {BOLD}Descrição:{RESET}")
        for linha in dados["conteudo"].split("\n")[:5]:
            print(f"  {DIM}{linha}{RESET}")
        separador()
        print(f"""
  {GREEN}[S]{RESET} Publicar
  {YELLOW}[E]{RESET} Editar
  {RED}[X]{RESET} Cancelar
""")
        op = pedir("Escolha:").upper()

        if op == "S":
            _salvar_postagem(dados, usuario)
            return "fim"
        elif op == "E":
            return _menu_editar(dados)
        elif op == "X":
            return "voltar"
        else:
            erro("Opção inválida.")

def _menu_editar(dados):
    cabecalho("EDITAR POSTAGEM", "O que deseja editar?")
    print(f"""
  {CYAN}[1]{RESET} Bairro
  {CYAN}[2]{RESET} Local
  {CYAN}[3]{RESET} Título
  {CYAN}[4]{RESET} Descrição
  {CYAN}[5]{RESET} Classificação
  {RED}[X]{RESET} Cancelar edição
""")
    op = pedir("Campo:").upper()
    mapa = {"1":"bairro","2":"local","3":"titulo","4":"conteudo","5":"natureza"}
    return mapa.get(op, "confirmar")

def _salvar_postagem(dados, usuario):
    status = "aprovado" if usuario else "aguardando"
    uid    = usuario["id"] if usuario else None
    nome   = usuario["nome"] if usuario else "Anônimo"

    with conectar() as conn:
        conn.execute(
            """INSERT INTO postagens
               (bairro_id, local_bairro, titulo, conteudo, natureza_id,
                usuario_id, autor_nome, status, criado_em)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (dados["bairro_id"], dados["local_bairro"], dados["titulo"],
             dados["conteudo"],  dados["natureza_id"],  uid, nome,
             status, agora_str())
        )
    if status == "aprovado":
        sucesso("Ocorrência publicada com sucesso!")
    else:
        aviso("Ocorrência enviada! Aguardando aprovação de um moderador.")
    pausar()

# ─── Votar útil ───────────────────────────────────────────────────────────────
def votar_util(postagem_id, usuario_id):
    with conectar() as conn:
        existe = conn.execute(
            "SELECT 1 FROM votos_uteis WHERE usuario_id=? AND postagem_id=?",
            (usuario_id, postagem_id)
        ).fetchone()
        if existe:
            return False
        conn.execute(
            "INSERT INTO votos_uteis (usuario_id, postagem_id) VALUES (?,?)",
            (usuario_id, postagem_id)
        )
        conn.execute(
            "UPDATE postagens SET votos_uteis = votos_uteis + 1 WHERE id=?",
            (postagem_id,)
        )
        return True

def ja_votou_util(postagem_id, usuario_id):
    with conectar() as conn:
        return bool(conn.execute(
            "SELECT 1 FROM votos_uteis WHERE usuario_id=? AND postagem_id=?",
            (usuario_id, postagem_id)
        ).fetchone())

# ─── Denunciar ────────────────────────────────────────────────────────────────
def denunciar_postagem(postagem_id, usuario_id):
    with conectar() as conn:
        existe = conn.execute(
            "SELECT 1 FROM denuncias_fake WHERE usuario_id=? AND postagem_id=?",
            (usuario_id, postagem_id)
        ).fetchone()
        if existe:
            return "ja_denunciou"
        conn.execute(
            "INSERT INTO denuncias_fake (usuario_id, postagem_id, criado_em) VALUES (?,?,?)",
            (usuario_id, postagem_id, agora_str())
        )
        conn.execute(
            "UPDATE postagens SET denuncias = denuncias + 1 WHERE id=?",
            (postagem_id,)
        )
        total = conn.execute(
            "SELECT denuncias FROM postagens WHERE id=?", (postagem_id,)
        ).fetchone()["denuncias"]
        if total >= LIMITE_DENUNCIAS:
            conn.execute(
                "UPDATE postagens SET status='oculto' WHERE id=?", (postagem_id,)
            )
            return "oculto"
        return "ok"

def ja_denunciou(postagem_id, usuario_id):
    with conectar() as conn:
        return bool(conn.execute(
            "SELECT 1 FROM denuncias_fake WHERE usuario_id=? AND postagem_id=?",
            (usuario_id, postagem_id)
        ).fetchone())

# ─── Exibir postagem completa ─────────────────────────────────────────────────
def exibir_postagem_completa(pid, usuario):
    post = _buscar_postagem(pid)
    if not post:
        erro("Postagem não encontrada.")
        pausar()
        return

    cabecalho(post["bairro_nome"] or "?", formatar_data_hora(post["criado_em"]))

    hora     = formatar_hora(post["criado_em"])
    natureza = post.get("natureza_nome") or "Não classificada"
    badge_nat = badge_natureza(natureza)

    print(f"  {BOLD}{hora} — {post['titulo']}{RESET}")
    print(f"  {badge_nat}")
    separador()
    print(f"  {BOLD}Local:{RESET} {post['local_bairro'] or 'Não informado'}")
    separador()
    print()
    for linha in post["conteudo"].split("\n"):
        print(f"  {linha}")
    print()
    separador()

    # Autor
    if post.get("usuario_nome"):
        badge_u = badge_usuario(post.get("usuario_tipo","comum"))
        orgao_txt = f" — {post['orgao']}" if post.get("orgao") else ""
        print(f"  {DIM}Publicado por:{RESET} {post['usuario_nome']} {badge_u}{DIM}{orgao_txt}{RESET}")

    votos = post["votos_uteis"]
    print(f"\n  {GREEN}{votos} {'pessoa achou' if votos == 1 else 'pessoas acharam'} isso útil.{RESET}")
    separador()

    # Ações
    uid = usuario["id"] if usuario else None

    # Útil
    if usuario:
        if ja_votou_util(pid, uid):
            print(f"  {DIM}Você já marcou esta postagem como útil.{RESET}")
        else:
            resp = pedir("Achou útil? (S/N):").upper()
            if resp == "S":
                votar_util(pid, uid)
                votos += 1
                sucesso(f"{votos} {'pessoa achou' if votos==1 else 'pessoas acharam'} isso útil.")
    else:
        print(f"  {DIM}Faça login para marcar como útil.{RESET}")

    # Denúncia
    if usuario:
        if ja_denunciou(pid, uid):
            print(f"  {DIM}Você já denunciou esta postagem.{RESET}")
        else:
            resp = pedir("Denunciar como fake news? (S/N):").upper()
            if resp == "S":
                resultado = denunciar_postagem(pid, uid)
                if resultado == "oculto":
                    aviso("Esta postagem atingiu o limite de denúncias e foi ocultada para revisão.")
                elif resultado == "ok":
                    sucesso("Denúncia registrada.")
                elif resultado == "ja_denunciou":
                    aviso("Você já denunciou esta postagem.")
    else:
        print(f"  {DIM}Faça login para denunciar.{RESET}")

    pausar()
