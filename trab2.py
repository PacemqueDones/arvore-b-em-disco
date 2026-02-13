from controller import *
from b_tree_disk import BTree
import sys

#arquivo_entrada = sys.argv[1]
#arquivo_saida = sys.argv[2]

arquivo_entrada = "casos_teste/caso_teste_4.txt"
arquivo_saida = 'output/teste.bin'

# lê o valor de d (ordem máxima) e o arquivo com operações
d, f = ler_cabecalho(arquivo_entrada)
d=2
print(d, (d + 1) // 2)
try:
    # Calcule o grau mínimo (t) como o teto da metade de d.
    # Isso permite aceitar casos em que o número máximo de filhos (d) é ímpar.
    t_min = (d + 1) // 2
    # Cria a árvore B com grau mínimo calculado
    with BTree(path=arquivo_saida, t=t_min, create=True) as arvore:
        executar_operacoes(f, arvore)
        # Imprime a árvore em níveis para depuração
        arvore.print_tree_levels(arvore.raiz_idx)
finally:
    f.close()