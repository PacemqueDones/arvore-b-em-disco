from controller import *
from b_tree_disk import BTree

caminho = "casos_teste/caso_teste_4.txt"

d, f = ler_cabecalho(caminho)
print(f'grau: d')
try:
    arvore = BTree(path = 'teste.txt', t = int(d/2), create=True)
    executar_operacoes(f, arvore)
finally:
    f.close()

arvore.print_tree_levels(arvore.raiz_idx)