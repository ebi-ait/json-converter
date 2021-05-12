import copy
from collections import Mapping

from .data_node import DataNode

KEYWORD_MARKER = '$'

SPEC_ANCHOR = '$on'
SPEC_FILTER = '$filter'

SPEC_OBJECT_LITERAL = '$object'
SPEC_ARRAY_LITERAL = '$array'


def json_object(value: dict):
    return [SPEC_OBJECT_LITERAL, value]


def json_array(*values):
    return [SPEC_ARRAY_LITERAL, list(values)]


class JsonMapper:

    def __init__(self, source: dict):
        self.root_node = DataNode(source)

    def map(self, using={}, on='', node=None, is_output_array=False):
        spec = using
        orig_spec = copy.deepcopy(using)
        self._check_if_readable(spec)
        anchor = self._determine_anchor(on, spec)

        if not is_output_array:
            node = self.root_node if not anchor else self._anchor_node(anchor)

        if node is None:
            return node

        if isinstance(node, list):
            result = []
            for item in node:
                mapping = self._apply_node_spec(item, anchor, spec)
                if len(mapping) > 0:
                    result.append(mapping)
                spec = copy.deepcopy(orig_spec)
        else:
            result = self._apply_node_spec(node, anchor, spec)

        if is_output_array:
            return result[0] if isinstance(result, list) else result

        return result

    @staticmethod
    def _check_if_readable(spec):
        if not (isinstance(spec, (list, dict)) and len(spec) > 0):
            raise UnreadableSpecification

    @staticmethod
    def _determine_anchor(field, spec):
        anchor = field
        if SPEC_ANCHOR in spec:
            anchor = f'{anchor}.{spec[SPEC_ANCHOR]}' if anchor else spec[SPEC_ANCHOR]
        return anchor

    def _anchor_node(self, field):
        if field:
            anchored_node = self.root_node.get(field, None)
            # check if anchored_node is dict-like
            if anchored_node is None:
                return anchored_node

            if isinstance(anchored_node, Mapping):
                return DataNode(anchored_node)

            # or if anchored_node is actually a list
            if isinstance(anchored_node, list):
                return [DataNode(node) for node in anchored_node]

            raise InvalidNode(field)

    def _apply_node_spec(self, node: DataNode, anchor: str, spec: dict):
        filter_spec = spec.get(SPEC_FILTER)
        if not self._passes(filter_spec, node):
            return {}
        result = DataNode()
        for field_name, field_spec in spec.items():
            # skip reserved field
            if not field_name.startswith(KEYWORD_MARKER):
                self._check_if_readable(field_spec)
                field_value = None
                if isinstance(field_spec, list):
                    field_value = self._apply_field_spec(node, field_spec)
                elif isinstance(field_spec, dict):
                    field_value = self.map(using=field_spec, on=anchor)
                if field_value is not None:
                    result[field_name] = field_value
        return result.as_dict()

    @staticmethod
    def _passes(filter_spec: list, node: DataNode):
        if filter_spec is None:
            return True
        filter_field = filter_spec[0]
        value = node.get(filter_field)
        passing = True
        if value is not None:
            filter_args = [value]
            filter_args.extend(filter_spec[2:])
            do_filter = filter_spec[1]
            passing = bool(do_filter(*filter_args))
        return passing

    def _apply_field_spec(self, node: DataNode, spec: list):
        source_field_name = spec[0]
        if source_field_name == SPEC_OBJECT_LITERAL:
            field_value = self._get_object_or_array_literal(spec)
        elif source_field_name == SPEC_ARRAY_LITERAL:
            field_value = self._get_object_or_array_literal(spec, node, True)
        else:
            field_value = node.get(source_field_name)
            has_customisation = len(spec) > 1
            if has_customisation:
                operation = spec[1]
                args = [field_value]
                args.extend(spec[2:])
                field_value = operation(*args)
        return field_value

    def _get_object_or_array_literal(self, spec, node=None, is_output_array=False):
        field_value = self.__get_field_value(spec)

        contains_spec = spec[2] if len(spec) == 3 else False

        if len(field_value) == 0:
            field_value = None

        if contains_spec and isinstance(field_value, list):
            for i, item in enumerate(field_value):
                if node is not None:
                    field_value[i] = self.map(item, '', node, is_output_array)
                else:
                    field_value[i] = self.map(item)

        if contains_spec and isinstance(field_value, Mapping):
            field_value = self.map(field_value)

        return field_value

    @staticmethod
    def __get_field_value(spec):
        if len(spec) < 2 or len(spec) > 3:
            raise UnreadableSpecification(f'The {spec[0]} spec can  either have 1 or 2 parameters.')

        field_value = spec[1]

        if not isinstance(field_value, (Mapping, list)):
            raise UnreadableSpecification('JSON literal should be a dict-like or list structure.')

        return field_value


class InvalidNode(Exception):

    def __init__(self, field):
        super().__init__(f'Invalid node [{field}].')
        self.field = field


class UnreadableSpecification(Exception):

    def __init__(self, details=''):
        super().__init__(f'Provided specification is unreadable. {details}')
