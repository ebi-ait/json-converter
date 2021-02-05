import json
from string import Template
from unittest import TestCase

from json_converter.json_mapper import JsonMapper, InvalidNode, UnreadableSpecification


class JsonMapperTest(TestCase):

    def test_map_object(self):
        # given:
        json_object = json.loads('''{
            "user_name": "jdelacruz",
            "user_age": 31
        }''')

        # when:
        converted_json = JsonMapper(json_object).map({
            'name': ['user_name'],
            'age': ['user_age']
        })

        # then:
        self.assertIsNotNone(converted_json)
        self.assertEqual('jdelacruz', converted_json['name'])
        self.assertEqual(31, converted_json['age'])

    def test_map_object_using_field_chaining(self):
        # given:
        json_object = json.loads('''{
            "name": "John Doe",
            "address": {
                "city": "London",
                "country": "UK"
            }
        }''')

        # when:
        profile_json = JsonMapper(json_object).map({
            'user.profile': ['name'],
            'user.address_city': ['address.city'],
            'user.address_country': ['address.country']
        })

        # then:
        self.assertIsNotNone(profile_json)
        self.assertEqual('John Doe', profile_json.get('user', {}).get('profile'))
        self.assertEqual('London', profile_json.get('user', {}).get('address_city'))
        self.assertEqual('UK', profile_json.get('user', {}).get('address_country'))

    def test_map_object_with_anchored_key(self):
        # given:
        json_object = json.loads('''{
            "user": {
                "name": "Jane Doe"
            },
            "address": {
                "city": "Cambridge",
                "country": "UK"
            }
        }''')

        # when:
        address_json = JsonMapper(json_object).map(
            on='address',
            using={
                'address_city': ['city'],
                'address_country': ['country']
            })

        # then:
        self.assertIsNotNone(address_json)
        self.assertEqual('Cambridge', address_json['address_city'])
        self.assertEqual('UK', address_json['address_country'])

    def test_map_object_using_spec_based_anchor(self):
        # given:
        json_object = json.loads('''{
            "shipping_info": {
                "recipient": "Kamado Tanjiro",
                "address": "Tokyo, Japan"
            }
        }''')

        # when:
        delivery_json = JsonMapper(json_object).map({
            '$on': 'shipping_info',
            'name': ['recipient'],
            'location': ['address']
        })

        # then:
        self.assertEqual('Kamado Tanjiro', delivery_json.get('name'))
        self.assertEqual('Tokyo, Japan', delivery_json.get('location'))

    def test_map_object_using_chained_spec_based_anchors(self):
        # given:
        json_object = json.loads('''{
            "user": {
                "profile": {
                    "name": "Kamado Nezuko",
                    "location": "hako no naka"
                }
            }
        }''')

        # when:
        person_json = JsonMapper(json_object).map({
            '$on': 'user',
            'person': {
                '$on': 'profile',
                'known_by': ['name']
            }
        })

        # then:
        self.assertEqual('Kamado Nezuko', person_json.get('person', {}).get('known_by'))

    def test_map_object_with_non_node_anchor(self):
        # given:
        json_object = json.loads('''{
            "name": "Boaty McBoatface"
        }''')
        mapper = JsonMapper(json_object)

        # expect:
        with self.assertRaises(InvalidNode):
            mapper.map({
                'known_as': ['name']
            }, on='name')

    def test_map_object_with_non_existent_anchor(self):
        # given:
        json_object = json.loads('''{
            "description": "test"
        }''')
        mapper = JsonMapper(json_object)

        # when:
        flat_result = mapper.map({
            '$on': 'non.existent.node',
            'name': ['text']
        })

        # and:
        nested_result = mapper.map({
            'text': ['description'],
            'optional': {
                '$on': 'non.existent.node',
                'field': ['field']
            }
        })

        # then:
        self.assertIsNone(flat_result)
        self.assertEqual({'text': 'test'}, nested_result)

    def test_map_object_with_custom_processing(self):
        # given:
        json_object = json.loads('''{
            "name": "Pedro,Catapang,de Guzman",
            "age": 44
        }''')

        # and:
        def parse_name(*args):
            name = args[0]
            index = args[1]
            return name.split(',')[index]

        # and:
        def fake_age(*args):
            age = args[0]
            return age - 10

        # when:
        resulting_json = JsonMapper(json_object).map({
            'first_name': ['name', parse_name, 0],
            'middle_name': ['name', parse_name, 1],
            'last_name': ['name', parse_name, 2],
            'fake_age': ['age', fake_age]
        })

        # then:
        self.assertEqual('Pedro', resulting_json['first_name'])
        self.assertEqual('Catapang', resulting_json['middle_name'])
        self.assertEqual('de Guzman', resulting_json['last_name'])
        self.assertEqual(34, resulting_json['fake_age'])

    def test_map_object_with_nested_spec(self):
        # given:
        json_object = json.loads('''{
            "first_name": "Vanessa",
            "last_name": "Doofenshmirtz"
        }''')

        # when:
        profile_json = JsonMapper(json_object).map({
            'profile': {
                'first_name': ['first_name'],
                'last_name': ['last_name']
            }
        })

        # then:
        profile = profile_json.get('profile')
        self.assertIsNotNone(profile)
        self.assertEqual('Vanessa', profile.get('first_name'))
        self.assertEqual('Doofenshmirtz', profile.get('last_name'))

    def test_map_list_of_objects(self):
        # given:
        json_object = json.loads('''{
            "contacts": [
                {
                    "name": "James",
                    "phone": "55556161"
                },
                {
                    "name": "Ana",
                    "phone": "55510103"
                }
            ]
        }''')

        # when:
        people = JsonMapper(json_object).map(on='contacts', using={
            'known_by': ['name']
        })

        # then:
        self.assertEqual(2, len(people))
        names = [person.get('known_by') for person in people]
        self.assertTrue('Ana' in names)
        self.assertTrue('James' in names)

    def test_map_list_of_objects_with_nested_anchoring(self):
        # given:
        json_object = json.loads('''{
            "social_network": {
                "friends": [
                    {
                        "name": "Carl",
                        "age": 24
                    },
                    {
                        "name": "Tina",
                        "age": 22
                    },
                    {
                        "name": "Oscar",
                        "age": 22
                    }
                ]
            }
        }''')

        # when:
        people_json = JsonMapper(json_object).map({
            '$on': 'social_network',
            'people': {
                '$on': 'friends',
                'person_name': ['name'],
                'person_age': ['age']
            }
        })

        # then:
        people = people_json.get('people')
        self.assertIsNotNone(people)
        self.assertEqual(3, len(people))

    # TODO consider required field mode
    def test_map_object_ignore_missing_fields(self):
        # given:
        json_object = json.loads('''{
            "first_name": "Juan",
            "last_name": "dela Cruz"
        }''')

        # when:
        person_json = JsonMapper(json_object).map({
            'fname': ['first_name'],
            'mname': ['middle_name'],
            'lname': ['last_name']
        })

        # then:
        self.assertEqual('Juan', person_json.get('fname'))
        self.assertEqual('dela Cruz', person_json.get('lname'))
        self.assertTrue('mname' not in person_json)

    def test_map_object_allow_empty_strings(self):
        # given:
        json_object = json.loads('''{
            "pet_name": "Champ",
            "favourite_food": ""
        }''')

        # when:
        pet_json = JsonMapper(json_object).map({
            'name': ['pet_name'],
            'fav_food': ['favourite_food']
        })

        # then:
        self.assertEqual('Champ', pet_json.get('name'))
        self.assertEqual('', pet_json.get('fav_food'))

    def test_map_object_with_invalid_spec(self):
        # given:
        json_object = json.loads('''{
            "description": "this is a test"
        }''')

        # expect: main spec
        with self.assertRaises(UnreadableSpecification):
            JsonMapper(json_object).map('spec')

        # and: field spec
        with self.assertRaises(UnreadableSpecification):
            JsonMapper(json_object).map({'d': 'specification'})

        # and: empty dict as spec
        with self.assertRaises(UnreadableSpecification):
            JsonMapper(json_object).map({})

        # and: empty field specification
        with self.assertRaises(UnreadableSpecification):
            JsonMapper(json_object).map({'field': []})

        # and: None field specification
        with self.assertRaises(UnreadableSpecification):
            JsonMapper(json_object).map({'field': None})

    def test_map_object_with_filter(self):
        # given:
        json_template = Template('''{
            "name": "$name",
            "age": $age
        }''')

        # and:
        filtered_out_json = json.loads(json_template.substitute({'name': 'Charlie', 'age': 10}))
        passing_json = json.loads(json_template.substitute({'name': 'Mary', 'age': 27}))

        # and:
        def is_adult(*args):
            age = args[0]
            return age >= 18

        # and:
        filtered_spec = {
            '$filter': ['age', is_adult],
            'known_by': ['name']
        }

        # when:
        under_age_result = JsonMapper(filtered_out_json).map(filtered_spec)
        adult_result = JsonMapper(passing_json).map(filtered_spec)

        # then:
        self.assertEqual({}, under_age_result)
        self.assertEqual({'known_by': 'Mary'}, adult_result)

    def test_map_object_list_with_filter(self):
        # given:
        json_object = json.loads('''{
            "product_list": [
                {
                    "name": "eggs",
                    "price": 1.25
                },
                {
                    "name": "milk",
                    "price": 0.50
                },
                {
                    "name": "loaf",
                    "price": 2.25
                }
            ]
        }''')

        # and:
        def price_filter(*args):
            price = args[0]
            return price >= 1

        # when:
        products = JsonMapper(json_object).map({
            '$on': 'product_list',
            '$filter': ['price', price_filter],
            'item': ['name']
        })

        # then:
        self.assertEqual(2, len(products))
        item_names = [item.get('item') for item in products]
        self.assertTrue('eggs' in item_names and 'loaf' in item_names)

    def test_map_with_object_literal(self):
        # given:
        json_object = json.loads('''{
            "description": "test"
        }''')

        # when:
        metadata = {'authored_by': 'me'}
        result = JsonMapper(json_object).map({
            'text': ['description'],
            'metadata': ['$object', metadata],
            'empty': ['$object', {}]
        })

        # then:
        self.assertEqual(metadata, result.get('metadata'))
        self.assertFalse('empty' in result.keys())

    def test_map_with_invalid_object_literal(self):
        # given:
        json_mapper = JsonMapper({})

        # expect: non dict as object literal
        with self.assertRaises(UnreadableSpecification):
            json_mapper.map({
                'field': ['$object', 'testing!']
            })

        # and: no specified literal
        with self.assertRaises(UnreadableSpecification):
            json_mapper.map({
                'field': ['$object']
            })

    def test_map_with_array_literal(self):
        # given:
        json_mapper = JsonMapper({})

        # when:
        values = ['list', 'of', 'values']
        result = json_mapper.map({
            'metadata': ['$array', values],
            'empty': ['$array', []]
        })

        # then:
        self.assertEqual(values, result.get('metadata'))
        self.assertFalse('empty' in result.keys())
