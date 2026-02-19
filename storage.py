# Nome: Anderson Lucas de Paula
# Matrícula: 2025130753

import struct
from node import Node
"""
Camada de persistência da B-tree.

Responsável por:
    - Gerenciar arquivo binário.
    - Calcular offsets.
    - Ler e escrever nós em posições fixas.
    - Manter cabeçalho com metadados da árvore.
"""

class Storage:
    """
    Gerencia persistência em arquivo binário.

    Cabeçalho do arquivo:
        - t (grau mínimo)
        - next_idx (próximo índice livre)
        - root_idx (índice da raiz)
    """
    HEAD_FMT = "iii"  # t, next_idx, root_idx

    def __init__(self, path: str, create: bool):
        self.f = open(path, "w+b" if create else "r+b")

    def close(self):
        self.f.flush()
        self.f.close()

    def head_size(self):
        return struct.calcsize(self.HEAD_FMT)

    def write_head(self, d: int, next_idx: int, root_idx: int):
        """
        Escreve metadados no início do arquivo.
        """
        self.f.seek(0)
        self.f.write(struct.pack(self.HEAD_FMT, d, next_idx, root_idx))

    def read_head(self):
        """
        Lê metadados armazenados no cabeçalho.
        """
        self.f.seek(0)
        data = self.f.read(self.head_size())
        return struct.unpack(self.HEAD_FMT, data)

    def node_offset(self, d: int, idx: int):
        """
        Calcula offset em bytes de um nó dado seu índice lógico.
        """
        return self.head_size() + idx * Node.byte_size(d)

    def read_node(self, d: int, idx: int):
        """
        Lê nó do disco a partir do índice lógico.
        """
        self.f.seek(self.node_offset(d, idx))
        data = self.f.read(Node.byte_size(d))
        return Node.from_bytes(d, data)

    def write_node(self, d: int, node):
        """
        Persiste nó no disco na posição correspondente ao seu índice.
        """
        self.f.seek(self.node_offset(d, node.idx))
        self.f.write(node.to_bytes(d))
