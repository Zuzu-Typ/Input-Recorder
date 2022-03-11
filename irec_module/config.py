
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

import os, atexit

CONFIG_FILE = "config.dict"

__config = {}

if os.path.exists(CONFIG_FILE):
    __file = open(CONFIG_FILE, "r", encoding="UTF8")
    content = __file.read().strip()
    __file.close()

    if not (content.startswith("{") and content.endswith("}") and not ";" in content):
        raise Exception("Invalid config file!")

    __config = eval(content)

def get(key, default = None):
    global __config
    return __config.get(key, default)

def set(key, value):
    global __config
    __config[key] = value

def __save():
    global __config
    
    __file = open(CONFIG_FILE, "w", encoding="UTF8")
    __file.write(repr(__config))
    __file.close()

atexit.register(__save)
