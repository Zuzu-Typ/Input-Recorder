# -*- coding: cp1252 -*-

# By Zuzu_Typ

import ctypes
import os
from ctypes import wintypes

import winput
    
import time
import zlib
try: # Python 2
    from Tkinter import *
    import ttk
    import tkFileDialog as filedialog
    import tkMessageBox as messagebox
    
except ImportError: # Python 3
    from tkinter import *
    from tkinter import filedialog
    from tkinter import messagebox
    from tkinter import ttk
    

RECORD_MOVEMENT = True

MIN_FPS = 20

WAIT_BETWEEN_ACTIONS = True

SAVE_COMPRESSED = True

IS_LOCKED = False

IS_RELATIVE = False

# lang

button_create_new_macro = None

button_save_macros = None

button_choose_stop_recording_key = None

root = None

stop_recording_key = winput.VK_ESCAPE

macros = {}
current_macro = []
time_delta = 0
start_time = time.time()
last_time = 0
last_flip = time.time()
options = {}
screen_res = (800,600)

user32 = ctypes.WinDLL('user32', use_last_error=True)

INPUT_MOUSE    = 0
INPUT_KEYBOARD = 1
INPUT_HARDWARE = 2

KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP       = 0x0002
KEYEVENTF_UNICODE     = 0x0004
KEYEVENTF_SCANCODE    = 0x0008

MAPVK_VK_TO_VSC = 0

class Config:
    def __init__(self, filename):
        file_ = open(filename, "rb")
        content_string = file_.read()
        file_.close()
        self.filename = filename
        try:
            content_string = zlib.decompress(content_string)
        except:
            pass
        content_string = content_string.decode("utf-8")
        self.content_list = list(content_string.split("\n"))

    def save(self):
        content_string = ""
        for i in self.content_list:
            content_string += i
            
        content_string = zlib.compress(content_string.encode("utf-8"), 9)
        
        file_ = open(self.filename, "wb")
        file_.write(content_string)
        file_.close()

    def get(self, text):
        return text in self.content_list

    def add(self, text):
        if not self.get(text):
            self.content_list.append(text)

config = Config("cfg.ini")

# msdn.microsoft.com/en-us/library/dd375731
# keys

# C struct definitions

wintypes.ULONG_PTR = wintypes.WPARAM

class MOUSEINPUT(ctypes.Structure):
    _fields_ = (("dx",          wintypes.LONG),
                ("dy",          wintypes.LONG),
                ("mouseData",   wintypes.DWORD),
                ("dwFlags",     wintypes.DWORD),
                ("time",        wintypes.DWORD),
                ("dwExtraInfo", wintypes.ULONG_PTR))

class KEYBDINPUT(ctypes.Structure):
    _fields_ = (("wVk",         wintypes.WORD),
                ("wScan",       wintypes.WORD),
                ("dwFlags",     wintypes.DWORD),
                ("time",        wintypes.DWORD),
                ("dwExtraInfo", wintypes.ULONG_PTR))

    def __init__(self, *args, **kwds):
        super(KEYBDINPUT, self).__init__(*args, **kwds)
        # some programs use the scan code even if KEYEVENTF_SCANCODE
        # isn't set in dwFflags, so attempt to map the correct code.
        if not self.dwFlags & KEYEVENTF_UNICODE:
            self.wScan = user32.MapVirtualKeyExW(self.wVk,
                                                 MAPVK_VK_TO_VSC, 0)

class HARDWAREINPUT(ctypes.Structure):
    _fields_ = (("uMsg",    wintypes.DWORD),
                ("wParamL", wintypes.WORD),
                ("wParamH", wintypes.WORD))

class INPUT(ctypes.Structure):
    class _INPUT(ctypes.Union):
        _fields_ = (("ki", KEYBDINPUT),
                    ("mi", MOUSEINPUT),
                    ("hi", HARDWAREINPUT))
    _anonymous_ = ("_input",)
    _fields_ = (("type",   wintypes.DWORD),
                ("_input", _INPUT))

