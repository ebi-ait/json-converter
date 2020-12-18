# JSON Mapping

The `JsonMapper` class is a tool for translating/converting a JSON document into another JSON document with a 
different structure. The mapping process follows a dictionary-based specification of how fields map to the new 
JSON format. The main function in the `JsonMapper` is `map` that takes a structured specification:

        JsonMapper(json_document).map(specification)


## Mapping Specification

The general idea is that the specification describes the resulting structure of the converted JSON document. The
dictionary-based specification will closely resemble the schema of the resulting JSON.

### Field Specification

A field specification is defined by a list of parameters, the first of which is a name that refers to a field in 
the current JSON to be converted. This is the only required field.

        <converted_field>: [<original_field>]

For example, given the sample JSON document,

        {
            "person_name": "Juan dela Cruz"
            "person_age": 37 
        }

the simplest mapping that can be done is to translate to a different field name. For example, to map 
`person_name` to `name` in the resulting JSON, the following specification is used:

        {
            'name': ['person_name']
        }

#### Field Chaining

JSON mapping also supports chaining of fields on either or both side of the specification. For example, using the
following specification to the JSON above,

        {
            'person.name': ['person_name'],
            'person.age': ['person_age']
        }
 
 will result in the conversion:
 
        {
            "person": {
                "name": "Juan dela Cruz",
                "age": 37
            }
        }
        
 To convert back to the original JSON in the example, just reverse the field specification, for example, 
