"""
Task class

Copyright (c) 2019 Benjamin P. Haley

See the LICENSE file for information on usage and redistribution of this
file and for a DISCLAIMER OF ALL WARRANTIES.
"""

import os, time
from socket import gethostname
from collections import OrderedDict

from .params import Params
from .odio import read_od, write_od

schema_file = 'task_schema'

class Task(object):
    """A discrete step in a workflow"""

    def __init__(self, path=None, echo_output=True):
        self.name = ''
        self.command = ''
        self.echo_output = echo_output
        self.templates = OrderedDict()
        self.inputs = Params()
        self.outputs = Params()
        if path is not None:
            self.read(path)
        self.complete = False

    def connect(self, prev_task, iomap={}):
        """
        Connect this Task to prev_task, by setting the values of inputs from
        the values of outputs in prev_task; the mapping iomap should have the
        names of names of inputs in this Task as keys and outputs from prev_task
        as values
        """
        for curr_name, prev_name in iomap.values():
            curr_param = self.inputs[curr_name]
            prev_param = prev_task.outputs[prev_name]
            prev_value = prev_task.outputs.get_value(prev_name)
            if curr_param.type != prev_param.type:
                fmt1 = 'Type {0} of output {1} in task {2} does not match '
                msg  = fmt1.format(prev_param.type, prev_name, prev_task.name)
                fmt2 = 'type {0} of input {1} in task {2}'
                msg += fmt2.format(curr_param.type, curr_name, self.name)
                raise RuntimeError(msg)
            self.inputs.set_value(curr_name, prev_value)

    def _run(self):
        """
        Implemented by derived classes: set self.complete, 
        return (status, stdout, stderr) 
        """
        self.complete = True
        return True, '', ''

    def run(self):
        """
        Execute the task; return (status, out, err) where status is True/False 
        to indicate success, out is stdout, and err is stderr
        """
        t0 = time.time()
        status, out, err = self._run()
        t1 = time.time()
        self.outputs.add('_user', 'string', os.environ['USER'])
        self.outputs.add('_host', 'string', gethostname())
        self.outputs.add('_date', 'string', time.ctime(t0))
        self.outputs.add('_duration', 'real', t1-t0, units='s')
        self.outputs.add('_status', 'boolean', status)
        self.outputs.add('_stdout', 'string', out)
        self.outputs.add('_stderr', 'string', err)
        return status, out, err

    def read(self, path, validate=True):
        """
        Read Task from a file in the format supported by read_od(); raise a
        RuntimeError if validate is True and the Task format is bad
        """
        this_dir = os.path.dirname(os.path.abspath(__file__))
        schema_path = os.path.join(this_dir, schema_file)
        d = read_od(path, schema_path if validate is True else None)
        od = d['task']
        self.name = od['name']
        self.command = od['command']
        self.echo_output &= od['echo_output']
        self.templates = od['templates']
        self.inputs = Params(od['inputs'])
        self.inputs.verify_types()
        self.outputs = Params(od['outputs'])
        self.outputs.verify_types()

    def write(self, path):
        """Write Task to a file in the format supported by write_od()"""
        od = OrderedDict()
        od['name'] = self.name
        od['command'] = self.command
        od['echo_output'] = self.echo_output
        od['templates'] = self.templates
        od['inputs'] = self.inputs.od
        od['outputs'] = self.outputs.od
        write_od({'task': od}, path)

