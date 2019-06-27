"""
OrderedDict I/O -- format specfic

Copyright (c) 2019 Benjamin P. Haley

See the LICENSE file for information on usage and redistribution of this
file and for a DISCLAIMER OF ALL WARRANTIES.
"""

import json
from collections import OrderedDict
from jsonschema import RefResolver, validate
from jsonschema.exceptions import SchemaError, ValidationError

def od_ext():
    return '.json'

def write_od(od, path):
    """Write od to file"""
    with open(path, 'w') as f:
        json.dump(od, f, indent=4)

def read_od(path, schema_path=None):
    """
    Read od from file; validate if schema_path is not None; raise RuntimeError 
    on validation error
    """
    with open(path, 'r') as f:
        od = json.load(f, object_pairs_hook=OrderedDict)
    if schema_path is not None:
        with open(schema_path+'.json', 'r') as f:
            sd = json.load(f)
        try:
            #handlers = {'file': _handle_file_uri}
            resolver = RefResolver.from_schema(sd) #, handlers=handlers)
            validate(od, sd, resolver=resolver)
        except SchemaError as e:
            raise RuntimeError('Bad schema: '+str(e))
        except ValidationError as e:
            raise RuntimeError('Bad Task: '+str(e))
    return od

