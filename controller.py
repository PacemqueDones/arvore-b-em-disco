def ler_int(linha: str) -> int:
    return int(linha.strip())

def parse_linha_operacao(linha: str):
    s = linha.strip()
    if not s:
        return None, None

    op = s[0]
    resto = s[1:].strip()

    # normaliza: troca vírgula por espaço e quebra
    tokens = resto.replace(",", " ").split()
    args = [int(tok) for tok in tokens] if tokens else []
    return op, args

def ler_cabecalho(caminho_arquivo: str):
    f = open(caminho_arquivo, "r", encoding="utf-8")
    try:
        d = ler_int(f.readline())
        return d, f
    except Exception:
        f.close()
        raise


def executar_operacoes(f, arvore):
    n = ler_int(f.readline())

    operacoes_lidas = 0
    for linha in f:
        op, args = parse_linha_operacao(linha)
        if op is None:
            continue

        if op == "I":
            chave, dado = args
            arvore.inserir(chave, dado)

        elif op == "R":
            (chave,) = args
            arvore.remover(chave)

        elif op == "B":
            (chave,) = args
            arvore.buscar(chave)

        operacoes_lidas += 1
        if operacoes_lidas == n:
            break