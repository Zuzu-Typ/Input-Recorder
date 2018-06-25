import ctypes
from ctypes import wintypes

class MouseEvent:
    def __init__(self, position, action, time, *additional_data):
        self.position = position
        self.action = action
        self.time = time
        self.additional_data = additional_data
        self.type = "MouseEvent"

class KeyboardEvent:
    def __init__(self, action, vkCode, time):
        self.action = action
        self.vkCode = vkCode
        self.time = time
        self.type = "KeyboardEvent"

user32 = ctypes.windll.user32

LRESULT = ctypes.c_void_p

ULONG_PTR = ctypes.POINTER(ctypes.c_ulong)

WH_MOUSE_LL = (14)

WH_KEYBOARD_LL = (13)

WM_MOUSEMOVE                    =0x0200

WM_LBUTTONDOWN                  =0x0201
WM_LBUTTONUP                    =0x0202

WM_RBUTTONDOWN                  =0x0204
WM_RBUTTONUP                    =0x0205

WM_MBUTTONDOWN                  =0x0207
WM_MBUTTONUP                    =0x0208

WM_MOUSEWHEEL                   =0x020A
WM_MOUSEHWHEEL                  =0x020E

WM_XBUTTONDOWN                  =0x020B
WM_XBUTTONUP                    =0x020C

XBUTTON1      =0x0001
XBUTTON2      =0x0002

MB_LEFT = 0x0001
MB_RIGHT = 0x0002
MB_MIDDLE = 0x0004
MB_X1 = 0x0008
MB_X2 = 0x0016

WM_KEYDOWN                      =0x0100
WM_KEYUP                        =0x0101

WM_SYSKEYDOWN                   =0x0104
WM_SYSKEYUP                     =0x0105

WHEEL_DELTA                  =120
GET_HWORD          =lambda x: ctypes.c_short((x >> 16)).value

