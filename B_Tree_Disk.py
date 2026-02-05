from node import Node
import struct

class BTree:
    def __init__(self, path: str, t: int, create: bool):
        self.t = t
        self.path = path

        mode = "w+b" if create else "r+b"
        self.f = open(path, mode)

        if create:
            self.raiz = Node(True, 0)
            self.idx = 1
        else:
            t, idx, raiz_idx = self.read_head()
            raiz = self.read_node(raiz_idx)

            self.t = t
            self.idx = idx
            self.raiz = raiz


    def head_size(self) -> int:
        fmt = "iii"
        return struct.calcsize(fmt)

    def write_head(self):
        self.f.seek(0)
        bin_head = struct.pack("iii", self.t, self.idx, self.raiz.idx)
        self.f.write(bin_head)

    def read_head(self):
        size = self.head_size()
        head = self.f.read(size)
        t, idx, raiz_idx = head
        return t, idx, raiz_idx

    def read_head(self):
        self.f.seek(0)
        head = self.f.read(self.head_size())
        t, idx, raiz_idx = struct.unpack("iii", head)
        return t, idx, raiz_idx

    def busca(self, chave: int, node = None):
        node = self.raiz if node == None else node

        i = 0
        while i < node.n and chave > node.chaves[i]:
            i += 1

        # achou
        if i < node.n and chave == node.chaves[i]:
            return (node, i)

        # se é folha, para aqui (não achou; este é o nó candidato à inserção)
        elif node.folha:
            return None

        else:
            return self.busca(chave, node.filhos[i])

    def split(self, pai: Node, indice: int):
        t = self.t

        # y é um filho de pai, mas um filho cheio de chaves
        y = pai.filhos[indice]

        # cria um novo nó.
        z = Node(y.folha, self.idx)
        self.idx += 1

        # o novo nó agora é filho de pai
        pai.filhos.insert(indice + 1, z.idx)

        # promove chave e registro do meio
        pai.chaves.insert(indice, y.chaves[t - 1])
        pai.registros.insert(indice, y.registros[t - 1])

        # direita recebe parte alta
        z.chaves = y.chaves[t: (2 * t) - 1]
        z.registros = y.registros[t:(2 * t) - 1]

        # esquerda fica com parte baixa
        y.chaves = y.chaves[0: t - 1]
        y.registros = y.registros[0:t - 1]

        # se y não é folha, reatribuimos os filhos de y em y e z
        if not y.folha:
            z.filhos = y.filhos[t: 2 * t]
            y.filhos = y.filhos[0: t]


    def insert(self, k: int, valor: int):
        t = self.t
        raiz = self.raiz

        # if a raiz está cheia, splite-a
        if raiz.n == (2 * t) - 1:
            nova_raiz = Node()
            self.idx += 1
            self.raiz = nova_raiz
            nova_raiz.filhos.insert(0, raiz)
            self.split(nova_raiz, 0)
            self.insert_non_full(nova_raiz, k, valor)
        else:
            self.insert_non_full(raiz, k, valor)

    def insert_non_full(self, node: Node, k: int, valor:int):
        t = self.t
        i = node.n - 1

        # encontra a posição correta na folha
        if node.folha:
            node.chaves.append(None)
            node.registros.append(None)
            while i >= 0 and k < node.chaves[i]:
                node.chaves[i + 1] = node.chaves[i]
                node.registros[i + 1] = node.registros[i]
                i -= 1
            node.chaves[i + 1] = k
            node.registros[i + 1] = valor
        # se não é folha
        else:
            while i >= 0 and k < node.chaves[i]:
                i -= 1
            i += 1
            # if no filho está cheio splite-o
            if node.filhos[i].n == (2 * t) - 1:
                self.split(node, i)
                if k > node.chaves[i]:
                    i += 1
            self.insert_non_full(node.filhos[i], k, valor)

    def delete(self, node: Node, k: int):
        t = self.t
        i = 0

        while i < node.n and k > node.chaves[i]:
            i += 1
        if node.folha:
            if i < node.n and node.chaves[i] == k:
                node.chaves.pop(i)
                node.registros.pop(i)
            return

        if i < node.n and node.chaves[i]==k:
            return self.delete_internal_node(node, k, i)
        elif node.filhos[i].n >= t:
            self.delete(node.filhos[i], k)
        else:
            if i != 0 and i + 2 < len(node.filhos):
                if node.filhos[i - 1].n >= t:
                    self.delete_sibling(node, i, i - 1)
                elif node.filhos[i + 1].n >= t:
                    self.delete_sibling(node, i, i + 1)
                else:
                    self.delete_merge(node, i, i + 1)
            elif i == 0:
                if node.filhos[i + 1].n >= t:
                    self.delete_sibling(node, i, i + 1)
                else:
                    self.delete_merge(node, i, i + 1)
            elif i + 1 == len(node.filhos):
                if node.filhos[i - 1].n >= t:
                    self.delete_sibling(node, i, i - 1)
                else:
                    self.delete_merge(node, i, i - 1)
            self.delete(node.filhos[i], k)

    def delete_internal_node(self, node: Node, k: int, i: int):
        t = self.t
        if node.folha:
            if node.chaves[i] == k:
                node.chaves.pop(i)
            return

        if node.filhos[i].n >= t:
            k_pred, v_pred = self.delete_predecessor(node.filhos[i])
            node.chaves[i] = k_pred
            node.registros[i] = v_pred
            return
        elif node.filhos[i + 1].n >= t:
            node.chaves[i] = self.delete_successor(node.filhos[i + 1])
            return
        else:
            self.delete_merge(node, i, i + 1)
            self.delete_internal_node(node.filhos[i], k, self.t - 1)

    def delete_predecessor(self, node: Node):
        if node.folha:
            k = node.chaves.pop()
            v = node.registros.pop()
            return k, v

        n = node.n - 1
        if node.filhos[n].n >= self.t:
            self.delete_sibling(node, n + 1, n)
        else:
            self.delete_merge(node, n, n + 1)
        return self.delete_predecessor(node.filhos[n])

    def delete_successor(self, node):
        if node.folha:
            k = node.chaves.pop(0)
            v = node.registros.pop(0)
            return k, v

        if node.filhos[1].n >= self.t:
            self.delete_sibling(node, 0, 1)
        else:
            self.delete_merge(node, 0, 1)
        return self.delete_successor(node.filhos[0])

    def delete_merge(self, node, i, j):
        cnode = node.filhos[i]

        if j > i:
            rsnode = node.filhos[j]
            cnode.chaves.append(node.chaves[i])
            cnode.registros.append(node.registros[i])
            for k in range(rsnode.n):
                cnode.chaves.append(rsnode.chaves[k])
                if len(rsnode.filhos) > 0:
                    cnode.filhos.append(rsnode.filhos[k])
            if len(rsnode.filhos) > 0:
                cnode.filhos.append(rsnode.filhos.pop())
            novo = cnode
            node.chaves.pop(i)
            node.registros.pop(i)
            node.filhos.pop(j)

        else:
            lsnode = node.filhos[j]
            lsnode.chaves.append(node.chaves[j])
            lsnode.registros.append(node.registros[j])
            for i in range(cnode.n):
                lsnode.chaves.append(cnode.chaves[i])
                if len(lsnode.filhos) > 0:
                    lsnode.filhos.append(cnode.filhos[i])
            if len(lsnode.filhos) > 0:
                lsnode.filhos.append(cnode.filhos.pop())
            novo = lsnode
            node.chaves.pop(j)
            node.registros.pop(i)
            node.filhos.pop(i)

        if node == self.raiz and node.n == 0:
            self.raiz = novo

    def delete_sibling(self, node, i, j):
        cnode = node.filhos[i]
        if i < j:
            rsnode = node.filhos[j]

            cnode.chaves.append(node.chaves[i])
            cnode.registros.append(node.registros[i])

            node.chaves[i] = rsnode.chaves[0]
            node.registros[i] = rsnode.registros[0]
            if len(rsnode.filhos) > 0:
                cnode.filhos.append(rsnode.filhos[0])
                rsnode.filhos.pop(0)
            rsnode.chaves.pop(0)
            rsnode.registros.pop(0)
        else:
            lsnode = node.filhos[j]

            cnode.chaves.insert(0, node.chaves[i - 1])
            cnode.registros.insert(0, node.registros[i - 1])

            node.chaves[i - 1] = lsnode.chaves.pop()
            node.registros[i - 1] = lsnode.registros.pop()
            if len(lsnode.filhos) > 0:
                cnode.filhos.insert(0, lsnode.filhos.pop())

    def get(self, chave):
        res = self.busca(chave)
        if res is None:
            return None
        node, i = res
        return node.registros[i]

    def print_tree(self, node, level=0):
        print(f'Level {level}', end=": ")

        for i in node.chaves:
            print(i, end=" ")

        print()
        level += 1

        if len(node.filhos) > 0:
            for i in node.filhos:
                self.print_tree(i, level)