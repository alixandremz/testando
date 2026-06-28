from dados.database import conectar
from modulos.utils import cabecalho, pausar, formatar_data, paginar


def _calcular_confiabilidade(usuario_id):
    with conectar() as conn:
        resultado = conn.execute("""
            SELECT 
                COALESCE(SUM(votos_uteis), 0) AS total_uteis,
                COALESCE(SUM(denuncias), 0)   AS total_denuncias
            FROM postagens
            WHERE usuario_id = ? AND status != 'aguardando'
        """, (usuario_id,)).fetchone()

    uteis     = resultado["total_uteis"]
    denuncias = resultado["total_denuncias"]
    total     = uteis + denuncias

    if total == 0:
        return "Sem avaliações ainda"

    percentual = round((uteis / total) * 100)
    return f"{percentual}% confiável"


def _buscar_postagens_usuario(usuario_id):
    with conectar() as conn:
        return [dict(r) for r in conn.execute("""
            SELECT p.*, b.nome AS bairro_nome, n.nome AS natureza_nome
            FROM postagens p
            LEFT JOIN bairros b   ON b.id = p.bairro_id
            LEFT JOIN naturezas n ON n.id = p.natureza_id
            WHERE p.usuario_id = ?
            ORDER BY p.criado_em DESC
        """, (usuario_id,)).fetchall()]


def _buscar_bairro_usuario(usuario_id):
    with conectar() as conn:
        resultado = conn.execute("""
            SELECT b.nome
            FROM usuarios u
            LEFT JOIN bairros b ON b.id = u.bairro_id
            WHERE u.id = ?
        """, (usuario_id,)).fetchone()
    if resultado and resultado[0]:
        return resultado[0]
    return None


def _buscar_bairros():
    with conectar() as conn:
        return [dict(r) for r in conn.execute(
            "SELECT * FROM bairros ORDER BY nome"
        ).fetchall()]


def _definir_bairro(usuario_id):
    """Permite ao usuário escolher seu bairro."""
    bairros = _buscar_bairros()
    pagina = 1

    while True:
        itens, pagina, total = paginar(bairros, 10, pagina)
        cabecalho("DEFINIR MEU BAIRRO")
        print(f"  Página {pagina}/{total}\n")

        for i, b in enumerate(itens, start=(pagina - 1) * 10 + 1):
            print(f"  [{i:>2}] {b['nome']}")

        print("\n  [>] Próxima  [<] Anterior  [X] Cancelar")
        op = input("\n  Escolha seu bairro: ").strip().upper()

        if op == "X":
            return
        if op == ">" and pagina < total:
            pagina += 1
            continue
        if op == "<" and pagina > 1:
            pagina -= 1
            continue
        try:
            num = int(op)
            if 1 <= num <= len(bairros):
                bairro = bairros[num - 1]
                with conectar() as conn:
                    conn.execute(
                        "UPDATE usuarios SET bairro_id = ? WHERE id = ?",
                        (bairro["id"], usuario_id)
                    )
                print(f"\n  Bairro definido: {bairro['nome']}")
                pausar()
                return
        except ValueError:
            pass
        print("  Opção inválida.")


def _exibir_postagens(postagens, usuario_dono, usuario_logado):
    """Exibe as postagens do perfil com paginação."""
    if not postagens:
        print("\n  Nenhuma ocorrência publicada ainda.")
        pausar()
        return

    pagina = 1
    POR_PAGINA = 5

    while True:
        itens, pagina, total = paginar(postagens, POR_PAGINA, pagina)
        cabecalho(f"POSTAGENS DE {usuario_dono['nome'].upper()}")
        print(f"  {len(postagens)} postagem(ns) — Página {pagina}/{total}\n")

        for i, post in enumerate(itens, start=(pagina - 1) * POR_PAGINA + 1):
            status_tag = {
                "aprovado":   "[✓]",
                "aguardando": "[?]",
                "oculto":     "[!]",
            }.get(post["status"], "[ ]")

            bairro = (post.get("bairro_nome") or "?").upper()
            data   = formatar_data(post["criado_em"])
            nat    = post.get("natureza_nome") or "Sem classificação"
            votos  = post["votos_uteis"]

            print(f"  {status_tag} [{i}] {post['titulo']}")
            print(f"       Bairro: {bairro}  |  {nat}")
            print(f"       Data: {data}  |   {votos} útil(is)")
            print()

        print("  [>] Próxima  [<] Anterior  [X] Voltar")

        # Só permite abrir postagem se logado
        if usuario_logado:
            print("  Número = Ver postagem completa")

        op = input("\n  Comando: ").strip().upper()

        if op == "X":
            return
        if op == ">" and pagina < total:
            pagina += 1
            continue
        if op == "<" and pagina > 1:
            pagina -= 1
            continue
        if usuario_logado:
            try:
                num = int(op)
                idx = (pagina - 1) * POR_PAGINA + (num - 1)
                if 0 <= idx < len(postagens):
                    from modulos.postagens import ler_postagem
                    ler_postagem(postagens[idx]["id"], usuario_logado)
                    continue
            except ValueError:
                pass
        print("  Opção inválida.")


def ver_perfil(usuario_alvo_id, usuario_logado):
    """Exibe o perfil de qualquer usuário."""
    with conectar() as conn:
        usuario = conn.execute(
            "SELECT * FROM usuarios WHERE id = ?", (usuario_alvo_id,)
        ).fetchone()

    if not usuario:
        print("\n  Usuário não encontrado.")
        pausar()
        return

    usuario = dict(usuario)
    postagens = _buscar_postagens_usuario(usuario_alvo_id)
    bairro    = _buscar_bairro_usuario(usuario_alvo_id)
    nivel     = _calcular_confiabilidade(usuario_alvo_id)
    eh_dono   = usuario_logado and usuario_logado["id"] == usuario_alvo_id

    tipo_label = {
        "comum":      "Cidadão",
        "moderador":  "Moderador",
        "servidor":   "Servidor Público",
    }.get(usuario["tipo"], usuario["tipo"].capitalize())

    while True:
        cabecalho("PERFIL DE USUÁRIO")

        print(f"    {usuario['nome']}")
        print(f"    {tipo_label}")
        print(f"    {bairro or 'Bairro não informado'}")
        print(f"    {nivel}")
        print(f"    {len(postagens)} postagem(ns) publicada(s)")
        print()
        print("  " + "-" * 46)
        print()
        print("  [1] Ver postagens")

        if eh_dono:
            print("  [2] Alterar meu bairro")

        print("  [X] Voltar")

        op = input("\n  Escolha: ").strip().upper()

        if op == "X":
            return
        elif op == "1":
            _exibir_postagens(postagens, usuario, usuario_logado)
            # Recarrega postagens ao voltar (caso tenha interagido)
            postagens = _buscar_postagens_usuario(usuario_alvo_id)
        elif op == "2" and eh_dono:
            _definir_bairro(usuario_alvo_id)
            bairro = _buscar_bairro_usuario(usuario_alvo_id)
        else:
            print("  Opção inválida.")


def menu_meu_perfil(usuario_logado):
    """Atalho para ver o próprio perfil."""
    if not usuario_logado:
        print("\n  Faça login para ver seu perfil.")
        pausar()
        return
    ver_perfil(usuario_logado["id"], usuario_logado)