from controller import *
from b_tree_disk import BTree

caminho = "casos_teste/caso_teste_4.txt"

d, f = ler_cabecalho(caminho)
print(f'grau: {d//2}')
try:
    with BTree(path="teste.bin", t=(d+1)//2, create=True) as arvore:
        executar_operacoes(f, arvore)
        arvore.print_tree_levels(arvore.raiz_idx)
finally:
    f.close()