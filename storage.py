import struct
from node import Node

class NodeStorage:
    HEADER_FMT = "iii"  # t, next_idx, root_idx

    def __init__(self, path: str, t: int, create: bool):
        self.path = path
        self.t = t
        self.f = open(path, "w+b" if create else "r+b")

        if create:
            self.next_idx = 1
            self.root_idx = 0
            self.write_head()
        else:
            self.read_head()

    def close(self):
        self.f.flush()
        self.f.close()

    def head_size(self):
        return struct.calcsize(self.HEADER_FMT)

    def write_head(self):
        self.f.seek(0)
        self.f.write(struct.pack(self.HEADER_FMT, self.t, self.next_idx, self.root_idx))

    def read_head(self):
        self.f.seek(0)
        data = self.f.read(self.head_size())
        self.t, self.next_idx, self.root_idx = struct.unpack(self.HEADER_FMT, data)

    def node_offset(self, idx: int) -> int:
        return self.head_size() + idx * Node.byte_size(self.t)

    def read_node(self, idx: int) -> Node:
        self.f.seek(self.node_offset(idx))
        data = self.f.read(Node.byte_size(self.t))
        return Node.from_bytes(self.t, data, idx=idx)

    def write_node(self, node: Node):
        self.f.seek(self.node_offset(node.idx))
        self.f.write(node.to_bytes(self.t))

    def alloc_node(self, folha: bool) -> Node:
        idx = self.next_idx
        self.next_idx += 1
        self.write_head()  # persistir next_idx

        node = Node(folha=folha, idx=idx)
        self.write_node(node)
        return node
