import unittest

from json_converter.json_mapper import JsonMapper


class TestMappingArrays(unittest.TestCase):
    def test_source_array_on(self):
        expected_json = {
            "authors": ["Stephenson E", "Niel Tyson"]
        }
        json_object = {
            "publications": [
                {
                  "author": "Stephenson E"
                },
                {
                    "author": "Niel Tyson"
                }
            ]
        }
        test_spec = {
            "$on": "publications",
            "authors": ["$array", ["author"], True]
        }
        authors_json = JsonMapper(json_object).map(test_spec)
        self.assertDictEqual(expected_json, authors_json)

    def test_source_array(self):
        expected_json = {
            "authors": ["Stephenson E", "Niel Tyson"]
        }
        json_object = {
            "publications": [
                {
                  "author": "Stephenson E"
                },
                {
                    "author": "Niel Tyson"
                }
            ]
        }
        test_spec = {
            "authors": ["$array", ["publications.author"], True]
        }
        authors_json = JsonMapper(json_object).map(test_spec)
        self.assertDictEqual(expected_json, authors_json)

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
                    "name": ['$object', 'Authors'],
                    "value": ['publication.authors']
                },
                {
                    "name": ['$object', 'Title'],
                    "value": ['publication.title']
                }
            ], True]
        }
        publication_json = JsonMapper(json_object).map(test_spec)
        self.assertDictEqual(expected_json, publication_json)

    def test_both_source_and_spec_are_array(self):
        expected_json = [
            {
                "type": "Publications",
                "attributes": [
                    {
                        "name": "Author",
                        "value": "Li R"
                    },
                    {
                        "name": "Title",
                        "value": "Pdgfra marks a cellular lineage with distinct contributions to myofibroblasts in lung maturation and injury response."
                    }
                ]
            },
            {
                "type": "Publications",
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
            "attributes": ["$array", [
                {
                    "name": ['$object', 'Authors'],
                    "value": ['publications.authors']
                },
                {
                    "name": ['$object', 'Title'],
                    "value": ['publications.title']
                }
            ], True]
        }
        publications_json = JsonMapper(json_object).map(test_spec)
        self.assertListEqual(expected_json, publications_json)

    def test_both_source_and_spec_are_array_and_source_contains_arrays(self):
        expected_json = [
            {
                "type": "Publications",
                "attributes": [
                    {
                        "name": "Authors",
                        "value": ["Li R", "Bernau K"]
                    },
                    {
                        "name": "Title",
                        "value": "Single marks a cellular lineage with distinct contributions to myofibroblasts in lung maturation and injury response."
                    }
                ]
            },
            {
                "type": "Publications",
                "attributes": [
                    {
                        "name": "Authors",
                        "value": ["Stephenson E", "Sandbo N"]
                    },
                    {
                        "name": "Title",
                        "value": "Pdgfra marks a cellular lineage with distinct contributions to myofibroblasts in lung maturation and injury response."
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
                    "author": ["Stephenson E", "Sandbo N"],
                    "title": "Single-cell multi-omics analysis of the immune response in COVID-19",
                    "doi": "10.1038/s41591-021-01329-2",
                    "url": "https://www.nature.com/articles/s41591-021-01329-2#Sec8"
                }
            ]
        }
        test_spec = ['$array', [
            {
                'type': ['$object', 'Publications'],
                "attributes": ["$array", [
                    {
                        "name": ['$object', 'Authors'],
                        "value": ['$array', ['publications.authors'], True]
                    },
                    {
                        "name": ['$object', 'Title'],
                        "value": ['publications.title']
                    }
                ], True]
            }, True]
        ]
        publications_json = JsonMapper(json_object).map(test_spec)
        self.assertListEqual(expected_json, publications_json)


if __name__ == '__main__':
    unittest.main()
