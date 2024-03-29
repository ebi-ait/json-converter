import unittest

from json_converter.json_mapper import JsonMapper
from json_converter.post_process import default_to


def array_to_string(*args):
    value = ", ".join(args[0])
    return value


class TestMappingArrays(unittest.TestCase):
    def test_spec_array(self):
        expected_json = {
            "attributes": [
                {
                    "name": "Authors",
                    "value": "Stephenson E"
                },
                {
                    "name": "Title",
                    "value": "Single-cell multi-omics analysis of the immune response in COVID-19"
                }
            ]
        }
        json_object = {
            "publication": {
                "authors": "Stephenson E",
                "title": "Single-cell multi-omics analysis of the immune response in COVID-19"
            }
        }
        test_spec = {
            "attributes": ["$array", [
                {
                    "name": ['', default_to, 'Authors'],
                    "value": ['publication.authors']
                },
                {
                    "name": ['', default_to, 'Title'],
                    "value": ['publication.title']
                }
            ], True]
        }
        publication_json = JsonMapper(json_object).map(test_spec)
        self.assertDictEqual(expected_json, publication_json)

    def test_both_source_and_spec_are_array(self):
        expected_json = [
            {
                "type": "Publication",
                "attributes": [
                    {
                        "name": "Author",
                        "value": "Li R"
                    },
                    {
                        "name": "Title",
                        "value": "Pdgfra marks a cellular lineage with distinct contributions to myofi"
                                 "broblasts in lung maturation and injury response."
                    }
                ]
            },
            {
                "type": "Publication",
                "attributes": [
                    {
                        "name": "Author",
                        "value": "Stephenson E"
                    },
                    {
                        "name": "Title",
                        "value": "Single-cell multi-omics analysis of the immune response in COVID-19"
                    }
                ]
            }
        ]
        json_object = {
            "publications": [
                {
                    "author": "Li R",
                    "title": "Pdgfra marks a cellular lineage with distinct contributions to myofibroblasts in lung maturation and injury response.",
                    "doi": "10.7554/eLife.36865",
                    "pmid": 30178747
                },
                {
                  "author": "Stephenson E",
                  "title": "Single-cell multi-omics analysis of the immune response in COVID-19",
                  "doi": "10.1038/s41591-021-01329-2",
                  "url": "https://www.nature.com/articles/s41591-021-01329-2#Sec8"
                }
            ]
        }
        test_spec = {
            "$on": "publications",
            "type": ['', default_to, "Publication"],
            "attributes": ["$array", [
                {
                    "name": ['', default_to, 'Author'],
                    "value": ['author']
                },
                {
                    "name": ['', default_to, 'Title'],
                    "value": ['title']
                }
            ], True]
        }

        publications_json = JsonMapper(json_object).map(test_spec)
        self.assertEqual(expected_json, publications_json)

    def test_spec_array_with_inner_on_keyword(self):
        input_json = {
            "paper": [
                {
                    "book_title": "Axioms End",
                    "book_author": "Lindsay Ellis"
                },
                {
                    "book_title": "The Starless Sea",
                    "book_author": "Erin Morgenstern"
                }
            ],
            "cd": [
                {
                    "cd_name": "Yes Man",
                    "artist": "Danny Wallace"
                }
            ]
        }
        spec = {
            "book": ["$array", {'$on': 'paper', 'title': ['book_title']}, True],
            "audio": ["$array", {'$on': 'cd', 'title': ['cd_name']}, True]
        }
        expected = {
            "book": [
                {'title': "Axioms End"},
                {'title': "The Starless Sea"}
            ],
            "audio": [{'title': "Yes Man"}]
        }
        result = JsonMapper(input_json).map(spec)
        self.assertDictEqual(expected, result)

    def test_both_source_and_spec_are_array_and_source_contains_arrays(self):
        expected_json = [
            {
                "type": "Publication",
                "attributes": [
                    {
                        "name": "Authors",
                        "value": ["Li R", "Bernau K"]
                    },
                    {
                        "name": "Title",
                        "value": "Pdgfra marks a cellular lineage with distinct contributions to myofibroblasts in lung maturation and injury response."
                    }
                ]
            },
            {
                "type": "Publication",
                "attributes": [
                    {
                        "name": "Authors",
                        "value": ["Stephenson E", "Sandbo N"]
                    },
                    {
                        "name": "Title",
                        "value": "Single-cell multi-omics analysis of the immune response in COVID-19"
                    }
                ]
            }
        ]
        json_object = {
            "publications": [
                {
                    "authors": ["Li R", "Bernau K"],
                    "title": "Pdgfra marks a cellular lineage with distinct contributions to myofibroblasts in lung maturation and injury response.",
                    "doi": "10.7554/eLife.36865",
                    "pmid": 30178747
                },
                {
                    "authors": ["Stephenson E", "Sandbo N"],
                    "title": "Single-cell multi-omics analysis of the immune response in COVID-19",
                    "doi": "10.1038/s41591-021-01329-2",
                    "url": "https://www.nature.com/articles/s41591-021-01329-2#Sec8"
                }
            ]
        }
        test_spec = {
            "$on": "publications",
            "type": ['', default_to, "Publication"],
            "attributes": ["$array", [
                {
                    "name": ['', default_to, 'Authors'],
                    "value": ['authors']
                },
                {
                    "name": ['', default_to, 'Title'],
                    "value": ['title']
                }
            ], True]
        }

        publications_json = JsonMapper(json_object).map(test_spec)
        self.assertEqual(expected_json, publications_json)

    def test_both_source_and_spec_are_array_and_source_contains_arrays_but_target_not(self):
        expected_json = [
            {
                "type": "Publication",
                "attributes": [
                    {
                        "name": "Authors",
                        "value": "Li R, Bernau K"
                    },
                    {
                        "name": "Title",
                        "value": "Pdgfra marks a cellular lineage with distinct contributions to myofibroblasts in lung maturation and injury response."
                    }
                ]
            },
            {
                "type": "Publication",
                "attributes": [
                    {
                        "name": "Authors",
                        "value": "Stephenson E, Sandbo N"
                    },
                    {
                        "name": "Title",
                        "value": "Single-cell multi-omics analysis of the immune response in COVID-19"
                    }
                ]
            }
        ]
        json_object = {
            "publications": [
                {
                    "authors": ["Li R", "Bernau K"],
                    "title": "Pdgfra marks a cellular lineage with distinct contributions to myofibroblasts in lung maturation and injury response.",
                    "doi": "10.7554/eLife.36865",
                    "pmid": 30178747
                },
                {
                    "authors": ["Stephenson E", "Sandbo N"],
                    "title": "Single-cell multi-omics analysis of the immune response in COVID-19",
                    "doi": "10.1038/s41591-021-01329-2",
                    "url": "https://www.nature.com/articles/s41591-021-01329-2#Sec8"
                }
            ]
        }
        test_spec = {
            "$on": "publications",
            "type": ['', default_to, "Publication"],
            "attributes": ["$array", [
                {
                    "name": ['', default_to, 'Authors'],
                    "value": ['authors', array_to_string]
                },
                {
                    "name": ['', default_to, 'Title'],
                    "value": ['title']
                }
            ], True]
        }

        publications_json = JsonMapper(json_object).map(test_spec)
        self.assertEqual(expected_json, publications_json)


if __name__ == '__main__':
    unittest.main()
