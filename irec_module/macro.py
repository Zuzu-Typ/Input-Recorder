
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

try:
    from . import config, util
except ImportError:
    import config

import winput, time, ctypes, zlib

float_to_bytes = lambda f: bytes(ctypes.c_float(f))
bytes_to_float = lambda b: ctypes.cast(b, ctypes.POINTER(ctypes.c_float)).contents.value

perf_counter_ns = None

if hasattr(time, "perf_counter_ns"):
    perf_counter_ns = time.perf_counter_ns
elif hasattr(time, "perf_counter"):
    perf_counter_ns = lambda: int(time.perf_counter() * 1000000000.)
else:
    perf_counter_ns = lambda: int(time.time() * 1000000000.)

class MacroConfig:
    version = 1
    
    def __init__(self, screen_width, screen_height):
        assert type(screen_width) == type(screen_height) == int
        
        self.screen_width = screen_width
        self.screen_height = screen_height

    def to_bytes(self):
        data = self.version.to_bytes(1, "little") + self.screen_width.to_bytes(2, "little") + self.screen_height.to_bytes(2, "little")

        return len(data).to_bytes(1, "little") + data

    @classmethod
    def from_bytes(cls, bytes_obj):
        assert type(bytes_obj) == bytes and len(bytes_obj) > 1 and int.from_bytes(bytes_obj[0:1], "little") + 1 == len(bytes_obj)

        assert int.from_bytes(bytes_obj[1:2], "little") == cls.version

        return cls(int.from_bytes(bytes_obj[2:4], "little"), int.from_bytes(bytes_obj[4:], "little"))

class MacroEvent:
    def prepare(self):
        raise NotImplementedError()
    
    def execute(self):
        raise NotImplementedError()

    def to_bytes(self):
        raise NotImplementedError()

    def from_bytes(self):
        raise NotImplementedError()

class MousePositionEvent(MacroEvent):
    bytecode = b"P"
    
    def __init__(self, config, x, y):
        self.config = config
        self.rel_x = float(x) / config.screen_width
        self.rel_y = float(y) / config.screen_height

    def copy(self):
        self.prepare()
        return self.__class__(self.config, self.x, self.y)

    def prepare(self):
        self.x = int(round(self.config.screen_width * self.rel_x, 0))
        self.y = int(round(self.config.screen_height * self.rel_y, 0))

    def execute(self):
        winput.set_mouse_pos(self.x, self.y)

    def to_bytes(self):
        self.prepare()
        return self.bytecode + self.x.to_bytes(2, "little", signed=True) + self.y.to_bytes(2, "little", signed=True)

    @classmethod
    def from_bytes(cls, config, bytes_obj):
        assert type(bytes_obj) == bytes and len(bytes_obj) == 5 and bytes_obj[0:1] == cls.bytecode

        return cls(config, int.from_bytes(bytes_obj[1:3], "little", signed=True), int.from_bytes(bytes_obj[3:], "little", signed=True))

    def __str__(self):
        return "Set mouse position to ({:.2f}%, {:.2f}%)".format(self.rel_x * 100, self.rel_y * 100)

### doesn't work right because of the mouse acceleration
##class MouseMoveEvent(MacroEvent):
##    bytecode = b"M"
##    
##    def __init__(self, config, dx, dy):
##        self.config = config
##        self.rel_dx = float(dx) / config.screen_width
##        self.rel_dy = float(dy) / config.screen_height
##
##    def prepare(self):
##        self.dx = int(round(self.config.screen_width * self.rel_dx, 0))
##        self.dy = int(round(self.config.screen_height * self.rel_dy, 0))
##
##    def execute(self):
##        winput.move_mouse(self.dx, self.dy)
##
##    def to_bytes(self):
##        self.prepare()
##        return self.bytecode + self.dx.to_bytes(2, "little", signed=True) + self.dy.to_bytes(2, "little", signed=True)
##
##    @classmethod
##    def from_bytes(cls, config, bytes_obj):
##        assert type(bytes_obj) == bytes and len(bytes_obj) == 5 and bytes_obj[0:1] == cls.bytecode
##
##        return cls(config, int.from_bytes(bytes_obj[1:3], "little", signed=True), int.from_bytes(bytes_obj[3:], "little", signed=True))
##
##    def __str__(self):
##        return "Move mouse by ({:.2f}%, {:.2f}%)".format(self.rel_dx, self.rel_dy)