`'person_name': ['person.name']`. Field chaining can be done on multiple levels. However, at the time of writing, 
`JsonMapper` does not support direct field chaining for JSON array types. Processing such fields can be expressed 
through [anchoring](#anchoring) and [nesting](#nested-specification).
 
#### Post-Processing Using Generic Functions

The JSON mapper allows post processing of field values for more complex translation rules. This is done by 
specifying a generic Python function that takes an arbitrary list of arguments (`*args`). The post-processing 
function is specified after the original field name in the field specification:

        <converted_field>: [<original_field>, <post_processor>{, <args>}*]
        
`JsonMapper` will pass the value of the specified field as the first argument to the post-processor. Taking the 
same example in the previous section, a boolean field `adult` can be added using this feature. The following spec
demonstrates how this can be done:
            
        {
            'name': ['person_name'],
            'age': ['person_age'],
            'adult': ['person_age', is_adult]
        }
        
with the post-processor defined as:

        def is_adult(*args):
            age = args[0]
            return age >= 18
            
At the time of writing, there are a few built-in post-processors that can be applied to some common use-cases like
defaulting values (`default_to`), concatenating lists (`concatenate_list`), etc. These can be found in 
`post_process.py` module.

### Anchoring

While the `JsonMapper` has support for field chaining, for complex JSON with several levels of nesting, 
combined with long field names and field list, repetitively providing full field chain can be tedious. To be able
to express this more concisely, anchoring can be used. Anchoring specifies the root of the JSON structure to 
map to a new JSON format, relative to the actual root of the original JSON document.

#### The `on` Parameter

The `map` function in the `JsonMapper` takes a parameter named `on` that can be used to specify the root of the
JSON on which to start mapping. For example, given the following JSON,

        {
            "user": {
                "settings": {
                    "basic": {...},
                    "advanced": {
                        "security": {
                            "javascript_enabled": true,
                            "allow_trackers": false
                        }
                    }
                }
            }
        }
 
 the processing can be anchored on `user.settings.advanced.security` to translate the security settings. The
 following specification,
  
        {
            'javascript': ['javascript_enabled'],
            'trackers': ['allow_trackers']
        }

applied to the JSON above using `map(specification, on='user.settings.advanced.security')`, will result in,

        {
            "javascript": true,
            "trackers": false
        }

Without the anchor, it's necessary to always include `user.settings.advanced.security` in the field specification,
so the `javascript` mapping would look like `'javascript': ['user.settings.advanced.security.javascript_enabled']`.

#### The `$on` Specification

Another way of specifying the anchoring field is by directly adding it to the specification using the `$on`
keyword. Unlike field specifications, the `$on` keyword takes a plain string and *not* a list/vector. For 
example, the previous sample specification can be alternatively expressed as,

        {
            '$on': 'user.settings.advanced.security',
            "javascript": ['javascript_enabled'],
            "trackers": ['allow_trackers']
        } 

Using this specification, the mapping can be invoked without the `on` parameter. Keywords in specifications are, 
at the time of writing, case-sensitive, so `$On`, `$ON`, etc. are *not* recognised.

#### Chaining `on` and `$on`

The `on` parameter and the `$on` keyword do **not** override, but instead are chained together. The existence
of both during a mapping call results in the `$on` field chain being concatenated to the value provided in 
through the `on` parameter. For example, the following invocation is equivalent to the previous two above:

        map({
            '$on': 'advanced.security',
            "javascript": true,
            "trackers": false
        }, on='user.settings')
        
The `user.settings` field supplied through `on` parameter will be treated as a prefix to the `advanced.security`
field specified through the `$on` keyword.
        
### Nested Specification

Aside from field specifications, nested dictionary-like specification can be provided to any recognised fields in
the root specification. Nesting is useful for expressing nesting on single objects, or for applying conversion
to a list of JSON objects defined in an array.

#### Single Object Nesting

For single objects, nested specs can be defined to look like the resulting JSON object. Nesting specification this
way is a more expressive alternative to [field chaining that was demonstrated above](#field-chaining). For example, 
the following JSON, similar to the previous sections,

        {
            "person_name": "Jane Eyre",
            "person_age": 30
        }
        
can be mapped using nested specification defined with a nested `person` object:

        {
            'person': {
                'name': ['person_name'],
                'age': ['person_age']
            }
        }

[Anchoring](#anchoring) in nested specifications is also supported. However, unlike anchors in the main specification
that can be expressed through the `on` parameter, nested anchors can only be specified using the `$on` keyword. It is 
also important to note that nested anchors are defined relative to the parent specification. For example, the following
JSON,

        {
            "product_info" {
                "manufacturing": {
                    "location": "Cambridge, UK", 
                    "manufacturing_date": "2020-03-05",
                    "best_by_date": "2020-09-05"
                }
            }
        }

can be mapped using the following nested specification,

        {
            '$on': 'product_info',
            'production': {
                '$on': 'manufacturing',
                'date': ['manufacturing_date']
            }
        }

This mapping will result in the following JSON:

        {
            "production": {
                "date": "2020-03-05"
            }
        }

### Applying Specification to JSON Arrays

The JSON mapping utility can distinguish between JSON object nodes and JSON array, and applies specification 
accordingly. When it determines that a field referred to by the specification is a collection of JSON objects, it
applies the rules to each one of them iteratively. Note, however, that, as earlier mentioned in this document, using 
field chaining to refer to nested JSON array is *not* supported at this time. To apply specifications to JSON arrays, 
they need to be explicitly [anchored](#anchoring) if they are nested within the original JSON document.

To illustrate, the following JSON object,

        {
            "books": [
                {
                    "title": "A Python Book",
                    "price": 23.75
                },
                {
                    "title": "A Novel",
                    "price": 7.99
                },
                {
                    "title": "Compilation of Fun Stuff",
                    "price": 10.10
                }
            ]
        }
        
can be translated using the following specification (assume `translate` and `convert` are defined; see 
[post-processing](#post-processing-using-generic-functions) for more information on this),

        {
            '$on': 'books',
            'titulo': ['title', translate, 'es'],
            'precio': ['price', convert, 'eur']
        }
        
Notice that, since the specification is anchored to the `books` node, only the list of field specifications are 
defined. Specifications applied to multiple objects this way are expressed as if it applies to a single object. This 
sample translation will return an array of JSON objects and *not* a JSON object containing an array. If a nested array 
is desired, the specification above can be nested instead:

        {
            'libros': {
                '$on': 'books',
                'titulo': ['title', translate, 'es'],
                'precio': ['price', convert, 'eur']
            }
        }

#### Filtering

When working on collections of data, it is sometimes required to only process some based on some criteria. For 
`JsonMapper`, this is done by using filtering in the specification. Filters take the form of a field specification
with the second argument being a boolean function, also called a predicate.

        '$filter': [<original_field>, <predicate_function>{, args}*]
        
Just like in generic functions for [post-processing](#post-processing-using-generic-functions), `JsonMapper` will pass
the value of found in the `original_field` as the first parameter along with the rest of `args` if they exist.

For example, to process only books whose prices are above 10.00 from the sample books JSON above, the following spec 
can be used:

        {
            'expensive_books': {
                '$on': 'books',
                '$filter': ['price', greater_than, 10],
                'book_title': ['title'],
                'book_price': ['price']
            }
        }
        
with the predicate `greater_than` defined as,

        def greater_than(*args):
            number = args[0]
            other_number = args[1]
            return number > other_number

While filtering can be applied to single JSON nodes, the application can be limited. Any JSON object filtered out, will
appear as an empty JSON object in the resulting document.

### JSON Literals

There are situations when the resulting JSON need to contain fields and values outside the scope of the source JSON
document. In such cases, it's possible to define a post-processor that plugs-in a pre-defined dictionary-like or list
structure. However, `JsonMapper` also provides support for including literals in the specification.

#### Using Keywords

As mentioned above, there are 2 types of node that can be used for adding predefined values into the specification, 
which are object, and array. To specify a JSON object literal as field value in the resulting JSON document, the
`$json_object` keyword is used with a dictionary-like structure:

        <field_name>: ['$json_object', <json_object_value>]

For example:

        'metadata': ['$json_object', {
            'date_created': '2020-03-13',
            'author': 'Jane Doe'
        }]
        
For collections or list of JSON objects, the `'$json_array'` is used instead:

        <field_name>: ['$json_array': <json_object_list>]
        
For example:

        'authors': ['$json_array', [
            {
                'name': 'Peter Z',
                'institution': 'Some University'
            },
            {
                'name': 'Mary Q',
                'institution': 'Some Research Institute'
            }
        ]]
        
#### Convenience Methods
 
For convenience, the `json_mapper` module makes available 2 helper methods that allow easy inclusion of JSON 
predefined JSON nodes into the specification. These are `json_object` for JSON objects, and `json_array` for 
JSON arrays. `json_object` expects a dictionary-like structure as an input. 

For example, the previous example can be expressed as the following:

        'metadata': json_object({
            'date_created': '2020-03-13',
            'author': 'Jane Doe'
        })
        
The `json_array` method treats argument list as a list of JSON objects. For example:

        'authors': json_array(
            {
                'name': 'Peter Z',
                'institution': 'Some University'
            },
            {
                'name': 'Mary Q',
                'institution': 'Some Research Institute'
            }
        )
        
 Note that any list literal provided within the `json_array` method is treated as a single object. For instance, the
 call `json_array([{'object_id': 123}, {'object_id': 456}])` has *one* item in the resulting list of list.
