"""
Simulator class

Copyright (c) 2019 Benjamin P. Haley

See the LICENSE file for information on usage and redistribution of this
file and for a DISCLAIMER OF ALL WARRANTIES.
"""

import re

from .task import Task
from .run import run_command

class Simulator(Task):
    """A Task that runs an external program"""

    def __init__(self, path=None, echo_output=True):
        Task.__init__(self, path=path, echo_output=echo_output)

    def _setup(self):
        """
        Do any preprocessing, setup, initialization needed before calling
        run_command; implemented by derived classes
        """
        pass

    def _cleanup(self):
        """
        Do any postprocessing, cleanup, analysis needed after calling
        run_command; implemented by derived classes
        """
        pass

    def _run(self):
        """Run the simulator; return (status, out, err) from run_command()"""
        self._setup()
        self.inputs.verify_uris()
        for infile, template in self.templates.items():
            with open(template, 'r') as f:
                s = f.read()
            for n in self.inputs.names():
                val = str(self.inputs.get_value(n))
                # XXX if type == 'array': val = ' '.join(str(x) for x in value)
                s = re.sub(n, val, s)
            with open(infile, 'w') as f:
                f.write(s)
        status, out, err = run_command(self.command, echo=self.echo_output)
        self.complete = True
        self._cleanup()
        self.outputs.verify_uris()
        return status, out, err

