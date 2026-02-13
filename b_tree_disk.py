# Nome: Anderson Lucas de Paula
# Matrícula: 2025130753

from node import Node
from storage import Storage
from collections import deque
from utils import preparar_caminhos

"""
Observação importante:

Esta implementação segue o modelo por grau mínimo (t).
Portanto, o número máximo de filhos por nó é sempre 2t (par).
O parâmetro d do arquivo de entrada é convertido para t = d//2.
"""

class BTree:
    def __init__(self, path: str, t: int, create: bool):
        """
        Implementação de uma B-tree persistida em disco.

        Modelo utilizado:
            - Grau mínimo: t
            - Máximo de chaves por nó: 2t - 1
            - Máximo de filhos por nó: 2t
            - Mínimo de chaves (exceto raiz): t - 1
            - Mínimo de filhos (exceto raiz): t

        Invariantes:
            1. As chaves em cada nó são crescentes.
            2. Para um nó com n chaves existem n+1 filhos (se não for folha).
            3. A árvore é split top-down.
        """
        self.t = t
    
        caminho_bin, caminho_txt = preparar_caminhos(path)        
        self.txt = open(caminho_txt, "w", encoding="utf-8")
        self.storage = Storage(caminho_bin, create=create)  # storage abre o arquivo

        if create:
            self.raiz_idx = 0
            self.idx = 1                      # próximo índice livre

            raiz = Node(True, idx=self.raiz_idx)
            self.storage.write_node(self.t, raiz)
            self.storage.write_head(self.t, self.idx, self.raiz_idx)

        else:
            self.t, self.idx, self.raiz_idx = self.storage.read_head()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.storage.close()
        self.txt.close()
        return False

    def search_node(self, chave: int, idx = None):
        """
        Busca recursiva ena árvore-B.

        Retorna:
            (node, i) se chave encontrada
            None caso contrário

        Observação:
            A busca desce para o filho i tal que:
                chaves[i-1] < chave < chaves[i]
        """
        node_idx = self.raiz_idx if idx is None else idx
        node = self.storage.read_node(self.t, node_idx)

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
            return self.search_node(chave, node.filhos[i])
        
    def search(self, chave: int, idx=None):
        res = self.search_node(chave, idx)

        if res is None:
            self.txt.write("O REGISTRO NAO ESTA NA ARVORE!\n")
        else:
            self.txt.write(f"O REGISTRO ESTA NA ARVORE!\n")
        return res 

    def split(self, pai_idx: int, indice: int):
        """
        Divide o filho cheio y = pai.filhos[indice].

        Estratégia:
            - y possui 2t - 1 chaves (nó cheio).
            - A chave mediana (posição t-1) sobe para o pai.
            - As t-1 menores permanecem em y.
            - As t-1 maiores vão para novo nó z.
            - Se não for folha, redistribui também os filhos.
        """
        t = self.t

        # y é um filho de pai, mas um filho cheio de chaves
        pai = self.storage.read_node(t, pai_idx)
        y_idx = pai.filhos[indice]
        y = self.storage.read_node(t, y_idx)

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

        self.storage.write_node(t, pai)
        self.storage.write_node(t, y)
        self.storage.write_node(t, z)

    def insert(self, k: int, valor: int):
        """
        Inserção em B-tree com estratégia top-down.

        Estratégia:
            - Antes de descer, garante que o nó filho não esteja cheio.
            - Se raiz estiver cheia, cria nova raiz e faz split.
            - Nunca desce para um nó cheio.
        """
        # evita duplicata: atualiza (ou ignora) se já existe
        res = self.search_node(k)
        if res is not None:
            node, i = res
            node.registros[i] = valor  # "update" do valor
            self.storage.write_node(self.t, node)
            return

        t = self.t
        raiz = self.storage.read_node(self.t, self.raiz_idx)

        # if a raiz está cheia, splite-a
        if raiz.n == (2 * t) - 1:
            nova_raiz = Node(folha=False, idx = self.idx)
            self.raiz_idx = self.idx
            self.idx += 1
            nova_raiz.filhos.insert(0, raiz.idx)
            self.storage.write_node(self.t, nova_raiz)
            self.split(nova_raiz.idx, 0)
            self.insert_non_full(nova_raiz.idx, k, valor)
        else:
            self.insert_non_full(raiz.idx, k, valor)

        self.storage.write_head(self.t, self.idx, self.raiz_idx)

    def insert_non_full(self, node_idx: int, k: int, valor:int):
        """
        Insere chave em nó garantidamente não cheio.

        Caso 1: nó folha -> insere ordenadamente.
        Caso 2: nó interno -> desce para filho apropriado,
                fazendo split se necessário antes da descida.
        """
        t = self.t
        node = self.storage.read_node(t, node_idx)
        i = node.n - 1

        if node.folha:
            node.chaves.append(None)
            node.registros.append(None)
            while i >= 0 and k < node.chaves[i]:
                node.chaves[i + 1] = node.chaves[i]
                node.registros[i + 1] = node.registros[i]
                i -= 1
            node.chaves[i + 1] = k
            node.registros[i + 1] = valor

            self.storage.write_node(t, node)
            return
        
        # se não é folha
        else:
            while i >= 0 and k < node.chaves[i]:
                i -= 1
            i += 1
            child_idx = node.filhos[i]
            child = self.storage.read_node(t, child_idx)
            if child.n == (2*t) - 1:
                self.split(node_idx, i)
                node = self.storage.read_node(t, node_idx)
                if k > node.chaves[i]:
                    i += 1
            self.insert_non_full(node.filhos[i], k, valor)

    def delete(self, chave: int):
        """
        Interface pública de remoção.

        Delegada para _delete_recursive iniciando na raiz.
        """
        self._delete_recursive(self.raiz_idx, chave)

    def _delete_recursive(self, node_idx: int, k: int):
        """
        Remoção em B-tree.

        Invariante mantida:
            Ao descer na árvore, garante-se que o filho tenha
            pelo menos t chaves (exceto raiz).
        """
        t = self.t
        node = self.storage.read_node(t, node_idx)

        i = 0
        while i < node.n and k > node.chaves[i]:
            i += 1

        if node.folha:
            if i < node.n and node.chaves[i] == k:
                node.chaves.pop(i)
                node.registros.pop(i)
                self.storage.write_node(t, node)
            return

        # caso chave no nó interno
        if i < node.n and node.chaves[i] == k:
            return self.delete_internal_node(node_idx, k, i)

        child_idx = node.filhos[i]
        child = self.storage.read_node(t, child_idx)

        if child.n >= t:
            return self._delete_recursive(child_idx, k)

        if i != 0:
            left_idx = node.filhos[i - 1]
            left = self.storage.read_node(t, left_idx)
        else:
            left = None

        if i + 1 < len(node.filhos):
            right_idx = node.filhos[i + 1]
            right = self.storage.read_node(t, right_idx)
        else:
            right = None

        if left is not None and left.n >= t:
            # empresta do irmão esquerdo
            self.delete_sibling(node_idx, i, i - 1)

            node = self.storage.read_node(t, node_idx)
            return self._delete_recursive(node.filhos[i], k)

        if right is not None and right.n >= t:
            self.delete_sibling(node_idx, i, i + 1)

            node = self.storage.read_node(t, node_idx)
            return self._delete_recursive(node.filhos[i], k)

        if right is not None:
            self.delete_merge(node_idx, i, i + 1)

            node = self.storage.read_node(t, node_idx)
            return self._delete_recursive(node.filhos[i], k)
        else:
            self.delete_merge(node_idx, i - 1, i)

            node = self.storage.read_node(t, node_idx)
            return self._delete_recursive(node.filhos[i - 1], k)

    def delete_internal_node(self, node_idx: int, k: int, i: int):
        """
        Remove chave localizada em nó interno.

        Estratégia da B-tree:

        Caso 1:
            Filho esquerdo possui pelo menos t chaves ->
            substitui pela predecessora.

        Caso 2:
            Filho direito possui pelo menos t chaves ->
            substitui pela sucessora.

        Caso 3:
            Ambos possuem t-1 chaves ->
            realiza merge e continua remoção recursivamente.

        Garante preservação das invariantes estruturais.
        """
        t = self.t
        node = self.storage.read_node(t, node_idx)

        if node.folha:
            if node.chaves[i] == k:
                node.chaves.pop(i)
                node.registros.pop(i)
                self.storage.write_node(t, node)
            return

        left_idx = node.filhos[i]
        right_idx = node.filhos[i + 1]

        left = self.storage.read_node(t, left_idx)
        right = self.storage.read_node(t, right_idx)

        if left.n >= t:
            k_pred, v_pred = self.delete_predecessor(left_idx)

            node = self.storage.read_node(t, node_idx)
            node.chaves[i] = k_pred
            node.registros[i] = v_pred
            self.storage.write_node(t, node)
            return

        if right.n >= t:
            k_succ, v_succ = self.delete_successor(right_idx)

            node = self.storage.read_node(t, node_idx)
            node.chaves[i] = k_succ
            node.registros[i] = v_succ
            self.storage.write_node(t, node)
            return

        self.delete_merge(node_idx, i, i + 1)

        node = self.storage.read_node(t, node_idx)
        merged_idx = node.filhos[i]
        return self.delete_internal_node(merged_idx, k, t - 1)

    def delete_predecessor(self, node_idx: int):
        """
        Retorna e remove a maior chave da subárvore.

        Processo:
            - Desce sempre pelo filho mais à direita.
            - Antes de descer, garante que o filho tenha ≥ t chaves.
            - Se necessário, realiza borrow ou merge.

        Mantém a propriedade de mínimo t-1 chaves por nó.
        """
        t = self.t
        node = self.storage.read_node(t, node_idx)

        # caso base: folha
        if node.folha:
            k = node.chaves.pop()
            v = node.registros.pop()
            self.storage.write_node(t, node)
            return k, v

        # filho mais à direita: índice = node.n
        last = node.n
        child_idx = node.filhos[last]
        child = self.storage.read_node(t, child_idx)

        # garantir que o filho tenha pelo menos t chaves
        if child.n < t:
            left_pos = last - 1
            left_idx = node.filhos[left_pos]
            left = self.storage.read_node(t, left_idx)

            if left.n >= t:
                # empresta do irmão esquerdo
                self.delete_sibling(node_idx, last, left_pos)
            else:
                # merge: resultado fica na posição left_pos
                self.delete_merge(node_idx, left_pos, last)

                # após merge, o filho correto passa a ser left_pos
                node = self.storage.read_node(t, node_idx)
                child_idx = node.filhos[left_pos]
                return self.delete_predecessor(child_idx)

            # após borrow, relê o pai para segurança
            node = self.storage.read_node(t, node_idx)
            child_idx = node.filhos[last]

        return self.delete_predecessor(child_idx)
    
    def delete_successor(self, node_idx: int):
        """
        Retorna e remove a menor chave da subárvore.

        Processo simétrico ao delete_predecessor:
            - Desce sempre pelo filho mais à esquerda.
            - Garante ≥ t chaves antes da descida.
        """
        t = self.t
        node = self.storage.read_node(t, node_idx)

        # caso base: folha
        if node.folha:
            k = node.chaves.pop(0)
            v = node.registros.pop(0)
            self.storage.write_node(t, node)
            return k, v

        # sucessor desce sempre no filho mais à esquerda: posição 0
        first = 0
        child_idx = node.filhos[first]
        child = self.storage.read_node(t, child_idx)

        # garantir que o filho tenha pelo menos t chaves antes de descer
        if child.n < t:
            right_pos = first + 1
            right_idx = node.filhos[right_pos]
            right = self.storage.read_node(t, right_idx)

            if right.n >= t:
                # empresta do irmão direito
                self.delete_sibling(node_idx, first, right_pos)
            else:
                # merge: resultado fica na posição first (0)
                self.delete_merge(node_idx, first, right_pos)

                # após merge, o filho correto continua em first (0)
                node = self.storage.read_node(t, node_idx)
                child_idx = node.filhos[first]
                return self.delete_successor(child_idx)

            # após borrow, relê o pai por segurança
            node = self.storage.read_node(t, node_idx)
            child_idx = node.filhos[first]

        return self.delete_successor(child_idx)
    
    def delete_merge(self, parent_idx: int, i: int, j: int) -> int:
        """
        Realiza merge de dois irmãos adjacentes.

        Processo:
            - Desce a chave separadora do pai.
            - Concatena chaves e filhos do nó direito ao esquerdo.
            - Remove chave e ponteiro do pai.
            - Se o pai ficar vazio e for raiz, ajusta nova raiz.
        """
        t = self.t

        parent = self.storage.read_node(t, parent_idx)

        left_idx = parent.filhos[i]
        right_idx = parent.filhos[j]

        left = self.storage.read_node(t, left_idx)
        right = self.storage.read_node(t, right_idx)

        # desce a chave separadora do pai para o meio do left
        left.chaves.append(parent.chaves[i])
        left.registros.append(parent.registros[i])

        # concatena tudo do right
        left.chaves.extend(right.chaves)
        left.registros.extend(right.registros)

        if not left.folha:
            left.filhos.extend(right.filhos)

        # remove do pai a chave separadora e o ponteiro do filho direito
        parent.chaves.pop(i)
        parent.registros.pop(i)
        parent.filhos.pop(j)

        # escreve de volta
        self.storage.write_node(t, left)
        self.storage.write_node(t, parent)

        # se o pai era raiz e ficou vazio, nova raiz vira left
        if parent_idx == self.raiz_idx and len(parent.chaves) == 0:
            self.raiz_idx = left_idx
            self.storage.write_head(t, self.idx, self.raiz_idx)

        return left_idx

    def delete_sibling(self, parent_idx: int, i: int, j: int):
        """
        Redistribui chave entre irmãos (borrow).

        Caso j > i:
            empresta do irmão direito.
        Caso j < i:
            empresta do irmão esquerdo.

        Evita merge quando possível.
        """
        t = self.t

        parent = self.storage.read_node(t, parent_idx)

        c_idx = parent.filhos[i]
        s_idx = parent.filhos[j]

        cnode = self.storage.read_node(t, c_idx)
        sib = self.storage.read_node(t, s_idx)

        # irmão à direita
        if i < j:
            # desce a chave separadora do pai para o final de cnode
            cnode.chaves.append(parent.chaves[i])
            cnode.registros.append(parent.registros[i])

            # sobe a primeira chave do irmão direito para o pai
            parent.chaves[i] = sib.chaves.pop(0)
            parent.registros[i] = sib.registros.pop(0)

            # se não for folha, também move o primeiro filho do irmão para cnode
            if not cnode.folha:
                cnode.filhos.append(sib.filhos.pop(0))

        # irmão à esquerda
        else:
            # desce a chave separadora do pai para o início de cnode
            cnode.chaves.insert(0, parent.chaves[i - 1])
            cnode.registros.insert(0, parent.registros[i - 1])

            # sobe a última chave do irmão esquerdo para o pai
            parent.chaves[i - 1] = sib.chaves.pop()
            parent.registros[i - 1] = sib.registros.pop()

            # se não for folha, também move o último filho do irmão para cnode
            if not cnode.folha:
                cnode.filhos.insert(0, sib.filhos.pop())

        # persiste alterações
        self.storage.write_node(t, parent)
        self.storage.write_node(t, cnode)
        self.storage.write_node(t, sib)

    def get(self, chave):
        """
        Recupera o valor associado à chave.

        Retorna:
            valor se encontrado
            None caso contrário
        """
        res = self.search(chave)
        if res is None:
            return None
        node, i = res
        return node.registros[i]

    def print_tree_levels(self, root_idx: int):
        """
        Impressão por níveis (BFS).

        Utiliza fila (deque) para percorrer a árvore por largura,
        escrevendo cada nível em uma linha separada.
        """
        def _fmt_node(node) -> str:
            return "[" + ", ".join('key: ' + str(k) for k in node.chaves) + "]"

        t = self.t
        q = deque([(root_idx, 0)])

        current_level = 0
        line_parts = []

        while q:
            node_idx, level = q.popleft()
            node = self.storage.read_node(t, node_idx)

            # quando muda o nível, imprime a linha anterior
            if level != current_level:
                self.txt.write(" ".join(line_parts) + "\n")
                line_parts = []
                current_level = level

            line_parts.append(_fmt_node(node))

            if not node.folha:
                for child_idx in node.filhos:
                    q.append((child_idx, level + 1))

        # imprime a última linha acumulada
        if line_parts:
            self.txt.write(" ".join(line_parts))