LPINPUT = ctypes.POINTER(INPUT)

def _check_count(result, func, args):
    if result == 0:
        raise ctypes.WinError(ctypes.get_last_error())
    return args

user32.SendInput.errcheck = _check_count
user32.SendInput.argtypes = (wintypes.UINT, # nInputs
                             LPINPUT,       # pInputs
                             ctypes.c_int)  # cbSize

# Functions

def MouseEvent(dwFlags = 0x0001, dx = 0, dy = 0, mouseData = 0x000):
    me = INPUT(type=INPUT_MOUSE,
               mi=MOUSEINPUT(dx = dx, dy = dy, dwFlags = dwFlags, mouseData = mouseData))
    user32.SendInput(1, ctypes.byref(me), ctypes.sizeof(me))

def PressKey(hexKeyCode):
    x = INPUT(type=INPUT_KEYBOARD,
              ki=KEYBDINPUT(wVk=hexKeyCode))
    user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))

def ReleaseKey(hexKeyCode):
    x = INPUT(type=INPUT_KEYBOARD,
              ki=KEYBDINPUT(wVk=hexKeyCode,
                            dwFlags=KEYEVENTF_KEYUP))
    user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))

class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_ulong), ("y", ctypes.c_ulong)]



def getMousePosition():
    pt = POINT()
    user32.GetCursorPos(ctypes.byref(pt))
    return (pt.x, pt.y)

def hookAllEvents(event):
    global current_macro, time_delta, start_time, last_time, RECORD_MOVEMENT, hookManager, options, stop_recording_key, IS_RELATIVE, screen_res, last_flip, MIN_FPS
    IS_RELATIVE = (IS_RELATIVE or options["relative"].get())

    this_time = time.time()
    time_delta = ((this_time - start_time) - last_time)
    last_time = this_time - start_time

    if (this_time - last_flip) > 1./MIN_FPS:
        root.update()
        last_flip = this_time

    if type(event) == winput.MouseEvent:
        if options["mouse"].get():
            x, y = event.position
            if IS_RELATIVE:
                x = round(float(x)/screen_res[0], 5)
                y = round(float(y)/screen_res[1], 5)
            if event.action == winput.WM_MOUSEMOVE:
                if RECORD_MOVEMENT: 
                    current_macro.append((time_delta, winput.WM_MOUSEMOVE, x, y))
            else:
                current_macro.append((time_delta, event.action, x, y))
            return 1

    else:
        
        key_vkCode = event.vkCode
        if event.action == winput.WM_KEYDOWN:
            if key_vkCode == stop_recording_key:
                winput.unhook_mouse()
                winput.unhook_keyboard()
                winput.stop()
                return
                
        if options["keyboard"].get():
            current_macro.append((time_delta, event.action, key_vkCode))

def createNewMacro(name = None):
    global macros, current_macro, last_time, options, start_time, last_flip

    if not name:
        name = "Macro #{}".format(len(macros))
        
    start_time = time.time()
    last_time = 0
    last_flip = time.time()
    
    winput.hook_mouse(hookAllEvents)
    winput.hook_keyboard(hookAllEvents)
    winput.wait_messages()

    if current_macro:
        macros[name] = current_macro
        current_macro = []

def getMacros():
    global macros
    return macros

