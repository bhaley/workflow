# workflow
Python library for creating iterative workflows of local tasks

This simple workflow library is designed to iteratively execute a sequence of 
tasks, which can be simple Python functions or complex external simulators.   
It does not support access to remote computers or batch systems; for that case 
see the Pegasus project.

The workflow is specified by a JSON file, with the following format:
```
{
    "workflow": {
        "echo_output": true,
        "tasks": [
            {
                "taskname": taskname,
                "iomap": {
                    "input_name": "prev_output_name"
                }
            }
        ]
    }
}
```

The tasks array determines the order of the specific tasks, and each task is
specified by a JSON file, like the following:
```
{
    "task": {
        "name": "Task name",
        "command": "/path/to/exe input_file",
        "echo_output": true,
        "templates": {
            "input_file": "input_file_template",
        },
        "inputs": {
            "input_name": {
                "type":  "type_name",
                "value": "",
                "label": "",
                "units": "",
                "tags": []
            } 
        },
        "outputs": {},
    }
}
```

Each input and output parameter has a name, a type, and a value, and can include
optional label, units, and metadata tags.  The value field can be any of the
following:
* boolean
* string
* integer
* real 
* array
* uri

