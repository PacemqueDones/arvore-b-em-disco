import struct

class Node:
    def __init__(self, leaf: bool):
        self.leaf = leaf
        self.keys = []     # list[int]
        self.vals = []     # list[int]
        self.child = []    # list[Node]

    @property
    def n(self):
        return len(self.keys)
    
    def to_bytes(self, d: int) -> bytes:
        max_keys = d - 1
        max_child = d

        keys = self.keys + [-1] * (max_keys - self.n)
        vals = self.vals + [-1] * (max_keys - self.n)

        if self.leaf:
            child = [-1] * max_child
        else:
            child = self.child + [-1] * (max_child - len(self.child))

        fmt = f"?ii{max_keys}i{max_keys}i{max_child}i"
        return struct.pack(fmt, self.leaf, self.n, self.idx, *keys, *vals, *child)

    @classmethod
    def from_bytes(cls, d: int, data: bytes):
        max_keys = d - 1
        max_child = d
        fmt = f"?ii{max_keys}i{max_keys}i{max_child}i"

        descompactado = struct.unpack(fmt, data)

        leaf = descompactado[0]
        n = descompactado[1]
        idx = descompactado[2]

        start_keys = 3
        end_keys = start_keys + max_keys
        vals_end = end_keys + max_keys
        end_child = vals_end + max_child

        keys = list(descompactado[start_keys:end_keys])[:n]
        vals = list(descompactado[end_keys:vals_end])[:n]
        raw_child = list(descompactado[vals_end:end_child])

        node = cls(leaf=leaf, idx=idx)
        node.keys = keys
        node.vals = vals
        node.child = [] if leaf else raw_child[:n + 1]

        return node

    @classmethod
    def byte_size(cls, d: int) -> int:
        max_keys = d - 1
        max_child = d
        fmt = f"?ii{max_keys}i{max_keys}i{max_child}i"
        return struct.calcsize(fmt)