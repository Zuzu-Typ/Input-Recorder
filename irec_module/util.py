
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

import winput, re

def vk_code_to_key_name(vk_code):
    name = winput.vk_code_dict.get(vk_code, "VK_UNKNOWN")

    if name.startswith("VK_"):
        name = name[3:]
    
    special_left_key_match = re.match("L(CONTROL|MENU|WIN|SHIFT)", name)

    if special_left_key_match:
        name = "LEFT " + special_left_key_match.group(1)

    special_right_key_match = re.match("R(CONTROL|MENU|WIN|SHIFT)", name)

    if special_right_key_match:
        name = "RIGHT " + special_right_key_match.group(1)

    name = name.replace("_", " ")

    name = " ".join((word.capitalize() for word in name.split(" ")))

    oem_match = re.fullmatch("(.*)OEM(.*)", name, re.IGNORECASE)

    if oem_match:
        name = oem_match.group(1) + "OEM" + oem_match.group(2)
    
    return name

def mouse_button_to_name(button):
    return "Left" if button == winput.LMB else \
           "Right" if button == winput.RMB else \
           "Middle" if button == winput.MMB else \
           "X1" if button == winput.XMB1 else \
           "X2"
