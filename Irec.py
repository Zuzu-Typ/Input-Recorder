#!/usr/bin/python

"""
Input Recorder - Record and play back keyboard and mouse input.
Copyright (C) 2022  Zuzu_Typ

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import os, sys

os.environ["PyPI_REQUIREMENTS_OUTPUT"] = "ON"

os.chdir(os.path.dirname(sys.argv[0]))

try:
    import winput
    import PIL
except ImportError:
    import requirements


argv_short_to_long_dict = { "h" : "help", "?" : "help" }

kwargs_with_argments = ()

HELP_STRING = """Input Recorder.
Records and plays back macros.

Currently only supports GUI mode.

Usage: irec
"""

def start_command_line_mode(*args, **kwargs):
    pass

def start_windowed_mode():
    import irec_module.window
    

def main(*args, **kwargs):
    if kwargs.get("help", False):
        print(HELP_STRING)
        return

    if kwargs or args:
        start_command_line_mode(*args, **kwargs)

    start_windowed_mode()

def process_argv():
    argv = sys.argv

    kwargs = {}
    args = []

    if len(argv) > 1:
        last_command = None
        
        for arg in argv[1:]:
            if len(arg) == 2 and (arg[0] == "-" or arg[0] == "/"):
                command_alias = arg[1]
                
                if not command_alias in argv_short_to_long_dict:
                    raise KeyError("Unknown command line argument {}. Try -h for a list of commands.".format(arg))

                if last_command:
                    raise ValueError("Argument '{}' has no value.".format(last_command))

                command = argv_short_to_long_dict[command_alias]

                if command in kwargs_with_argments:
                    last_command = command

                else:
                    kwargs[command] = True

            elif len(arg) > 2 and arg.startswith("--"):
                command = arg[2:]
                
                if not command in argv_short_to_long_dict.values():
                    raise KeyError("Unknown command line argument {}. Try -h for a list of commands.".format(arg))

                if last_command:
                    raise ValueError("Argument '{}' has no value.".format(last_command))

                if command in kwargs_with_argments:
                    last_command = command

                else:
                    kwargs[command] = True

            else:
                if last_command:
                    kwargs[last_command] = arg
                    last_command = None

                else:
                    args.append(arg)

        if last_command:
            raise ValueError("Argument '{}' has no value.".format(last_command))

    return (args, kwargs)
                

if __name__ == "__main__":
    args, kwargs = process_argv()
    main(*args, **kwargs)

