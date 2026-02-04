import math

class Node:
    def __init__(self, folha=False):
        self.chaves =  []
        self.filhos = []
        self.registros = []
        self.folha = folha
        self.n = 0