class MouseWheelEvent(MacroEvent):
    def __init__(self, amount):
        self.amount = amount

    def copy(self):
        return self.__class__(self.amount)

    def prepare(self):
        pass

    def to_bytes(self):
        return self.bytecode + self.amount.to_bytes(1, "little", signed=True)

    @classmethod
    def from_bytes(cls, config, bytes_obj):
        assert type(bytes_obj) == bytes and len(bytes_obj) == 2 and bytes_obj[0:1] == cls.bytecode

        return cls(int.from_bytes(bytes_obj[1:], "little", signed=True))

class MouseWheelMoveEvent(MouseWheelEvent):
    bytecode = b"V"
    
    def execute(self):
        winput.move_mousewheel(self.amount)

    def __str__(self):
        return "Move mousewheel by {:+1d}".format(int(self.amount))

class MouseWheelHorizontalMoveEvent(MouseWheelEvent):
    bytecode = b"H"
    
    def execute(self):
        winput.move_mousewheel(self.amount, True)

    def __str__(self):
        return "Move mousewheel horizontally by {:+1d}".format(int(self.amount))

class MouseButtonEvent(MacroEvent):
    def __init__(self, mouse_button):
        self.mouse_button = mouse_button

    def copy(self):
        return self.__class__(self.mouse_button)

    def prepare(self):
        pass

    def to_bytes(self):
        return self.bytecode + self.mouse_button.to_bytes(1, "little")

    @classmethod
    def from_bytes(cls, config, bytes_obj):
        assert type(bytes_obj) == bytes and len(bytes_obj) == 2 and bytes_obj[0:1] == cls.bytecode

        return cls(int.from_bytes(bytes_obj[1:], "little"))

class MouseButtonPressEvent(MouseButtonEvent):
    bytecode = b"B"
    
    def execute(self):
        winput.press_mouse_button(self.mouse_button)

    def __str__(self):
        return "Press {} mouse button".format(util.mouse_button_to_name(self.mouse_button).lower())
        
class MouseButtonReleaseEvent(MouseButtonEvent):
    bytecode = b"b"
    
    def execute(self):
        winput.release_mouse_button(self.mouse_button)

    def __str__(self):
        return "Release {} mouse button".format(util.mouse_button_to_name(self.mouse_button).lower())

class KeyEvent(MacroEvent):
    def __init__(self, vk_code):
        self.vk_code = vk_code

    def copy(self):
        return self.__class__(self.vk_code)

    def prepare(self):
        pass

    def to_bytes(self):
        return self.bytecode + self.vk_code.to_bytes(2, "little")

    @classmethod
    def from_bytes(cls, config, bytes_obj):
        assert type(bytes_obj) == bytes and len(bytes_obj) == 3 and bytes_obj[0:1] == cls.bytecode

        return cls(int.from_bytes(bytes_obj[1:], "little"))

class KeyPressEvent(KeyEvent):
    bytecode = b"K"
    
    def execute(self):
        winput.press_key(self.vk_code)

    def __str__(self):
        return "Press {}".format(util.vk_code_to_key_name(self.vk_code))

class KeyReleaseEvent(KeyEvent):
    bytecode = b"k"
    
    def execute(self):
        winput.release_key(self.vk_code)

    def __str__(self):
        return "Release {}".format(util.vk_code_to_key_name(self.vk_code))

