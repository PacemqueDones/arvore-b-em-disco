import struct
from node import Node

class Storage:
    HEAD_FMT = "iii"  # t, next_idx, root_idx

    def __init__(self, path: str, create: bool):
        self.f = open(path, "w+b" if create else "r+b")

    def close(self):
        self.f.flush()
        self.f.close()

    def head_size(self):
        return struct.calcsize(self.HEAD_FMT)

    def write_head(self, d: int, next_idx: int, root_idx: int):
        self.f.seek(0)
        self.f.write(struct.pack(self.HEAD_FMT, d, next_idx, root_idx))

    def read_head(self):
        self.f.seek(0)
        data = self.f.read(self.head_size())
        return struct.unpack(self.HEAD_FMT, data)

    def node_offset(self, d: int, idx: int):
        return self.head_size() + idx * Node.byte_size(d)

    def read_node(self, d: int, idx: int):
        self.f.seek(self.node_offset(d, idx))
        data = self.f.read(Node.byte_size(d))
        return Node.from_bytes(d, data)

    def write_node(self, d: int, node):
        self.f.seek(self.node_offset(d, node.idx))
        self.f.write(node.to_bytes(d))
