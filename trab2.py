# Nome: Anderson Lucas de Paula
# Matrícula: 2025130753

from controller import *
from b_tree_disk import BTree
import sys

def main():
    arquivo_entrada = sys.argv[1]
    arquivo_saida = sys.argv[2]

    create_mode = True
    if len(sys.argv) > 3 and sys.argv[3].lower() == "open":
        create_mode = False

    # lê o valor de d (ordem máxima) e o arquivo com operações (f)
    d, f = ler_cabecalho(arquivo_entrada)
    try:
        # Calcule o grau mínimo (t) como o teto da metade de d.
        t_min = (d + 1) // 2
        # Cria a árvore B com grau mínimo
        with BTree(path=arquivo_saida, t=t_min, create=create_mode) as arvore:
            executar_operacoes(f, arvore)
            # Imprime a árvore em níveis
            arvore.print_tree_levels(arvore.raiz_idx)
    finally:
            f.close()

if __name__ == "__main__":
    main()