def playMacro(macro):
    global WAIT_BETWEEN_ACTIONS, last_time, root, IS_RELATIVE, options, screen_res, last_flip, MIN_FPS, STOP_PLAYING
    IS_RELATIVE = (IS_RELATIVE or options["relative"].get())
    total_time = 0
    start_time = time.time()
    last_time = 0
    for action in macro:
        if (STOP_PLAYING):
            break
        this_time = time.time()
        total_time += action[0]
        if (this_time - last_flip) > 1./MIN_FPS:
            root.update()
            winput.get_message()
            last_flip = this_time
        
        time_delta = max(total_time - (this_time-start_time),0) 
        
        action_type = int(action[1])
        
        if WAIT_BETWEEN_ACTIONS:
            if time_delta: time.sleep(time_delta)
            
        if action_type in (winput.WM_KEYUP, winput.WM_SYSKEYUP, winput.WM_KEYDOWN, winput.WM_SYSKEYDOWN):
            key = int(action[2])
            if action_type == winput.WM_KEYUP: # key up
                ReleaseKey(key)
            else:
                PressKey(key)

        elif action_type == winput.WM_MOUSEMOVE:
            desired_position = (int(round(action[2] * screen_res[0],0)), int(round(action[3] * screen_res[1],0))) if IS_RELATIVE else (int(action[2]), int(action[3]))
            user32.SetCursorPos(*desired_position)

        else:
            current_mouse_position = getMousePosition()
            relative_position = (int(round(action[2] * screen_res[0],0)) - current_mouse_position[0], int(round(action[3] * screen_res[1],0)) - current_mouse_position[1]) if IS_RELATIVE else (int(action[2]) - current_mouse_position[0], int(action[3]) - current_mouse_position[1])

            mouse_change = 0x0002 if action_type == winput.WM_LBUTTONDOWN else \
                           0x0004 if action_type == winput.WM_LBUTTONUP else \
                           0x0020 if action_type == winput.WM_MBUTTONDOWN else \
                           0x0040 if action_type == winput.WM_MBUTTONUP else \
                           0x0008 if action_type == winput.WM_RBUTTONDOWN else \
                           0x0010

            MouseEvent(0x0001 + mouse_change, *relative_position)

            root.update()
        
def saveMacros(macros, filename):
    global options, SAVE_COMPRESSED, IS_RELATIVE
    file_ = open(filename,"wb")
    file_content = "*{}".format(filename)
    if options["once"].get():
        file_content += " -o"
    if (options["relative"].get() or IS_RELATIVE):
        file_content += " -r"

    file_content += "\n"
    for macro_name in macros:
        macro = macros[macro_name]
        file_content += "|{}\n".format(macro_name)
        for action in macro:
            file_content += "{}, {}, {}".format(action[0], action[1], action[2])
            if len(action) == 4:
                file_content += ", {}".format(action[3])

            file_content += "\n"
            
    if SAVE_COMPRESSED:
        file_content = zlib.compress(file_content.encode("utf-8"),9)
    file_.write(file_content)

    file_.close()

def loadMacros(filename):
    global config, IS_LOCKED, button_create_new_macro, button_save_macros, IS_RELATIVE
    macros = {}
    
    file_ = open(filename, "rb")
    file_content = file_.readlines()
    file_content_string = b""
    for line in file_content:
        file_content_string += line
    try:
        file_content_string = zlib.decompress(file_content_string)
    except: pass
    try: file_content_string = file_content_string.decode()
    except: pass
    file_content = []
    current_content = ""
    for character in file_content_string:
        if len(current_content) and current_content[-1] == "\n":
            file_content.append(current_content)
            current_content = character
        else:
            current_content += character
    file_.close()

    macro = []

    macro_name = ""

    for line in file_content:
        if line[0] == "*":
            line = line[1:]
            line = line.strip()
            line_split = line.split(" ")

            if config.get(os.path.basename(line_split[0])):
                IS_LOCKED = False
                IS_RELATIVE = False
                button_create_new_macro.config(state=NORMAL)
                button_save_macros.config(state=NORMAL)
                return

            if "-o" in line_split:
                IS_LOCKED = True
                button_create_new_macro.config(state=DISABLED)
                button_save_macros.config(state=DISABLED)
                config.add(os.path.basename(line_split[0]))
                continue

            if "-r" in line_split:
                IS_RELATIVE = True
            else:
                IS_RELATIVE = False
                
            IS_LOCKED = False
            button_create_new_macro.config(state=NORMAL)
            button_save_macros.config(state=NORMAL)
            continue
                
        if line[0] == "|":
            if macro:
                macros[macro_name] = macro
                macro = []
                
            macro_name = line.strip()[1:]
            continue
        
        if not "," in line:
            continue


        values = line.split(",")
        action = [float(values[0].strip()), values[1].strip(), eval(values[2].strip())]
        if len(values) == 4: # motion
            action.append(eval(values[3].strip()))
                          
        macro.append(action)
    if macro:
        macros[macro_name] = macro
    return macros

