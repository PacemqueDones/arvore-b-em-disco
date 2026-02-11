import struct

class Node:
    def __init__(self, folha=False, idx=None):
        self.idx = idx
        self.chaves = []  # list[int]
        self.filhos = []  # list[int] posições no arquivo (ou -1)
        self.registros = []  # list[int]
        self.folha = folha

    @property
    def n(self):
        return len(self.chaves)

    def to_bytes(self, t: int) -> bytes:
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
        max_chaves = 2 * t - 1
        max_filhos = 2 * t
        fmt = fmt = f"?ii{max_chaves}i{max_chaves}i{max_filhos}i"
        return struct.calcsize(fmt)