all_vk_codes = {30: 'VK_ACCEPT', 107: 'VK_ADD', 93: 'VK_APPS', 246: 'VK_ATTN', 8: 'VK_BACK', 166: 'VK_BROWSER_BACK', 171: 'VK_BROWSER_FAVORITES', 167: 'VK_BROWSER_FORWARD', 172: 'VK_BROWSER_HOME', 168: 'VK_BROWSER_REFRESH', 170: 'VK_BROWSER_SEARCH', 169: 'VK_BROWSER_STOP', 3: 'VK_CANCEL', 20: 'VK_CAPITAL', 12: 'VK_CLEAR', 17: 'VK_CONTROL', 28: 'VK_CONVERT', 247: 'VK_CRSEL', 110: 'VK_DECIMAL', 46: 'VK_DELETE', 111: 'VK_DIVIDE', 40: 'VK_DOWN', 35: 'VK_END', 249: 'VK_EREOF', 27: 'VK_ESCAPE', 43: 'VK_EXECUTE', 248: 'VK_EXSEL', 112: 'VK_F1', 121: 'VK_F10', 122: 'VK_F11', 123: 'VK_F12', 124: 'VK_F13', 125: 'VK_F14', 126: 'VK_F15', 127: 'VK_F16', 128: 'VK_F17', 129: 'VK_F18', 130: 'VK_F19', 113: 'VK_F2', 131: 'VK_F20', 132: 'VK_F21', 133: 'VK_F22', 134: 'VK_F23', 135: 'VK_F24', 114: 'VK_F3', 115: 'VK_F4', 116: 'VK_F5', 117: 'VK_F6', 118: 'VK_F7', 119: 'VK_F8', 120: 'VK_F9', 24: 'VK_FINAL', 195: 'VK_GAMEPAD_A', 196: 'VK_GAMEPAD_B', 204: 'VK_GAMEPAD_DPAD_DOWN', 205: 'VK_GAMEPAD_DPAD_LEFT', 206: 'VK_GAMEPAD_DPAD_RIGHT', 203: 'VK_GAMEPAD_DPAD_UP', 200: 'VK_GAMEPAD_LEFT_SHOULDER', 209: 'VK_GAMEPAD_LEFT_THUMBSTICK_BUTTON', 212: 'VK_GAMEPAD_LEFT_THUMBSTICK_DOWN', 214: 'VK_GAMEPAD_LEFT_THUMBSTICK_LEFT', 213: 'VK_GAMEPAD_LEFT_THUMBSTICK_RIGHT', 211: 'VK_GAMEPAD_LEFT_THUMBSTICK_UP', 201: 'VK_GAMEPAD_LEFT_TRIGGER', 207: 'VK_GAMEPAD_MENU', 199: 'VK_GAMEPAD_RIGHT_SHOULDER', 210: 'VK_GAMEPAD_RIGHT_THUMBSTICK_BUTTON', 216: 'VK_GAMEPAD_RIGHT_THUMBSTICK_DOWN', 218: 'VK_GAMEPAD_RIGHT_THUMBSTICK_LEFT', 217: 'VK_GAMEPAD_RIGHT_THUMBSTICK_RIGHT', 215: 'VK_GAMEPAD_RIGHT_THUMBSTICK_UP', 202: 'VK_GAMEPAD_RIGHT_TRIGGER', 208: 'VK_GAMEPAD_VIEW', 197: 'VK_GAMEPAD_X', 198: 'VK_GAMEPAD_Y', 21: 'VK_KANA', 25: 'VK_KANJI', 47: 'VK_HELP', 36: 'VK_HOME', 228: 'VK_ICO_00', 230: 'VK_ICO_CLEAR', 227: 'VK_ICO_HELP', 45: 'VK_INSERT', 23: 'VK_JUNJA', 182: 'VK_LAUNCH_APP1', 183: 'VK_LAUNCH_APP2', 180: 'VK_LAUNCH_MAIL', 181: 'VK_LAUNCH_MEDIA_SELECT', 1: 'VK_LBUTTON', 162: 'VK_LCONTROL', 37: 'VK_LEFT', 164: 'VK_LMENU', 160: 'VK_LSHIFT', 91: 'VK_LWIN', 4: 'VK_MBUTTON', 176: 'VK_MEDIA_NEXT_TRACK', 179: 'VK_MEDIA_PLAY_PAUSE', 177: 'VK_MEDIA_PREV_TRACK', 178: 'VK_MEDIA_STOP', 18: 'VK_MENU', 31: 'VK_MODECHANGE', 106: 'VK_MULTIPLY', 142: 'VK_NAVIGATION_ACCEPT', 143: 'VK_NAVIGATION_CANCEL', 139: 'VK_NAVIGATION_DOWN', 140: 'VK_NAVIGATION_LEFT', 137: 'VK_NAVIGATION_MENU', 141: 'VK_NAVIGATION_RIGHT', 138: 'VK_NAVIGATION_UP', 136: 'VK_NAVIGATION_VIEW', 34: 'VK_NEXT', 252: 'VK_NONAME', 29: 'VK_NONCONVERT', 144: 'VK_NUMLOCK', 96: 'VK_NUMPAD0', 97: 'VK_NUMPAD1', 98: 'VK_NUMPAD2', 99: 'VK_NUMPAD3', 100: 'VK_NUMPAD4', 101: 'VK_NUMPAD5', 102: 'VK_NUMPAD6', 103: 'VK_NUMPAD7', 104: 'VK_NUMPAD8', 105: 'VK_NUMPAD9', 186: 'VK_OEM_1', 226: 'VK_OEM_102', 191: 'VK_OEM_2', 192: 'VK_OEM_3', 219: 'VK_OEM_4', 220: 'VK_OEM_5', 221: 'VK_OEM_6', 222: 'VK_OEM_7', 223: 'VK_OEM_8', 240: 'VK_OEM_ATTN', 243: 'VK_OEM_AUTO', 225: 'VK_OEM_AX', 245: 'VK_OEM_BACKTAB', 254: 'VK_OEM_CLEAR', 188: 'VK_OEM_COMMA', 242: 'VK_OEM_COPY', 239: 'VK_OEM_CUSEL', 244: 'VK_OEM_ENLW', 241: 'VK_OEM_FINISH', 146: 'VK_OEM_NEC_EQUAL', 149: 'VK_OEM_FJ_LOYA', 147: 'VK_OEM_FJ_MASSHOU', 150: 'VK_OEM_FJ_ROYA', 148: 'VK_OEM_FJ_TOUROKU', 234: 'VK_OEM_JUMP', 189: 'VK_OEM_MINUS', 235: 'VK_OEM_PA1', 236: 'VK_OEM_PA2', 237: 'VK_OEM_PA3', 190: 'VK_OEM_PERIOD', 187: 'VK_OEM_PLUS', 233: 'VK_OEM_RESET', 238: 'VK_OEM_WSCTRL', 253: 'VK_PA1', 231: 'VK_PACKET', 19: 'VK_PAUSE', 250: 'VK_PLAY', 42: 'VK_PRINT', 33: 'VK_PRIOR', 229: 'VK_PROCESSKEY', 2: 'VK_RBUTTON', 163: 'VK_RCONTROL', 13: 'VK_RETURN', 39: 'VK_RIGHT', 165: 'VK_RMENU', 161: 'VK_RSHIFT', 92: 'VK_RWIN', 145: 'VK_SCROLL', 41: 'VK_SELECT', 108: 'VK_SEPARATOR', 16: 'VK_SHIFT', 95: 'VK_SLEEP', 44: 'VK_SNAPSHOT', 32: 'VK_SPACE', 109: 'VK_SUBTRACT', 9: 'VK_TAB', 38: 'VK_UP', 174: 'VK_VOLUME_DOWN', 173: 'VK_VOLUME_MUTE', 175: 'VK_VOLUME_UP', 5: 'VK_XBUTTON1', 6: 'VK_XBUTTON2', 251: 'VK_ZOOM'}


                
VK_LBUTTON        =0x01
VK_RBUTTON        =0x02
VK_CANCEL         =0x03
VK_MBUTTON        =0x04    #/* NOT contiguous with L & RBUTTON */