def saveMacrosDialog(macros_=None):
    global macros
    if not macros_:
        macros_ = macros

    filename = filedialog.asksaveasfilename(defaultextension="mcr", filetypes=[("Macros", '.mcr'), ("All Files", '.*')], title="Save...")

    if not filename: return
    saveMacros(macros_,filename)

def loadMacrosDialog():
    global macros

    filename = filedialog.askopenfilename(defaultextension="mcr", filetypes=[("Macros", '.mcr'), ("All Files", '.*')], title="Open...")

    if not filename: return
    
    macros_ = loadMacros(filename)

    if macros_:
        macros = macros_

def choose_stop_recording_key_hook(event):
    global button_choose_stop_recording_key, stop_recording_key

    stop_recording_key = event.vkCode

    button_choose_stop_recording_key.config(text = (winput.all_vk_codes.get(stop_recording_key, chr(stop_recording_key))).replace("VK_", ""), state = NORMAL)

    winput.stop()
    
def choose_stop_recording_key():
    global button_choose_stop_recording_key, stop_recording_key, root
    button_choose_stop_recording_key.config(text = "Press key...", state = DISABLED)

    root.update()

    winput.hook_keyboard(choose_stop_recording_key_hook)

    winput.wait_messages()

    winput.unhook_keyboard()

