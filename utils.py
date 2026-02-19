# Nome: Anderson Lucas de Paula
# Matrícula: 2025130753

from pathlib import Path

def preparar_caminhos(path):
    p = Path(path)

    # Caso 1: path contém sufixo
    if p.suffix:
        p.parent.mkdir(parents=True, exist_ok=True)
        caminho_bin = p.with_suffix('.bin')
        caminho_txt = p.with_suffix('.txt')

    # Caso 2: path não contém sufixo
    else:
        p.mkdir(parents=True, exist_ok=True)
        caminho_bin = p / "resposta.bin"
        caminho_txt = p / "resposta.txt"

    return caminho_bin, caminho_txt