VK_XBUTTON1       =0x05    #/* NOT contiguous with L & RBUTTON */
VK_XBUTTON2       =0x06    #/* NOT contiguous with L & RBUTTON */



VK_BACK           =0x08
VK_TAB            =0x09


VK_CLEAR          =0x0C
VK_RETURN         =0x0D

VK_SHIFT          =0x10
VK_CONTROL        =0x11
VK_MENU           =0x12
VK_PAUSE          =0x13
VK_CAPITAL        =0x14

VK_KANA           =0x15
VK_HANGEUL        =0x15  #/* old name - should be here for compatibility */
VK_HANGUL         =0x15


VK_JUNJA          =0x17
VK_FINAL          =0x18
VK_HANJA          =0x19
VK_KANJI          =0x19


VK_ESCAPE         =0x1B

VK_CONVERT        =0x1C
VK_NONCONVERT     =0x1D
VK_ACCEPT         =0x1E
VK_MODECHANGE     =0x1F

VK_SPACE          =0x20
VK_PRIOR          =0x21
VK_NEXT           =0x22
VK_END            =0x23
VK_HOME           =0x24
VK_LEFT           =0x25
VK_UP             =0x26
VK_RIGHT          =0x27
VK_DOWN           =0x28
VK_SELECT         =0x29
VK_PRINT          =0x2A
VK_EXECUTE        =0x2B
VK_SNAPSHOT       =0x2C
VK_INSERT         =0x2D
VK_DELETE         =0x2E
VK_HELP           =0x2F


VK_LWIN           =0x5B
VK_RWIN           =0x5C
VK_APPS           =0x5D


VK_SLEEP          =0x5F

VK_NUMPAD0        =0x60
VK_NUMPAD1        =0x61
VK_NUMPAD2        =0x62
VK_NUMPAD3        =0x63
VK_NUMPAD4        =0x64
VK_NUMPAD5        =0x65
VK_NUMPAD6        =0x66
VK_NUMPAD7        =0x67
VK_NUMPAD8        =0x68
VK_NUMPAD9        =0x69
VK_MULTIPLY       =0x6A
VK_ADD            =0x6B
VK_SEPARATOR      =0x6C
VK_SUBTRACT       =0x6D
VK_DECIMAL        =0x6E
VK_DIVIDE         =0x6F
VK_F1             =0x70
VK_F2             =0x71
VK_F3             =0x72
VK_F4             =0x73
VK_F5             =0x74
VK_F6             =0x75
VK_F7             =0x76
VK_F8             =0x77
VK_F9             =0x78
VK_F10            =0x79
VK_F11            =0x7A
VK_F12            =0x7B
VK_F13            =0x7C
VK_F14            =0x7D
VK_F15            =0x7E
VK_F16            =0x7F
VK_F17            =0x80
VK_F18            =0x81
VK_F19            =0x82
VK_F20            =0x83
VK_F21            =0x84
VK_F22            =0x85
VK_F23            =0x86
VK_F24            =0x87


VK_NAVIGATION_VIEW     =0x88 # reserved
VK_NAVIGATION_MENU     =0x89 # reserved
VK_NAVIGATION_UP       =0x8A # reserved
VK_NAVIGATION_DOWN     =0x8B # reserved
VK_NAVIGATION_LEFT     =0x8C # reserved
VK_NAVIGATION_RIGHT    =0x8D # reserved
VK_NAVIGATION_ACCEPT   =0x8E # reserved
VK_NAVIGATION_CANCEL   =0x8F # reserved


VK_NUMLOCK        =0x90
VK_SCROLL         =0x91

VK_OEM_NEC_EQUAL  =0x92   # '=' key on numpad

