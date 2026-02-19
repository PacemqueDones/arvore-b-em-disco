# Nome: Anderson Lucas de Paula
# Matrícula: 2025130753

import struct

"""
Definição estrutural de um nó da B-tree.

Estrutura física em disco:
    - folha (bool)
    - n (int): número de chaves válidas
    - idx (int): índice do nó no arquivo
    - chaves (2t - 1 inteiros)
    - registros (2t - 1 inteiros)
    - filhos (2t inteiros)

Todos os nós possuem tamanho fixo em bytes.
"""

class Node:
    def __init__(self, folha=False, idx=None):
        """
        Representa um nó lógico da B-tree.

        A responsabilidade desta classe é:
            - Manter estrutura em memória.
            - Serializar/deserializar para formato binário fixo.
        """
        self.idx = idx
        self.chaves = []  # list[int]
        self.filhos = []  # list[int] posições no arquivo (ou -1)
        self.registros = []  # list[int]
        self.folha = folha

    @property
    def n(self):
        return len(self.chaves)

    def to_bytes(self, t: int) -> bytes:
        """
        Serializa o nó para formato binário de tamanho fixo.

        Garante:
            - Preenchimento com -1 para posições não utilizadas.
            - Tamanho constante independente de n.
        """
        max_chaves = 2 * t - 1
        max_filhos = 2 * t

        chaves = self.chaves + [-1] * (max_chaves - self.n)
        registros = self.registros + [-1] * (max_chaves - self.n)

        if self.folha:
            filhos = [-1] * max_filhos
        else:
            filhos = self.filhos + [-1] * (max_filhos - len(self.filhos))

        fmt = f"?ii{max_chaves}i{max_chaves}i{max_filhos}i"
        return struct.pack(fmt, self.folha, self.n, self.idx, *chaves, *registros, *filhos)

    @classmethod
    def from_bytes(cls, t: int, data: bytes):
        """
        Reconstrói um nó a partir de sua representação binária.

        Lê apenas as primeiras n chaves e registros válidos.
        Para nós internos, mantém apenas n+1 filhos.
        """
        max_chaves = 2 * t - 1
        max_filhos = 2 * t
        fmt = f"?ii{max_chaves}i{max_chaves}i{max_filhos}i"

        descompactado = struct.unpack(fmt, data)

        folha = descompactado[0]
        n = descompactado[1]
        idx = descompactado[2]

        inicio_chaves = 3
        fim_chaves = inicio_chaves + max_chaves
        registros_end = fim_chaves + max_chaves
        fim_filhos = registros_end + max_filhos

        chaves = list(descompactado[inicio_chaves:fim_chaves])[:n]
        registros = list(descompactado[fim_chaves:registros_end])[:n]
        filhos_brutos = list(descompactado[registros_end:fim_filhos])

        node = cls(folha=folha, idx=idx)
        node.chaves = chaves
        node.registros = registros
        node.filhos = [] if folha else filhos_brutos[:n + 1]

        return node

    @classmethod
    def byte_size(cls, t: int) -> int:
        """
        Retorna o tamanho fixo (em bytes) de um nó
        para determinado grau mínimo t.
        """
        max_chaves = 2 * t - 1
        max_filhos = 2 * t
        fmt = fmt = f"?ii{max_chaves}i{max_chaves}i{max_filhos}i"
        return struct.calcsize(fmt)