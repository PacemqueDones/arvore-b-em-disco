from controller import *
from b_tree_disk import BTree
import sys

#arquivo_entrada = sys.argv[1]
#arquivo_saida = sys.argv[2]

arquivo_entrada = "casos_teste/caso_teste_2.txt"
arquivo_saida = 'teste.bin'

d, f = ler_cabecalho(arquivo_entrada)

try:
<<<<<<< Updated upstream
    with BTree(path="teste.bin", t=(d+1)//2, create=True) as arvore:
=======
    with BTree(path=arquivo_saida, t=2, create=True) as arvore:
>>>>>>> Stashed changes
        executar_operacoes(f, arvore)
        arvore.print_tree_levels(arvore.raiz_idx)
finally:
    f.close()