VK_OEM_FJ_JISHO   =0x92   # 'Dictionary' key
VK_OEM_FJ_MASSHOU =0x93   # 'Unregister word' key
VK_OEM_FJ_TOUROKU =0x94   # 'Register word' key
VK_OEM_FJ_LOYA    =0x95   # 'Left OYAYUBI' key
VK_OEM_FJ_ROYA    =0x96   # 'Right OYAYUBI' key

VK_LSHIFT         =0xA0
VK_RSHIFT         =0xA1
VK_LCONTROL       =0xA2
VK_RCONTROL       =0xA3
VK_LMENU          =0xA4
VK_RMENU          =0xA5

VK_BROWSER_BACK        =0xA6
VK_BROWSER_FORWARD     =0xA7
VK_BROWSER_REFRESH     =0xA8
VK_BROWSER_STOP        =0xA9
VK_BROWSER_SEARCH      =0xAA
VK_BROWSER_FAVORITES   =0xAB
VK_BROWSER_HOME        =0xAC

VK_VOLUME_MUTE         =0xAD
VK_VOLUME_DOWN         =0xAE
VK_VOLUME_UP           =0xAF
VK_MEDIA_NEXT_TRACK    =0xB0
VK_MEDIA_PREV_TRACK    =0xB1
VK_MEDIA_STOP          =0xB2
VK_MEDIA_PLAY_PAUSE    =0xB3
VK_LAUNCH_MAIL         =0xB4
VK_LAUNCH_MEDIA_SELECT =0xB5
VK_LAUNCH_APP1         =0xB6
VK_LAUNCH_APP2         =0xB7


VK_OEM_1          =0xBA   # ';:' for US
VK_OEM_PLUS       =0xBB   # '+' any country
VK_OEM_COMMA      =0xBC   # ',' any country
VK_OEM_MINUS      =0xBD   # '-' any country
VK_OEM_PERIOD     =0xBE   # '.' any country
VK_OEM_2          =0xBF   # '/?' for US
VK_OEM_3          =0xC0   # '`~' for US


VK_GAMEPAD_A                         =0xC3 # reserved
VK_GAMEPAD_B                         =0xC4 # reserved
VK_GAMEPAD_X                         =0xC5 # reserved
VK_GAMEPAD_Y                         =0xC6 # reserved
VK_GAMEPAD_RIGHT_SHOULDER            =0xC7 # reserved
VK_GAMEPAD_LEFT_SHOULDER             =0xC8 # reserved
VK_GAMEPAD_LEFT_TRIGGER              =0xC9 # reserved
VK_GAMEPAD_RIGHT_TRIGGER             =0xCA # reserved
VK_GAMEPAD_DPAD_UP                   =0xCB # reserved
VK_GAMEPAD_DPAD_DOWN                 =0xCC # reserved
VK_GAMEPAD_DPAD_LEFT                 =0xCD # reserved
VK_GAMEPAD_DPAD_RIGHT                =0xCE # reserved
VK_GAMEPAD_MENU                      =0xCF # reserved
VK_GAMEPAD_VIEW                      =0xD0 # reserved
VK_GAMEPAD_LEFT_THUMBSTICK_BUTTON    =0xD1 # reserved
VK_GAMEPAD_RIGHT_THUMBSTICK_BUTTON   =0xD2 # reserved
VK_GAMEPAD_LEFT_THUMBSTICK_UP        =0xD3 # reserved
VK_GAMEPAD_LEFT_THUMBSTICK_DOWN      =0xD4 # reserved
VK_GAMEPAD_LEFT_THUMBSTICK_RIGHT     =0xD5 # reserved
VK_GAMEPAD_LEFT_THUMBSTICK_LEFT      =0xD6 # reserved
VK_GAMEPAD_RIGHT_THUMBSTICK_UP       =0xD7 # reserved
VK_GAMEPAD_RIGHT_THUMBSTICK_DOWN     =0xD8 # reserved
VK_GAMEPAD_RIGHT_THUMBSTICK_RIGHT    =0xD9 # reserved
VK_GAMEPAD_RIGHT_THUMBSTICK_LEFT     =0xDA # reserved



VK_OEM_4          =0xDB  #  '[{' for US
VK_OEM_5          =0xDC  #  '\|' for US
VK_OEM_6          =0xDD  #  ']}' for US
VK_OEM_7          =0xDE  #  ''"' for US
VK_OEM_8          =0xDF

VK_OEM_AX         =0xE1  #  'AX' key on Japanese AX kbd
VK_OEM_102        =0xE2  #  "<>" or "\|" on RT 102-key kbd.
VK_ICO_HELP       =0xE3  #  Help key on ICO
VK_ICO_00         =0xE4  #  00 key on ICO

