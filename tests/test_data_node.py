from unittest import TestCase

from json_converter.data_node import DataNode


class DataNodeTest(TestCase):

    def test___setitem__(self):
        # given:
        node = DataNode()

        # when:
        node['path.to.node'] = 'value'
        node['path.to.nested.field'] = 347

        # then:
        dict = node.as_dict()
        self.assertEqual('value', dict['path']['to']['node'])
        self.assertEqual(347, dict['path']['to']['nested']['field'])

    def test___getitem__(self):
        # given:
        defaults = {
            'first_name': 'Juan',
            'last_name': 'dela Cruz',
            'age': 39,
            'address': {
                'city': 'Manila',
                'country': 'Philippines'
            }
        }

        # and:
        data_node = DataNode(defaults=defaults)

        # expect:
        self.assertEqual('Juan', data_node['first_name'])
        self.assertEqual(39, data_node['age'])

        # and:
        self.assertEqual('Manila', data_node['address.city'])
        self.assertEqual('Philippines', data_node['address.country'])

    def test___getitem___non_existent_path(self):
        # given:
        defaults = {'product': {'name': 'biscuit', 'id': '123'}}
        data_node = DataNode(defaults=defaults)

        # expect:
        # TODO this should probably throw exception instead, indicating path does not exist
        self.assertIsNone(data_node['product.path.does.not.exist'])
        self.assertIsNone(data_node['simply.does.not.exist'])

    # TODO in the future, it might be worth being able to remove nested keys.
    #  For now, let's remove only high level keys
    def test_remove_field(self):
        # given:
        source = {'description': 'test source', 'count': 101, 'id': 'a3b7880'}
        data_node = DataNode(defaults=source)

        # when:
        data_node.remove_field('count')
        data_node.remove_field('description')

        # then:
        self.assertEqual(['id'], list(data_node.as_dict().keys()))

    def test_get(self):
        # given:
        data_node = DataNode({'content': {'text': 'this is a test'}, 'empty': ''})
        default_value = 'default'

        # expect:
        self.assertEqual(default_value, data_node.get('non.existent.field', default_value))
        self.assertEqual('this is a test', data_node.get('content.text', default_value))
        self.assertEqual('', data_node.get('empty'))