def launchGUI():
    global macros, options, IS_LOCKED, button_create_new_macro, button_save_macros, button_choose_stop_recording_key, stop_recording_key, root, screen_res
    root = Tk()

    screen_res = (root.winfo_screenwidth(), root.winfo_screenheight())

    options = {"once" : IntVar(), "keyboard" : IntVar(value=1), "mouse": IntVar(value=1), "relative" : IntVar(value=0), "repetitions" : IntVar(value=1)}

    try: root.iconbitmap('Irec.ico')
    except: pass

    root.title("Input Recorder")
    frame = Frame(root)
    scrollbar = ttk.Scrollbar(frame, orient=VERTICAL)
    listbox = Listbox(frame, yscrollcommand=scrollbar.set, width=20,height=18)
    scrollbar.config(command=listbox.yview)
    scrollbar.pack(side=RIGHT, fill=Y)
    listbox.pack(side=LEFT, fill=BOTH, expand=1)

    frame.grid(row=0,column=0,rowspan=9,sticky=N+S+W+E)

    def updateMacroListbox():
        global macros
        a = list(macros)
        a.sort()

        listbox.delete(0,END)

        for macro_name in a:
            listbox.insert(END, macro_name)

    canvas_is_recording = Canvas(root, bg = "white", width = 80, height = 80)
    canvas_is_recording.grid(row=9,column=0, columnspan=3)

    canvas_is_recording.create_rectangle(20,20,60,60, fill = "#161616")
    
    entry_macro_name = ttk.Entry(root, width = 20)
    entry_macro_name.grid(row=0,column=1)

    label_stop_recording = ttk.Label(root, text = "Stop recording key:")
    label_stop_recording.grid(row=7,column=1, sticky=W+E)

    button_choose_stop_recording_key = ttk.Button(root, text = "ESCAPE", command = choose_stop_recording_key)
    button_choose_stop_recording_key.grid(row=7, column=2, sticky=W+E)

    def createNewMacro_():
        canvas_is_recording.delete(ALL)
        canvas_is_recording.create_oval(20,20,60,60,fill = "#db0808")
        
        root.update()
        createNewMacro(entry_macro_name.get())
        entry_macro_name.delete(0,END)
        updateMacroListbox()
        canvas_is_recording.delete(ALL)
        canvas_is_recording.create_rectangle(20,20,60,60, fill = "#161616")

    if IS_LOCKED:
        button_create_new_macro = ttk.Button(root, text = "Add macro", command = createNewMacro_, state=DISABLED)
        button_create_new_macro.grid(row=0,column=2)
    else:
        button_create_new_macro = ttk.Button(root, text = "Add macro", command = createNewMacro_)
        button_create_new_macro.grid(row=0,column=2)
        checkbuttonKeyboard = ttk.Checkbutton(root, text="Keyboard", variable = options["keyboard"])
        checkbuttonKeyboard.grid(row=1,column=1)

        checkbuttonMouse = ttk.Checkbutton(root, text="Mouse", variable = options["mouse"])
        checkbuttonMouse.grid(row=1,column=2, sticky=W)

        checkbuttonOnce = ttk.Checkbutton(root, text="Play once", variable = options["once"])
        checkbuttonOnce.grid(row=2,column=1)
        
        checkbuttonRelative = ttk.Checkbutton(root, text="Relative coords", variable = options["relative"])
        checkbuttonRelative.grid(row=2,column=2)

    def deleteMacro(*e):
        if listbox.curselection():
            macro = listbox.get(listbox.curselection())
            if e or messagebox.askyesno("Are you sure?", "Are you sure you want to delete {}?".format(macro)):
                macros.pop(macro)
                listbox.delete(listbox.curselection())

    def dialogRunMacro():
        global macros, root, STOP_PLAYING
        STOP_PLAYING = False
        if listbox.curselection():
            canvas_is_recording.delete(ALL)
            canvas_is_recording.create_polygon(20,20,60,40,20,60, fill="blue")
            root.update()
            macro = macros[listbox.get(listbox.curselection())]
            
            def interrupt(event):
                global STOP_PLAYING, stop_recording_key
                if event.vkCode == stop_recording_key:
                    STOP_PLAYING = True
                    
            winput.hook_keyboard(interrupt)
            repetitions = options["repetitions"].get()
            
            if repetitions == 0:
                while not STOP_PLAYING:
                    playMacro(macro)
            else:
                for i in range(repetitions):
                    if STOP_PLAYING:
                        break
                    playMacro(macro)

            winput.unhook_keyboard()
            canvas_is_recording.delete(ALL)
            canvas_is_recording.create_rectangle(20,20,60,60, fill = "#161616")
            if IS_LOCKED:
                deleteMacro(True)

    label_repetitions_entry = ttk.Label(root, text = "Macro repetitions:")
    label_repetitions_entry.grid(row=8,column=1, sticky=W+E)
    repetitions_entry = ttk.Spinbox(root, from_=0, to=2**20, textvariable = options["repetitions"])
    repetitions_entry.grid(row=8,column=2)

    button_run_macro = ttk.Button(root,text = "Run macro", command = dialogRunMacro)
    button_run_macro.grid(row=3,column=1, columnspan=2, sticky=W+E)

    if IS_LOCKED:
        button_save_macros = ttk.Button(root, text = "Save macros", command = saveMacrosDialog, state=DISABLED)
        button_save_macros.grid(row=4,column=1, columnspan=2, sticky=W+E)
    else:
        button_save_macros = ttk.Button(root, text = "Save macros", command = saveMacrosDialog)
        button_save_macros.grid(row=4,column=1, columnspan=2, sticky=W+E)

    def loadMacrosDialog_():
        loadMacrosDialog()
        updateMacroListbox()

    button_load_macros = ttk.Button(root, text = "Open macros", command = loadMacrosDialog_)
    button_load_macros.grid(row=5,column=1, columnspan=2, sticky=W+E)

    

    button_delete_macro = ttk.Button(root, text = "Delete macro", command = deleteMacro)
    button_delete_macro.grid(row=6,column=1,columnspan=2,sticky=W+E)

    root.bind("<Delete>", deleteMacro)
    
    root.mainloop()

if __name__ == "__main__":
    launchGUI()
    config.save()