VK_PROCESSKEY     =0xE5


VK_ICO_CLEAR      =0xE6

VK_PACKET         =0xE7

VK_OEM_RESET      =0xE9
VK_OEM_JUMP       =0xEA
VK_OEM_PA1        =0xEB
VK_OEM_PA2        =0xEC
VK_OEM_PA3        =0xED
VK_OEM_WSCTRL     =0xEE
VK_OEM_CUSEL      =0xEF
VK_OEM_ATTN       =0xF0
VK_OEM_FINISH     =0xF1
VK_OEM_COPY       =0xF2
VK_OEM_AUTO       =0xF3
VK_OEM_ENLW       =0xF4
VK_OEM_BACKTAB    =0xF5

VK_ATTN           =0xF6
VK_CRSEL          =0xF7
VK_EXSEL          =0xF8
VK_EREOF          =0xF9
VK_PLAY           =0xFA
VK_ZOOM           =0xFB
VK_NONAME         =0xFC
VK_PA1            =0xFD
VK_OEM_CLEAR      =0xFE

class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long),
                ("y", ctypes.c_long)]

class MSLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [("pt", POINT),
                ("mouseData", wintypes.DWORD),
                ("flags", wintypes.DWORD),
                ("time", wintypes.DWORD),
                ("dwExtraInfo", ULONG_PTR)]

class KBDLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [("vkCode", wintypes.DWORD),
                ("scanCode", wintypes.DWORD),
                ("flags", wintypes.DWORD),
                ("time", wintypes.DWORD),
                ("dwExtraInfo", ULONG_PTR)]

def _LowLevelMouseProc(nCode, wParam, lParam, cbfunc):
    if wParam in (WM_XBUTTONDOWN, WM_XBUTTONUP): # X button changed state
        x = GET_HWORD(lParam.contents.mouseData)
        cbfunc(MouseEvent((lParam.contents.pt.x, lParam.contents.pt.y), wParam, lParam.contents.time, x))
        
    elif wParam == WM_MOUSEWHEEL: # used scrollwheel
        cbfunc(MouseEvent((lParam.contents.pt.x, lParam.contents.pt.y), wParam, lParam.contents.time, GET_HWORD(lParam.contents.mouseData) / WHEEL_DELTA))      
        
    else:
        cbfunc(MouseEvent((lParam.contents.pt.x, lParam.contents.pt.y), wParam, lParam.contents.time))
    return user32.CallNextHookEx(0, nCode, wParam, lParam)

def _LowLevelKeyboardProc(nCode, wParam, lParam, cbfunc):
    cbfunc(KeyboardEvent(wParam, lParam.contents.vkCode, lParam.contents.time))

    return user32.CallNextHookEx(0, nCode, wParam, lParam)

mouse_hook_func = None
keyboard_hook_func = None

mouse_hook = None
keyboard_hook = None


LLMouseProc = ctypes.CFUNCTYPE(LRESULT, ctypes.c_int, wintypes.WPARAM, ctypes.POINTER(MSLLHOOKSTRUCT))
LLKeyboardProc = ctypes.CFUNCTYPE(LRESULT, ctypes.c_int, wintypes.WPARAM, ctypes.POINTER(KBDLLHOOKSTRUCT))

def hook_mouse(func): # hook onto mouse event queue
    global mouse_hook_func, mouse_hook
    mouse_hook_func = LLMouseProc(lambda x, y, z: _LowLevelMouseProc(x, y, z, func))
    mouse_hook = user32.SetWindowsHookExA(WH_MOUSE_LL, mouse_hook_func, None, 0)

def hook_keyboard(func): # hook onto keyboard event queue
    global keyboard_hook_func, keyboard_hook
    keyboard_hook_func = LLKeyboardProc(lambda x, y, z: _LowLevelKeyboardProc(x, y, z, func))
    keyboard_hook = user32.SetWindowsHookExA(WH_KEYBOARD_LL, keyboard_hook_func, None, 0)
    
def wait_messages(): # enter message loop
    msg = wintypes.MSG()
    while user32.GetMessageA(ctypes.pointer(msg), None, 0, 0):
        pass

def stop(): # stop message loop
    user32.PostQuitMessage(0)

def unhook_mouse(): # remove hook from mouse event queue
    global mouse_hook
    user32.UnhookWindowsHookEx(mouse_hook)

def unhook_keyboard(): # remove hook from keyboard event queue
    global keyboard_hook
    user32.UnhookWindowsHookEx(keyboard_hook)