event_bytecode_class_map = {
        b"P" : MousePositionEvent,
##        b"M" : MouseMoveEvent,
        b"V" : MouseWheelMoveEvent,
        b"H" : MouseWheelHorizontalMoveEvent,
        b"B" : MouseButtonPressEvent,
        b"b" : MouseButtonReleaseEvent,
        b"K" : KeyPressEvent,
        b"k" : KeyReleaseEvent,
    }

class EventExecutor:
    def __init__(self, time_offset, event):
        assert type(time_offset) == int and isinstance(event, MacroEvent)
        
        self.time_offset = time_offset
        self.event = event

    def copy(self):
        return EventExecutor(self.time_offset, self.event.copy())

    def prepare(self):
        self.event.prepare()

    def execute_at_time_offset(self, start_time):
        now = perf_counter_ns()

        target_time = start_time + self.time_offset

        while now < target_time:
            diff_in_ms = (target_time - now) // 1000000

            if diff_in_ms > 10:
                time.sleep(diff_in_ms // 10 / 100.)

            else:
                time.sleep(1 / 1000.)
                
            now = perf_counter_ns()

        self.event.execute()

    def to_bytes(self):
        data = self.time_offset.to_bytes(8, "little") + self.event.to_bytes()

        return len(data).to_bytes(1, "little") + data

    @classmethod
    def from_bytes(cls, config, bytes_obj):
        assert type(bytes_obj) == bytes and len(bytes_obj) >= 10 and bytes_obj[0] + 1 == len(bytes_obj)
        
        time_offset = int.from_bytes(bytes_obj[1:9], "little")

        event_type = bytes_obj[9:10]

        assert event_type in event_bytecode_class_map, "Unknown event bytecode '{}'".format(event_type)

        event_class = event_bytecode_class_map[event_type]

        event = event_class.from_bytes(config, bytes_obj[9:])

        return cls(time_offset, event)

    def __str__(self):
        return "Executing {} at {}".format(str(self.event), self.time_offset)

class Macro:
    def __init__(self, name, config, event_executor_list):
        self.name = name
        self.config = config
        self.event_executor_list = event_executor_list

    def run(self):
        for executor in self.event_executor_list:
            executor.prepare()
            
        start_time = perf_counter_ns()
        for executor in self.event_executor_list:
            executor.execute_at_time_offset(start_time)

    def to_bytes(self):
        name_encoded = self.name.encode()
        name_data = len(name_encoded).to_bytes(1, "little") + name_encoded
        return name_data + self.config.to_bytes() + b"".join(map(lambda ee: ee.to_bytes(), self.event_executor_list))

    def as_compressed_bytes(self):
        return zlib.compress(self.to_bytes(), 9)

    @classmethod
    def from_bytes(cls, bytes_obj):
        assert type(bytes_obj) == bytes and len(bytes_obj) > 1 and len(bytes_obj) > int.from_bytes(bytes_obj[0:1], "little")

        offset = bytes_obj[0] + 1

        name = bytes_obj[1:offset].decode()

        config_data_length = bytes_obj[offset] + 1

        config_data = bytes_obj[offset:offset+config_data_length]

        config = MacroConfig.from_bytes(config_data)

        offset += config_data_length

        event_executor_list = []

        while offset < len(bytes_obj):
            event_data_length = bytes_obj[offset] + 1

            assert offset + event_data_length <= len(bytes_obj)

            event_data = bytes_obj[offset : offset + event_data_length]

            event_executor_list.append(EventExecutor.from_bytes(config, event_data))

            offset += event_data_length

        return Macro(name, config, event_executor_list)

    @classmethod
    def from_compressed_bytes(cls, compressed_bytes_obj):
        return cls.from_bytes(zlib.decompress(compressed_bytes_obj))

    @staticmethod
    def from_raw_data(name, start_time, start_mouse_pos, screen_width, screen_height, raw_data):
        event_executor_list = []

        macro_config = MacroConfig(screen_width, screen_height)

        if start_mouse_pos:
            event_executor_list.append(EventExecutor(0, MousePositionEvent(macro_config, start_mouse_pos[0], start_mouse_pos[1])))

        last_mouse_pos = start_mouse_pos

        print(screen_width, screen_height)

        for timestamp, raw_event in raw_data:
            time_offset = timestamp - start_time

            event = None

            if type(raw_event) == winput.MouseEvent:
                if raw_event.action == winput.WM_MOUSEMOVE:
                    event = MousePositionEvent(macro_config, raw_event.position[0], raw_event.position[1])
                    last_mouse_pos = raw_event.position

                elif raw_event.action == winput.WM_LBUTTONDOWN:
                    event = MouseButtonPressEvent(winput.LEFT_MOUSE_BUTTON)

                elif raw_event.action == winput.WM_LBUTTONUP:
                    event = MouseButtonReleaseEvent(winput.LEFT_MOUSE_BUTTON)

                elif raw_event.action == winput.WM_RBUTTONDOWN:
                    event = MouseButtonPressEvent(winput.RIGHT_MOUSE_BUTTON)

                elif raw_event.action == winput.WM_RBUTTONUP:
                    event = MouseButtonReleaseEvent(winput.RIGHT_MOUSE_BUTTON)

                elif raw_event.action == winput.WM_MBUTTONDOWN:
                    event = MouseButtonPressEvent(winput.MIDDLE_MOUSE_BUTTON)

                elif raw_event.action == winput.WM_MBUTTONUP:
                    event = MouseButtonReleaseEvent(winput.MIDDLE_MOUSE_BUTTON)

                elif raw_event.action == winput.WM_XBUTTONDOWN:
                    event = MouseButtonPressEvent(getattr(winput, "XMB" + str(raw_event.additional_data)))

                elif raw_event.action == winput.WM_XBUTTONUP:
                    event = MouseButtonReleaseEvent(getattr(winput, "XMB" + str(raw_event.additional_data)))

                elif raw_event.action == winput.WM_MOUSEWHEEL:
                    event = MouseWheelMoveEvent(int(raw_event.additional_data))

                elif raw_event.action == winput.WM_MOUSEHWHEEL:
                    event = MouseWheelHorizontalMoveEvent(int(raw_event.additional_data))

                else:
                    raise Exception("Unknown Mouse Event")

            elif type(raw_event) == winput.KeyboardEvent:
                if raw_event.action == winput.WM_KEYDOWN or raw_event.action == winput.WM_SYSKEYDOWN:
                    event = KeyPressEvent(raw_event.vkCode)
                    
                elif raw_event.action == winput.WM_KEYUP or raw_event.action == winput.WM_SYSKEYUP:
                    event = KeyReleaseEvent(raw_event.vkCode)

                else:
                    raise Exception("Unknown Keyboard Event")

            else:
                raise Exception("Unknown Event Type")

            event_executor_list.append(EventExecutor(time_offset, event))

        return Macro(name, macro_config, event_executor_list)

def callback(event):
    global raw_data

    raw_data.append((perf_counter_ns(), event))

def callback_with_stop_key(event):
    global stop_recording_key

    if event.vkCode == stop_recording_key:
        winput.stop()

    else:
        global raw_data

        raw_data.append((perf_counter_ns(), event))

def callback_only_stop_key(event):
    global stop_recording_key

    if event.vkCode == stop_recording_key:
        winput.stop()
    

def create_macro(name, start_at, screen_width, screen_height):
    global start, raw_data, stop_recording_key

    mode = config.get("recording_mode", "timer")

    duration = config.get("recording_duration", 10)

    stop_recording_key = config.get("recording_stop_key", winput.VK_ESCAPE)

    mouse_enabled = config.get("record_mouse", True)

    keyboard_enabled = config.get("record_keyboard", True)

    assert mode in ("timer", "key")

    assert type(duration) in (float, int) and duration > 0

    assert type(stop_recording_key) == int and 0 <= stop_recording_key <= 2**15

    assert type(mouse_enabled) == type(keyboard_enabled) == bool

    assert mouse_enabled or keyboard_enabled

    raw_data = []

    while True:
        if time.time() > start_at:
            break
        time.sleep(0.0001)

    start = perf_counter_ns()

    start_mouse_pos = None

    if mode == "timer":
        if mouse_enabled:
            start_mouse_pos = winput.get_mouse_pos()
            winput.hook_mouse(callback)

        if keyboard_enabled:
            winput.hook_keyboard(callback)
        
        while True:
            now = perf_counter_ns()

            if now >= start + duration * 1000000000:
                break

            winput.get_message()

    elif mode == "key":
        if mouse_enabled:
            start_mouse_pos = winput.get_mouse_pos()
            winput.hook_mouse(callback)

        if keyboard_enabled:
            winput.hook_keyboard(callback_with_stop_key)
        else:
            winput.hook_keyboard(callback_only_stop_key)
        
        winput.wait_messages()

    winput.unhook_mouse()
    winput.unhook_keyboard()

    return Macro.from_raw_data(name, start, start_mouse_pos, screen_width, screen_height, raw_data)

def macros_to_bytes(*macros, compressionlevel=9):
    assert macros and all(map(lambda m: isinstance(m, Macro), macros))

    data_array = []

    if len(macros) == 1:
        data_array.append(b"S")
        data_array.append(macros[0].to_bytes())

    else:
        data_array.append(b"M")
        data_array.append(len(macros).to_bytes(1, "little"))

        for macro in macros:
            macro_data = macro.to_bytes()
            data_array.append(len(macro_data).to_bytes(4, "little"))
            data_array.append(macro_data)

    uncompressed_data = b"".join(data_array)

    out_data = zlib.compress(uncompressed_data, compressionlevel)

    uncompressed_data_len = len(uncompressed_data)

    return uncompressed_data_len.to_bytes(4, "little") + out_data

def macros_from_bytes(bytes_obj):
    assert type(bytes_obj) == bytes

    content = bytes_obj[4:]

    uncompressed_bytes = zlib.decompress(content)

    assert uncompressed_bytes and uncompressed_bytes[0:1] in (b"S", b"M")

    if uncompressed_bytes[0:1] == b"S":
        return [Macro.from_bytes(uncompressed_bytes[1:])]

    else:
        macros = []
        
        offset = 1

        macro_count = uncompressed_bytes[offset]

        offset += 1

        while offset < len(uncompressed_bytes):
            assert len(uncompressed_bytes) > offset + 3

            macro_data_length = int.from_bytes(uncompressed_bytes[offset : offset + 4], "little")
            offset += 4
            macro_data = uncompressed_bytes[offset : offset + macro_data_length]
            
            macros.append(Macro.from_bytes(macro_data))

            offset += macro_data_length

        assert len(macros) == macro_count

        return macros

def request_key_callback(event):
    global requested_key
    requested_key = event.vkCode

def request_key(timeout):
    global requested_key
    
    requested_key = None
    
    start = time.time()

    winput.hook_keyboard(request_key_callback)

    while not requested_key:
        now = time.time()

        if now >= start + timeout:
            break

        winput.get_message()

    winput.unhook_keyboard()

    return requested_key

def request_mouse_callback(event):
    global last_request_position, last_request_timestamp

    last_request_position = event.position

    last_request_timestamp = time.time()

def request_mouse_pos(timeout):
    global last_request_position, last_request_timestamp

    last_request_position = None

    last_request_timestamp = time.time()

    winput.hook_mouse(request_mouse_callback)

    while True:
        now = time.time()

        winput.get_message()

        if last_request_position and last_request_timestamp + timeout < now:
            break

    winput.unhook_mouse()

    return last_request_position

    




























