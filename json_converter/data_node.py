import copy

FIELD_SEPARATOR = '.'


class DataNode:

    def __init__(self, defaults={}):
        self.node = copy.deepcopy(defaults)

    def __setitem__(self, key, value):
        field_chain = key.split(FIELD_SEPARATOR)
        target_node = self._determine_node(field_chain)
        target_node[field_chain[-1]] = value

    def _determine_node(self, field_chain):
        current_node = self.node
        for field in field_chain[:len(field_chain) - 1]:
            if field not in current_node:
                current_node[field] = {}
            current_node = current_node[field]
        return current_node

    def __getitem__(self, key):
        field_chain = key.split(FIELD_SEPARATOR)
        current_node = self.node.get(field_chain[0])
        for field in field_chain[1:]:
            if current_node is None:
                break
            else:
                current_node = current_node.get(field)
        return current_node

    def get(self, key: str, default=None):
        value = self[key]
        return value if value is not None else default

    def remove_field(self, field):
        del self.node[field]

    def keys(self):
        return list(self.node.keys())

    def as_dict(self):
        return copy.deepcopy(self.node)
