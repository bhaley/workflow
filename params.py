"""
Params class

Copyright (c) 2019 Benjamin P. Haley

See the LICENSE file for information on usage and redistribution of this
file and for a DISCLAIMER OF ALL WARRANTIES.
"""

from collections import OrderedDict
from urllib.request import urlopen
from urllib.error import URLError
import re, os

data_types = [
    'boolean',
    'string',
    'integer', 
    'real', 
    'array',
    'uri'
]

class Params(object):
    """A collection of (name, properties) tuples"""

    def __init__(self, od=OrderedDict()):
        self.od = od

    def __getitem__(self, name):
        """Return the entire dict for the specified parameter"""
        return self.od[name]

    def _verify_type(self, typename):
        if typename not in data_types:
            raise RuntimeError('Unknown parameter type: '+typename)

    def names(self):
        """Return the names of all parameters for iteration"""
        return self.od.keys()

    def add(self, name, typename, value, label='', units='', tags=[]):
        """
        Add a new parameter; overwrites an existing parameter of the same name
        """
        self._verify_type(typename)
        od = OrderedDict()
        od['type']  = typename
        od['value'] = value
        od['label'] = label
        od['units'] = units
        od['tags']  = tags
        self.od[name] = od

    def _get_d(self, name):
        d = self.od.get(name)
        if d is None:
            raise RuntimeError('Unknown parameter: '+name)
        return d

    def get_value(self, name):
        """
        Get the value of the specified parameter; raises a RuntimeError if name 
        is not an existing parameter
        """
        d = self._get_d(name)
        v = d['value']
        if d['type'] == 'integer':
            v = int(v)
        elif d['type'] == 'real':
            v = float(v)
        elif d['type'] == 'boolean':
            v = ('True' == v)
        elif d['type'] == 'array':
            v = [float(x) for x in v.split()]
        return v
        
    def set_value(self, name, value):
        """
        Set the value of the specified parameter; raises a RuntimeError if name 
        is not an existing parameter
        """
        self._get_d(name)['value'] = value
        
    def add_tag(self, name, tag):
        """
        Add a new tag to the specified parameter, if the tag does not already
        exist; raises a RuntimeError if name is not an existing parameter
        """
        d = self._get_d(name)
        if tag not in d['tags']:
            d['tags'].append(tag)

    def has_tag(self, name, tag):
        """
        Return True/False to indicate whether tag exists for the specified
        parameter; raises a RuntimeError if name is not an existing parameter
        """
        return tag in self._get_d(name)['tags']

    def verify_types(self):
        """
        Verify that each parameter has a known type; raise a RuntimeError if
        any unknown type is found
        """
        for d in self.od.values():
            self._verify_type(d['type'])

    def verify_uris(self):
        """
        Verify that all URI parameters exist; raise a RuntimeError if any uri
        cannot be opened
        """
        for n,d in self.od.items():
            if d['type'] == 'uri':
                try:
                    p = expand_workdir(d['value'])
                    r = urlopen(p)
                except URLError:
                    msg = '{0} does not exist at {1}\n'.format(n, p)
                    raise RuntimeError(msg)


def expand_workdir(path):
    if 'WORKDIR' in path:
        path = re.sub('WORKDIR', os.getcwd(), path)
    return path

def uri2path(uri):
    path = uri
    if 'file://' in path:
        path = path[7:]
    return expand_workdir(path)

