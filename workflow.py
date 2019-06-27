"""
Workflow class

Copyright (c) 2019 Benjamin P. Haley

See the LICENSE file for information on usage and redistribution of this
file and for a DISCLAIMER OF ALL WARRANTIES.
"""

import sys, os.path
from collections import OrderedDict
from inspect import isclass

from odio import read_od

schema_file = 'workflow_schema'

class Workflow(object):

    def __init__(self, path=None):
        self.od = OrderedDict()
        self.tasks = []
        if path is not None:
            self.read(path)

    def read(self, path, validate=True):
        """
        Read Workflow from a file in the format supported by read_od(); raise
        a RuntimeError if validate is True and the Workflow format is bad
        """
        this_dir = os.path.dirname(os.path.abspath(__file__))
        schema_path = os.path.join(this_dir, schema_file)
        d = read_od(path, schema_path if validate is True else None)
        self.od = d['workflow']
        for tod in self.od['tasks']:
            m = __import__(tod['taskname'])
            for v in m.__dict__.values():
                if isclass(v) is True:
                    ctor = v
            task = ctor(echo_output=self.od['echo_output'])
            self.tasks.append(task)

    def run(self):
        """
        Execute all Tasks until all are complete; connect outputs from a Task 
        to the inputs of the next Task at each iteration 
        """
        task_name = ''
        try:
            while True:  # iterate until all Tasks are complete
                complete = True
                for i,t in enumerate(self.tasks):
                    task_name = t.name
                    if i > 0:  # connect outputs of previous Task
                        iomap = self.od['tasks'][i]['iomap']
                        t.connect(self.tasks[i-1], iomap=iomap)
                    status, out, err = t.run()
                    if status is False:  # Task t failed
                        raise RuntimeError(err)
                    if t.echo_output is True:
                        # out was already written to stdout during t.run()
                        fmt = '\n=== Task {0:s} complete in {1:f} s===\n\n'
                        dur = t.outputs.get_value('_duration')
                        sys.stdout.write(fmt.format(task_name, dur))
                    complete &= t.complete
                if complete is True:
                    break
        except RuntimeError as e:
            fmt = 'Error: Task {0:s}: {1:s}'
            sys.stderr.write(fmt.format(task_name, str(e)))
            sys.exit(1)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.stderr.write('Usage: {} workflow_file\n'.format(sys.argv[0]))
        sys.exit(1)
    Workflow(path=sys.argv[1]).run()
