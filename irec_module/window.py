from . import config, macro, util

import math, time, winput, re

try:
    import tkinter
    from tkinter import filedialog
    from tkinter import ttk

except ImportError: # Python 2
    try:
        import Tkinter as tkinter
        import ttk
        import tkFileDialog as filedialog
        
    except ImportError:
        raise ImportError("Tcl/Tk (tkinter) is not installed!")

class PlaceholderEntry(ttk.Entry):
    widget_id = 1
    def __init__(self, *args, placeholder = None, placeholder_color = "#aaaaaa", **kw):        
        self.style_name = "Placeholder{}.TEntry".format(id(self))
        kw["style"] = self.style_name
        
        super().__init__(*args, **kw)

        PlaceholderEntry.widget_id += 1

        self.fg = kw.get("fg", kw.get("foreground", "black"))

        self.is_placeholder = bool(placeholder)
        
        self.in_focus = False

        self.style = ttk.Style()

        self.placeholder_color = placeholder_color

        self.placeholder = placeholder

        self.bind("<FocusIn>", self.on_focus_in)
        

    def on_focus_in(self, e):
        self.in_focus = True
        
        self.bind("<FocusOut>", self.on_focus_out)
        self.unbind("<FocusIn>")
        
        if self.is_placeholder:
            self.bind("<Button-1>", self.on_click)
            self.bind("<KeyPress>", self.on_key_press)
            self.icursor(0)

    def on_focus_out(self, e):
        self.in_focus = False

        self.bind("<FocusIn>", self.on_focus_in)
        self.unbind("<FocusOut>")

        if not self.is_placeholder and self.get() == "":
            self.is_placeholder = True

            self.insert(tkinter.END, self.placeholder)
            self.style.configure(self.style_name, foreground = self.placeholder_color)
            

    def on_key_press(self, e):
        if self.is_placeholder:
            if e.keysym == "Right" or e.keysym == "End":
                return "break"
            if e.keysym in ("Control", "Shift", "Control_L", "Shift_L", "Control_R", "Shift_R"):
                return
            
            self.is_placeholder = False
            self.unbind("<Button-1>")
            self.unbind("<KeyPress>")
            self.style.configure(self.style_name, foreground = self.fg)
            self.delete(0, tkinter.END)
            

    def on_click(self, e):
        if self.is_placeholder:
            self.icursor(0)
            
            if self.in_focus:
                return "break"

    def get(self):
        if self.is_placeholder:
            return ""
        return super().get()

    @property
    def placeholder(self):
        return self._placeholder

    @placeholder.setter
    def placeholder(self, value):
        if value is None:
            if self.is_placeholder:
                self.delete(0, tkinter.END)
                self.style.configure(self.style_name, foreground = self.fg)
        
        else:
            assert type(value) == str

            if self.is_placeholder:
                self.delete(0, tkinter.END)
                self.insert(tkinter.END, value)
                self.style.configure(self.style_name, foreground = self.placeholder_color)
            
            self._placeholder = value

class EventExecutorDelayListEntry:
    def __init__(self, delay, event_executor):
        self.delay = delay
        self.event_executor = event_executor

    @property
    def text(self):
        return "{:>5d}ms delay".format(self.delay) if self.delay else "     no delay"

class EventExecutorListEntry:
    def __init__(self, event_executor):
        self.event_executor = event_executor

    @property
    def text(self):
        return str(self.event_executor.event)

    @property
    def time_offset(self):
        return self.event_executor.time_offset

    def get_delay(self, previous_time_offset):
        return EventExecutorDelayListEntry(int(round((self.time_offset - previous_time_offset) / 1000000, 0)), self.event_executor)

def macro_to_list_entries(mcr):
    event_executors = mcr.event_executor_list

    out = []

    if not event_executors:
        return out

    last_time_offset = 0
    
    for event_executor in event_executors:
        assert event_executor.time_offset >= last_time_offset
        event_executor_copy = event_executor.copy()
        eele = EventExecutorListEntry(event_executor_copy)
        delay = eele.get_delay(last_time_offset)
        last_time_offset = eele.time_offset
        
        out.append(delay)
        out.append(eele)

    return out

def update_macro_list_widget():
    global root, macro_list, macro_list_widget, selection

    macro_list_widget.delete(0, tkinter.END)

    for macro in macro_list:
        macro_list_widget.insert(tkinter.END, macro.name)

    selection = (macro_list_widget.size() - 1, )

    macro_list_widget.focus_set()

def start_countdown(macro_name, length):
    global root, macro_list

    root.withdraw()

    assert type(length) == int and length >= 0

    start_time = time.time()

    width, height = root.winfo_screenwidth(), root.winfo_screenheight()

    if length:
        countdown_window = tkinter.Toplevel(root)

        countdown_window.overrideredirect(True)

        countdown_window.geometry("{}x{}+{}+{}".format(500, 800, (width - 500) // 2, (height - 800) // 2))

        countdown_window.config(bg="#333334")

        countdown_window.wm_attributes('-transparentcolor', '#333334')
        
        countdown_window.wm_attributes('-topmost', True)

        black_label = tkinter.Label(countdown_window, text=str(length), bg='#333334', fg="#333333", font=("Consolas", 300), anchor=tkinter.CENTER)
        black_label.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)

        countdown_window.update()

        while True:
            diff = time.time() - start_time

            if diff >= length - 1./30.:
                break

            fract, int_part = math.modf(length + 1 - diff)

            int_part = int(int_part)

            font_size = max(int(300 * fract), 10)

            black_label.config(font=("Consolas", font_size), text=str(int_part))

            countdown_window.update()

        countdown_window.destroy()

        end_time = time.time()

        start_time += length

    macro_list.append(macro.create_macro(macro_name, start_time, width, height))

    update_macro_list_widget()

    root.deiconify()

def save_macros_dialog():
    global macro_list
    
    file_ = filedialog.asksaveasfile("wb", filetypes=[("Macro", "*.mcr"), ("All files", "*.*")], defaultextension="*.mcr")
    
    if file_ is None:
        return
    
    file_.write(macro.macros_to_bytes(*macro_list, compressionlevel=int(config.get("compression_level", "9"))))
    file_.close()

def load_macros_dialog():
    global macro_list

    file_ = filedialog.askopenfile("rb", filetypes=[("Macro", "*.mcr"), ("All files", "*.*")], defaultextension="*.mcr")
    
    if file_ is None:
        return
    
    macro_list = macro.macros_from_bytes(file_.read())
    file_.close()

    update_macro_list_widget()

def edit_macro_dialog(mcr):
    global root, cursor_showing, current_edit_frame, current_selection, rebind

    current_selection = None

    current_edit_frame = None

##    options = {"keyboard" : tkinter.IntVar(value=int(config.get("record_keyboard", True))),
##               "mouse": tkinter.IntVar(value=int(config.get("record_mouse", True))),
##               "countdown" : tkinter.IntVar(value=int(config.get("countdown", 3))),
##               "recording_stop_key" : config.get("recording_stop_key", winput.VK_ESCAPE),
##               "recording_duration" : tkinter.StringVar(value=(config.get("recording_duration", 3))),
##               "recording_mode" : tkinter.StringVar(value=config.get("recording_mode", "key"))}
##
##    options["keyboard"].trace("w", lambda *args: (config.set("record_keyboard", bool(options["keyboard"].get()))))
##    options["mouse"].trace("w", lambda *args: (config.set("record_mouse", bool(options["mouse"].get()))))
##    options["countdown"].trace("w", lambda *args: (config.set("countdown", int(options["countdown"].get()))))
##    options["recording_duration"].trace("w", lambda *args: (config.set("recording_duration", float(options["recording_duration"].get()) if (options["recording_duration"].get()) else "0")))
##    options["recording_mode"].trace("w", lambda *args: (config.set("recording_mode", (options["recording_mode"].get()))))

    root_x = root.winfo_x()
    root_y = root.winfo_y()

    root_width = root.winfo_width()
    root_height = root.winfo_height()

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    window_width = root_width
    window_height = root_height - 50

    window = tkinter.Toplevel(root)
    window.title("Edit")
    window.wm_attributes("-toolwindow", True)
    window.grab_set()
    window.focus_set()

    window.geometry("{}x{}+{}+{}".format(window_width, window_height, root_x + root_width // 2 - window_width // 2, root_y + root_height // 2 - window_height // 2))

    CURSOR_SIZE = 21

    CURSOR_WIDTH = 1

    BORDER_SIZE = 2
    
    cursor_preview_window = tkinter.Toplevel(window, bg="white")
    cursor_preview_window.overrideredirect(True)
    cursor_preview_window.geometry("{}x{}+{}+{}".format(CURSOR_SIZE, CURSOR_SIZE, 10, 10))
    cursor_preview_window.wm_attributes('-transparentcolor', 'white')
    cursor_preview_window.wm_attributes('-topmost', True)

    cursor_canvas = tkinter.Canvas(cursor_preview_window, width=CURSOR_SIZE + BORDER_SIZE * 2, height=CURSOR_SIZE + BORDER_SIZE * 2, bg="white")

    show_cursor_canvas = lambda: cursor_canvas.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)
    hide_cursor_canvas = lambda: cursor_canvas.place_forget()

    cursor_showing = False

    def show_cursor(relx, rely):
        global cursor_showing
        x = int(round(relx * screen_width, 0))
        y = int(round(rely * screen_height, 0))

        HALF_CURSOR_SIZE = CURSOR_SIZE // 2
        
        cursor_preview_window.geometry("+{}+{}".format(x - HALF_CURSOR_SIZE, y - HALF_CURSOR_SIZE))
        show_cursor_canvas()

        cursor_showing = True

    def hide_cursor():
        global cursor_showing
        cursor_showing = False
        hide_cursor_canvas()
    
    cursor_hline = cursor_canvas.create_line(BORDER_SIZE, BORDER_SIZE + CURSOR_SIZE // 2, BORDER_SIZE + CURSOR_SIZE, BORDER_SIZE + CURSOR_SIZE // 2, fill="#444", width = CURSOR_WIDTH)
    cursor_vline = cursor_canvas.create_line(BORDER_SIZE + CURSOR_SIZE // 2, BORDER_SIZE, BORDER_SIZE + CURSOR_SIZE // 2, BORDER_SIZE + CURSOR_SIZE, fill="#444", width = CURSOR_WIDTH)

    color_from_time = lambda: "#{0}{0}{0}".format(hex(int((time.time() % 1) * 16))[-1])

    def animate_cursor():
        color = color_from_time()
        cursor_canvas.itemconfig(cursor_hline, fill=color)
        cursor_canvas.itemconfig(cursor_vline, fill=color)

    frame = tkinter.Frame(window)
    frame.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)

    PADX = PADY = 5

    list_entries = macro_to_list_entries(mcr)

    macro_list_widget = tkinter.Listbox(frame, width=40, height=22, font=("Consolas", 12))
    macro_list_widget.grid(column=1, row=1, padx=PADX, pady=PADY, sticky=tkinter.N)

    top_pane = tkinter.Frame(frame)
    top_pane.grid(column=1, row=0)

    name_label = tkinter.Label(top_pane, text="Macro name:")
    name_label.grid(column=0, row=0, padx=PADX, pady=PADY)

    name_entry = ttk.Entry(top_pane)
    name_entry.grid(column=1, row=0, padx=PADX, pady=PADY)

    name_entry.insert(tkinter.END, mcr.name)

    left_pane = tkinter.Frame(frame, height=window_height - 100)
    left_pane.grid(column=0, row=1, sticky=tkinter.N)

    left_label = tkinter.Label(left_pane, text="Insert")
    left_label.grid(column=0, row=0, columnspan=2, padx=PADX, pady=PADY)

    insert_var = tkinter.IntVar()

    insert_var.set(0)

    insert_before_button = ttk.Radiobutton(left_pane, text="Before", value=0, variable=insert_var)
    insert_before_button.grid(column=0, row=1, sticky=tkinter.E, padx=PADX, pady=PADY)
    
    insert_after_button = ttk.Radiobutton(left_pane, text="After", value=1, variable=insert_var)
    insert_after_button.grid(column=1, row=1, sticky=tkinter.W, padx=PADX, pady=PADY)

    def insert_before(event):
        global current_selection

##        assert current_selection
        
        event_executor = macro.EventExecutor(-1, event)

        list_entry = EventExecutorListEntry(event_executor)
        delay_entry = EventExecutorDelayListEntry(0, event_executor)

        not_list_entries = not list_entries

        if not_list_entries:
            current_selection = 1

        list_entries.insert(current_selection - 1, list_entry)
        list_entries.insert(current_selection - 1, delay_entry)

        macro_list_widget.insert(current_selection - 1, list_entry.text)
        macro_list_widget.insert(current_selection - 1, delay_entry.text)

        current_selection += 2

        if not_list_entries:
            macro_list_widget.selection_set(0, 1)

            current_selection = 1

        macro_list_widget.focus_set()

    def insert_after(event):
        global current_selection

##        assert current_selection
        
        event_executor = macro.EventExecutor(-1, event)

        list_entry = EventExecutorListEntry(event_executor)
        delay_entry = EventExecutorDelayListEntry(0, event_executor)

        if not list_entries:
            current_selection = -1

        list_entries.insert(current_selection + 1, list_entry)
        list_entries.insert(current_selection + 1, delay_entry)

        macro_list_widget.insert(current_selection + 1, list_entry.text)
        macro_list_widget.insert(current_selection + 1, delay_entry.text)

        if current_selection == -1:
            macro_list_widget.selection_set(0, 1)
            current_selection = 1

        macro_list_widget.focus_set()

    def insert(event):
        if int(insert_var.get()) == 0:
            insert_before(event)
        else:
            insert_after(event)

    add_set_mouse_position = ttk.Button(left_pane, text="Set Mouse Position", command=lambda: insert(macro.MousePositionEvent(mcr.config, 0, 0)))
    add_set_mouse_position.grid(column=0, row=2, columnspan=2, sticky=tkinter.W + tkinter.E, padx=PADX, pady=PADY)

    add_move_mousewheel = ttk.Button(left_pane, text="Move Mousewheel", command=lambda: insert(macro.MouseWheelMoveEvent(1)))
    add_move_mousewheel.grid(column=0, row=3, columnspan=2, sticky=tkinter.W + tkinter.E, padx=PADX, pady=PADY)

    add_press_mouse_button_label = tkinter.Label(left_pane, text="Press Mouse Button")
    add_press_mouse_button_label.grid(column=0, row=4, columnspan=2, padx=PADX, pady=PADY)

    add_press_mouse_button_frame = tkinter.Frame(left_pane)
    add_press_mouse_button_frame.grid(column=0, row=5, columnspan=2)

    add_press_left_mouse_button = ttk.Button(add_press_mouse_button_frame, text="Left", command=lambda: insert(macro.MouseButtonPressEvent(winput.LMB)))
    add_press_left_mouse_button.grid(row=0, column=0, padx=PADX, pady=PADY)

    add_press_middle_mouse_button = ttk.Button(add_press_mouse_button_frame, text="Middle", command=lambda: insert(macro.MouseButtonPressEvent(winput.MMB)))
    add_press_middle_mouse_button.grid(row=0, column=1, padx=PADX, pady=PADY)

    add_press_right_mouse_button = ttk.Button(add_press_mouse_button_frame, text="Right", command=lambda: insert(macro.MouseButtonPressEvent(winput.RMB)))
    add_press_right_mouse_button.grid(row=0, column=2, padx=PADX, pady=PADY)

    add_press_x1_mouse_button = ttk.Button(left_pane, text="X1", command=lambda: insert(macro.MouseButtonPressEvent(winput.XMB1)))
    add_press_x1_mouse_button.grid(column=0, row=6, sticky=tkinter.E, padx=PADX, pady=PADY)

    add_press_x2_mouse_button = ttk.Button(left_pane, text="X2", command=lambda: insert(macro.MouseButtonPressEvent(winput.XMB2)))
    add_press_x2_mouse_button.grid(column=1, row=6, sticky=tkinter.W, padx=PADX, pady=PADY)

    add_release_mouse_button_label = tkinter.Label(left_pane, text="Release Mouse Button")
    add_release_mouse_button_label.grid(column=0, row=7, columnspan=2, padx=PADX, pady=PADY)

    add_release_mouse_button_frame = tkinter.Frame(left_pane)
    add_release_mouse_button_frame.grid(column=0, row=8, columnspan=2)

    add_release_left_mouse_button = ttk.Button(add_release_mouse_button_frame, text="Left", command=lambda: insert(macro.MouseButtonReleaseEvent(winput.LMB)))
    add_release_left_mouse_button.grid(row=0, column=0, padx=PADX, pady=PADY)

    add_release_middle_mouse_button = ttk.Button(add_release_mouse_button_frame, text="Middle", command=lambda: insert(macro.MouseButtonReleaseEvent(winput.MMB)))
    add_release_middle_mouse_button.grid(row=0, column=1, padx=PADX, pady=PADY)

    add_release_right_mouse_button = ttk.Button(add_release_mouse_button_frame, text="Right", command=lambda: insert(macro.MouseButtonReleaseEvent(winput.RMB)))
    add_release_right_mouse_button.grid(row=0, column=2, padx=PADX, pady=PADY)

    add_release_x1_mouse_button = ttk.Button(left_pane, text="X1", command=lambda: insert(macro.MouseButtonReleaseEvent(winput.XMB1)))
    add_release_x1_mouse_button.grid(column=0, row=9, sticky=tkinter.E, padx=PADX, pady=PADY)

    add_release_x2_mouse_button = ttk.Button(left_pane, text="X2", command=lambda: insert(macro.MouseButtonReleaseEvent(winput.XMB2)))
    add_release_x2_mouse_button.grid(column=1, row=9, sticky=tkinter.W, padx=PADX, pady=PADY)

    add_keyboard_label = tkinter.Label(left_pane, text="Keyboard")
    add_keyboard_label.grid(column=0, row=10, columnspan=2, padx=PADX, pady=PADY)

    add_press_key = ttk.Button(left_pane, text="Press Key", command=lambda: insert(macro.KeyPressEvent(winput.VK_RETURN)))
    add_press_key.grid(column=0, row=11, columnspan=2, sticky=tkinter.W + tkinter.E, padx=PADX, pady=PADY)

    add_release_key = ttk.Button(left_pane, text="Release Key", command=lambda: insert(macro.KeyReleaseEvent(winput.VK_RETURN)))
    add_release_key.grid(column=0, row=12, columnspan=2, sticky=tkinter.W + tkinter.E, padx=PADX, pady=PADY)

    

    right_pane = tkinter.Frame(frame, height=window_height - 100)
    right_pane.grid(column=2, row=1, sticky=tkinter.N)

    right_label = tkinter.Label(right_pane, text="Edit")
    right_label.grid(column=0, row=0, columnspan=2, padx=PADX, pady=PADY)

    delay_label = tkinter.Label(right_pane, text="Delay:")
    delay_label.grid(column=0, row=1, padx=PADX, pady=PADY)

    delay_frame = tkinter.Frame(right_pane)
    delay_frame.grid(column=1, row=1, padx=PADX, pady=PADY)

    delay_variable = tkinter.IntVar()

    def update_delay(*args):
        global current_selection

        list_entries[current_selection - 1].delay = delay_variable.get()

        macro_list_widget.delete(current_selection - 1)
        macro_list_widget.insert(current_selection - 1, list_entries[current_selection - 1].text)
        macro_list_widget.selection_set(current_selection - 1)
        macro_list_widget.activate(current_selection)
        macro_list_widget.see(current_selection - 1)
        macro_list_widget.see(current_selection)
        

    def delay_validate_cmd(text):
        if text == "":
            delay_variable.set(0)
            return False
        
        try:
            i = int(text)
            if text.startswith("0"):
                delay_variable.set(int(text))
                return False
            return i >= 0 and not "-" in text
        except:
            return False

    delay_variable.trace("w", update_delay)

    registered_validator = root.register(delay_validate_cmd)

    delay_spinbox = ttk.Entry(delay_frame, width=10, textvariable=delay_variable, validate="all", validatecommand=(registered_validator, "%P"))
    delay_spinbox.grid(column=0, row=0)

    delay_unit_label = tkinter.Label(delay_frame, text="ms")
    delay_unit_label.grid(column=1, row=0)

    set_mouse_position_frame = tkinter.Frame(right_pane)
    move_mousewheel_frame = tkinter.Frame(right_pane)
    mouse_button_frame = tkinter.Frame(right_pane)
    key_frame = tkinter.Frame(right_pane)
    
    def show_edit_frame():
        global current_edit_frame
        
        current_edit_frame.grid(column=0, row=2, columnspan=2)

    def hide_edit_frame():
        global current_edit_frame
        
        if current_edit_frame:
            current_edit_frame.grid_forget()
            current_edit_frame = None

    x_coords_label = tkinter.Label(set_mouse_position_frame, text="X")
    x_coords_label.grid(row=0, column=0, padx=PADX, pady=PADY)

    y_coords_label = tkinter.Label(set_mouse_position_frame, text="Y")
    y_coords_label.grid(row=0, column=1, padx=PADX, pady=PADY)

    x_coords_var = tkinter.StringVar()

    y_coords_var = tkinter.StringVar()

    mousewheel_amount_var = tkinter.StringVar()

    mousewheel_horizontal_var = tkinter.StringVar()

    mouse_button_var = tkinter.StringVar()

    def update_cursor():
        global current_selection

        if not current_selection:
            return
        
        event_executor_list_entry = list_entries[current_selection]
        
        x, y = event_executor_list_entry.event_executor.event.rel_x, event_executor_list_entry.event_executor.event.rel_y
        show_cursor(x, y)

    def update_entry():
        macro_list_widget.delete(current_selection)
        macro_list_widget.insert(current_selection, list_entries[current_selection].text)
        macro_list_widget.selection_set(current_selection)
        macro_list_widget.activate(current_selection)
        macro_list_widget.see(current_selection - 1)
        macro_list_widget.see(current_selection )

    def update_x_coord(*args):
        global current_selection

        if not current_selection:
            return

        list_entries[current_selection].event_executor.event.rel_x = float(x_coords_var.get()) / 100.0

        update_cursor()

        update_entry()

    def update_y_coord(*args):
        global current_selection

        if not current_selection:
            return

        list_entries[current_selection].event_executor.event.rel_y = float(y_coords_var.get()) / 100.0

        update_cursor()

        update_entry()

    def update_mousewheel_amount(*args):
        global current_selection

        if not current_selection:
            return
        
        list_entries[current_selection].event_executor.event.amount = int(mousewheel_amount_var.get())

        update_entry()

    def update_mousewheel_horizontality(*args):
        global current_selection

        if not current_selection:
            return

        event_executor = list_entries[current_selection].event_executor
        
        if mousewheel_horizontal_var.get() == "horizontal":
            event_executor.event = macro.MouseWheelHorizontalMoveEvent(event_executor.event.amount)
            
        else:
            event_executor.event = macro.MouseWheelMoveEvent(event_executor.event.amount)

        update_entry()

    def update_mouse_button(*args):
        global current_selection

        if not current_selection:
            return

        event_executor = list_entries[current_selection].event_executor

        mouse_button_string = mouse_button_var.get()

        event_executor.event.mouse_button = winput.LMB if mouse_button_string == "Left" else \
                                            winput.RMB if mouse_button_string == "Right" else \
                                            winput.MMB if mouse_button_string == "Middle" else \
                                            winput.XMB1 if mouse_button_string == "X1" else \
                                            winput.XMB2

        update_entry()

    x_coords_var.trace("w", update_x_coord)
    
    y_coords_var.trace("w", update_y_coord)

    mousewheel_amount_var.trace("w", update_mousewheel_amount)

    mousewheel_horizontal_var.trace("w", update_mousewheel_horizontality)

    mouse_button_var.trace("w", update_mouse_button)

    def float_x_validate_cmd(text):
        if text == "":
            x_coords_var.set(0)
            return False
        if text in ("-", "0-"):
            x_coords_var.set("-0")
            return False
        if len(text) >= 2 and text[0] == "0" and not "." in text:
            x_coords_var.set(text[1:])
            return False
        try:
            float(text)
            return True
        except:
            return False

    def float_y_validate_cmd(text):
        if text == "":
            y_coords_var.set(0)
            return False
        if text in ("0-", "-0"):
            y_coords_var.set("-")
            return False
        if len(text) >= 2 and text[0] == "0" and not "." in text:
            y_coords_var.set(text[1:])
            return False
        try:
            float(text)
            return True
        except:
            return False

    registered_x_validator = root.register(float_x_validate_cmd)

    registered_y_validator = root.register(float_y_validate_cmd)

    x_coords_entry = ttk.Entry(set_mouse_position_frame, width=8, textvariable=x_coords_var, validate="all", validatecommand=(registered_x_validator, "%P"), justify=tkinter.RIGHT)
    x_coords_entry.grid(row=1, column=0, padx=PADX, pady=PADY)

    y_coords_entry = ttk.Entry(set_mouse_position_frame, width=8, textvariable=y_coords_var, validate="all", validatecommand=(registered_y_validator, "%P"), justify=tkinter.RIGHT)
    y_coords_entry.grid(row=1, column=1, padx=PADX, pady=PADY)

    def request_mouse_position():
        global current_selection

        root.iconify()

        window.iconify()

        root.update()
        
        pos_before = winput.get_mouse_pos()
        
        event_executor_list_entry = list_entries[current_selection]
        
        relx, rely = event_executor_list_entry.event_executor.event.rel_x, event_executor_list_entry.event_executor.event.rel_y
        
        x = int(round(relx * screen_width, 0))
        y = int(round(rely * screen_height, 0))
        
        winput.set_mouse_pos(x, y)
        
        x, y = macro.request_mouse_pos(1)

        relx = x / screen_width
        rely = y / screen_height

        x_coords_var.set("{:.2f}".format(relx * 100))
        y_coords_var.set("{:.2f}".format(rely * 100))

        winput.set_mouse_pos(*pos_before)

        root.deiconify()

        window.deiconify()
        
        macro_list_widget.focus_set()

        root.update()

    request_mouse_position_button = ttk.Button(set_mouse_position_frame, text="Change Position", command=request_mouse_position)
    request_mouse_position_button.grid(row=2, column=0, columnspan=2, padx=PADX, pady=PADY)


    mousewheel_amount_label = tkinter.Label(move_mousewheel_frame, text="Amount:")
    mousewheel_amount_label.grid(row=0, column=0, padx=PADX, pady=PADY)

    mousewheel_amount = ttk.Spinbox(move_mousewheel_frame, value=tuple(filter(bool, range(-100,101))), width=4, textvariable=mousewheel_amount_var)
    mousewheel_amount.grid(row=0, column=1, padx=PADX, pady=PADY)

    mousewheel_horizontal_radiobutton = ttk.Radiobutton(move_mousewheel_frame, text="Horizontal", value="horizontal", variable=mousewheel_horizontal_var)
    mousewheel_horizontal_radiobutton.grid(row=1, column=0, pady=PADY)

    mousewheel_vertical_radiobutton = ttk.Radiobutton(move_mousewheel_frame, text="Vertical", value="vertical", variable=mousewheel_horizontal_var)
    mousewheel_vertical_radiobutton.grid(row=1, column=1, pady=PADY)


    mouse_button_selection_label = tkinter.Label(mouse_button_frame, text="Button:")
    mouse_button_selection_label.grid(row=0, column=0, padx=PADX, pady=PADY)

    mouse_button_selection = ttk.OptionMenu(mouse_button_frame, mouse_button_var, "Left", "Left", "Middle", "Right", "X1", "X2")
    mouse_button_selection.grid(row=0, column=1, padx=PADX, pady=PADY)

    def create_mouse_release_after():
        global current_selection

        assert current_selection

        mouse_release = macro.MouseButtonReleaseEvent(list_entries[current_selection].event_executor.event.mouse_button)

        event_executor = macro.EventExecutor(-1, mouse_release)

        list_entry = EventExecutorListEntry(event_executor)

        delay_entry = EventExecutorDelayListEntry(0, event_executor)

        list_entries.insert(current_selection + 1, list_entry)
        list_entries.insert(current_selection + 1, delay_entry)

        macro_list_widget.insert(current_selection + 1, list_entry.text)
        macro_list_widget.insert(current_selection + 1, delay_entry.text)

        macro_list_widget.focus_set()

    def create_mouse_press_before():
        global current_selection

        assert current_selection

        mouse_press = macro.MouseButtonPressEvent(list_entries[current_selection].event_executor.event.mouse_button)

        event_executor = macro.EventExecutor(-1, mouse_press)

        list_entry = EventExecutorListEntry(event_executor)

        delay_entry = EventExecutorDelayListEntry(0, event_executor)

        list_entries.insert(current_selection - 1, list_entry)
        list_entries.insert(current_selection - 1, delay_entry)

        macro_list_widget.insert(current_selection - 1, list_entry.text)
        macro_list_widget.insert(current_selection - 1, delay_entry.text)

        current_selection += 2

        macro_list_widget.focus_set()

    def create_mouse_click_after():
        global current_selection

        assert current_selection

        mouse_press = macro.MouseButtonPressEvent(list_entries[current_selection].event_executor.event.mouse_button)
        mouse_release = macro.MouseButtonReleaseEvent(list_entries[current_selection].event_executor.event.mouse_button)

        press_event_executor = macro.EventExecutor(-1, mouse_press)
        release_event_executor = macro.EventExecutor(-1, mouse_release)

        press_list_entry = EventExecutorListEntry(press_event_executor)
        release_list_entry = EventExecutorListEntry(release_event_executor)

        press_delay_entry = EventExecutorDelayListEntry(0, press_event_executor)
        release_delay_entry = EventExecutorDelayListEntry(0, release_event_executor)

        list_entries.insert(current_selection + 1, release_list_entry)
        list_entries.insert(current_selection + 1, release_delay_entry)
        list_entries.insert(current_selection + 1, press_list_entry)
        list_entries.insert(current_selection + 1, press_delay_entry)

        macro_list_widget.insert(current_selection + 1, release_list_entry.text)
        macro_list_widget.insert(current_selection + 1, release_delay_entry.text)
        macro_list_widget.insert(current_selection + 1, press_list_entry.text)
        macro_list_widget.insert(current_selection + 1, press_delay_entry.text)

        macro_list_widget.focus_set()

    mouse_button_create_release_after = ttk.Button(mouse_button_frame, text="Create release after", width=20, command=create_mouse_release_after)
    mouse_button_create_release_after.grid(row=1, column=0, columnspan=2, padx=PADX, pady=PADY)

    mouse_button_create_press_before = ttk.Button(mouse_button_frame, text="Create press before", width=20, command=create_mouse_press_before)
    mouse_button_create_press_before.grid(row=2, column=0, columnspan=2, padx=PADX, pady=PADY)

    mouse_button_create_click_after = ttk.Button(mouse_button_frame, text="Create click after", width=20, command=create_mouse_click_after)
    mouse_button_create_click_after.grid(row=3, column=0, columnspan=2, padx=PADX, pady=PADY)


    key_selection_label = tkinter.Label(key_frame, text="Key:")
    key_selection_label.grid(row=0, column=0, padx=PADX, pady=PADY)

    key_selection = ttk.Button(key_frame, text="Key")
    key_selection.grid(row=0, column=1, padx=PADX, pady=PADY)

    def get_new_key():
        global current_selection, rebind

        assert current_selection
        
        key_selection.config(text="Press a Key...", state=tkinter.DISABLED)
        
        bound_id = {}

        def unbind_and_break(sym):
            print(sym)
            macro_list_widget.unbind(sym)
            del bound_id[sym]
            return "break"

        macro_list_widget.focus_set()

        bind_key = lambda sym: bound_id.__setitem__(sym, macro_list_widget.bind(sym, lambda e: unbind_and_break(sym)))

        bind_key("<Key>")
        bind_key("<Delete>")
        bind_key("<Up>")

##        bound_id = macro_list_widget.bind("<Key>", unbind_and_break)
##        bound_id = macro_list_widget.bind("<Delete>", unbind_and_break)
##        bound_id = macro_list_widget.bind("<Up>", unbind_and_break)

##        key_selection.focus_set()
        
        window.update()

        requested_key = macro.request_key(5)

        if requested_key:
            list_entries[current_selection].event_executor.event.vk_code = requested_key

        key_selection.config(text=util.vk_code_to_key_name(list_entries[current_selection].event_executor.event.vk_code), state=tkinter.NORMAL)

        update_entry()
        
        window.update()

        for sym in bound_id:
            macro_list_widget.unbind(sym)

        rebind()

    key_selection.config(command=get_new_key)

    def string_to_vk_code(text):
        if not type(text) == str:
            return None
        
        if text.startswith("VK_"):
            return getattr(winput, text, None)

        if text.startswith("0x"):
            try:
                num = int(text, 16)
                if 1 <= num <= 0xFE:
                    return num
                
            except ValueError:
                pass

            return None

        try:
            num = int(text)
            if 10 <= num <= 0xFE:
                return num
                
        except ValueError:
            pass

        return string_to_vk_code("VK_" + text.replace(" ", "_").upper())

    def from_vk_code():
        vk_code = string_to_vk_code(root.clipboard_get())

        if not vk_code:
            dialog_return = tkinter.StringVar()
            
            vk_code_dialog = tkinter.Toplevel(window)
            vk_code_dialog.title("From VK-Code")

            width = 250
            height = 100

            vk_code_dialog.geometry("{}x{}+{}+{}".format(width, height, window.winfo_x() + (window.winfo_width() // 2 - width // 2), window.winfo_y() + (window.winfo_height() // 2 - height // 2)))

            title_label = tkinter.Label(vk_code_dialog, text="Enter the virutal key code (string, hex or int):")
            title_label.grid(column=0, row=0, columnspan=2, padx=PADX, pady=PADY)

            entry = ttk.Entry(vk_code_dialog)
            entry.grid(column=0, row=1, columnspan=2, sticky=tkinter.W + tkinter.E, padx=PADX, pady=PADY)

            cancel_button = ttk.Button(vk_code_dialog, text="Cancel", command=lambda: (vk_code_dialog.grab_release(), vk_code_dialog.destroy()))
            cancel_button.grid(column=0, row=2, padx=PADX, pady=PADY)

            ok_button = ttk.Button(vk_code_dialog, text="OK", command=lambda: (dialog_return.set(entry.get()), vk_code_dialog.grab_release(), vk_code_dialog.destroy()))
            ok_button.grid(column=1, row=2, padx=PADX, pady=PADY)

            window.grab_release()

            vk_code_dialog.grab_set()

            entry.focus_set()

            entry.bind("<Return>", lambda e: (dialog_return.set(entry.get()), vk_code_dialog.grab_release(), vk_code_dialog.destroy()))

            while True:
                try:
                    if vk_code_dialog.winfo_exists():
                        vk_code_dialog.update()
                    else:
                        break
                except:
                    break

            window.grab_set()

            vk_code = string_to_vk_code(dialog_return.get())

        if vk_code:
            list_entries[current_selection].event_executor.event.vk_code = vk_code

            key_selection.config(text=util.vk_code_to_key_name(list_entries[current_selection].event_executor.event.vk_code))

            update_entry()

        macro_list_widget.focus_set()

    key_from_vk_code = ttk.Button(key_frame, text="From VK-Code", width=20, command=from_vk_code)
    key_from_vk_code.grid(row=1, column=0, columnspan=2, padx=PADX, pady=PADY)

    def create_key_release_after():
        global current_selection

        assert current_selection

        key_release = macro.KeyReleaseEvent(list_entries[current_selection].event_executor.event.vk_code)

        event_executor = macro.EventExecutor(-1, key_release)

        list_entry = EventExecutorListEntry(event_executor)

        delay_entry = EventExecutorDelayListEntry(0, event_executor)

        list_entries.insert(current_selection + 1, list_entry)
        list_entries.insert(current_selection + 1, delay_entry)

        macro_list_widget.insert(current_selection + 1, list_entry.text)
        macro_list_widget.insert(current_selection + 1, delay_entry.text)

        macro_list_widget.focus_set()

    def create_key_press_before():
        global current_selection

        assert current_selection

        key_press = macro.KeyPressEvent(list_entries[current_selection].event_executor.event.vk_code)

        event_executor = macro.EventExecutor(-1, key_press)

        list_entry = EventExecutorListEntry(event_executor)

        delay_entry = EventExecutorDelayListEntry(0, event_executor)

        list_entries.insert(current_selection - 1, list_entry)
        list_entries.insert(current_selection - 1, delay_entry)

        macro_list_widget.insert(current_selection - 1, list_entry.text)
        macro_list_widget.insert(current_selection - 1, delay_entry.text)

        current_selection += 2

        macro_list_widget.focus_set()

    def create_key_click_after():
        global current_selection

        assert current_selection

        key_press = macro.KeyPressEvent(list_entries[current_selection].event_executor.event.vk_code)
        key_release = macro.KeyReleaseEvent(list_entries[current_selection].event_executor.event.vk_code)

        press_event_executor = macro.EventExecutor(-1, key_press)
        release_event_executor = macro.EventExecutor(-1, key_release)

        press_list_entry = EventExecutorListEntry(press_event_executor)
        release_list_entry = EventExecutorListEntry(release_event_executor)

        press_delay_entry = EventExecutorDelayListEntry(0, press_event_executor)
        release_delay_entry = EventExecutorDelayListEntry(0, release_event_executor)

        list_entries.insert(current_selection + 1, release_list_entry)
        list_entries.insert(current_selection + 1, release_delay_entry)
        list_entries.insert(current_selection + 1, press_list_entry)
        list_entries.insert(current_selection + 1, press_delay_entry)

        macro_list_widget.insert(current_selection + 1, release_list_entry.text)
        macro_list_widget.insert(current_selection + 1, release_delay_entry.text)
        macro_list_widget.insert(current_selection + 1, press_list_entry.text)
        macro_list_widget.insert(current_selection + 1, press_delay_entry.text)

        macro_list_widget.focus_set()

    key_create_release_after = ttk.Button(key_frame, text="Create release after", width=20, command=create_key_release_after)
    key_create_release_after.grid(row=2, column=0, columnspan=2, padx=PADX, pady=PADY)

    key_create_press_before = ttk.Button(key_frame, text="Create press before", width=20, command=create_key_press_before)
    key_create_press_before.grid(row=3, column=0, columnspan=2, padx=PADX, pady=PADY)

    key_create_click_after = ttk.Button(key_frame, text="Create click after", width=20, command=create_key_click_after)
    key_create_click_after.grid(row=4, column=0, columnspan=2, padx=PADX, pady=PADY)


    bottom_pane = tkinter.Frame(frame)
    bottom_pane.grid(column=1, row=2)

    def cancel():
        window.grab_release()

        window.destroy()

    def save():
        global macro_list
        
        event_executor_list = []

        time_offset = 0

        for list_entry in list_entries:
            if isinstance(list_entry, EventExecutorDelayListEntry):
                time_offset += list_entry.delay * 1000000
            else:
                assert isinstance(list_entry, EventExecutorListEntry)
                
                event_executor = list_entry.event_executor
                event_executor.time_offset = time_offset
                event_executor_list.append(event_executor)

        mcr.event_executor_list = event_executor_list

        mcr.name = name_entry.get() or ("Unnamed Macro {}".format(len(macro_list)))

        window.grab_release()

        window.destroy()

    button_cancel = ttk.Button(bottom_pane, text="Cancel", command=cancel)
    button_cancel.grid(column=0, row=0, padx=PADX, pady=PADY)

    button_save = ttk.Button(bottom_pane, text="Save", command=save)
    button_save.grid(column=1, row=0, padx=PADX, pady=PADY)

    def on_select(e):
        global cursor_showing, current_selection, current_edit_frame

        if not macro_list_widget.curselection():
            macro_list_widget.selection_set(current_selection)
            macro_list_widget.selection_set(current_selection - 1)
            macro_list_widget.activate(current_selection)
            return
        
        curselection = macro_list_widget.curselection()[0]
        
        event_executor_list_entry = list_entries[curselection]
        
        if isinstance(event_executor_list_entry, EventExecutorDelayListEntry):
            event_executor_list_entry = list_entries[curselection + 1]
            macro_list_widget.selection_set(curselection + 1)
            macro_list_widget.activate(curselection + 1)

            current_selection = curselection + 1

            macro_list_widget.see(curselection + 1)
        else:
            macro_list_widget.selection_set(curselection - 1)
            macro_list_widget.activate(curselection)

            current_selection = curselection

            macro_list_widget.see(curselection - 1)

        delay_list_entry = list_entries[current_selection - 1]

        delay_variable.set(delay_list_entry.delay)

        hide_edit_frame()
        
        if cursor_showing:
            hide_cursor()

        event = event_executor_list_entry.event_executor.event

        if isinstance(event, macro.MousePositionEvent):
            x, y = event.rel_x, event.rel_y
            show_cursor(x, y)

            current_edit_frame = set_mouse_position_frame

            show_edit_frame()
            
            x_coords_var.set("{:.2f}".format(x * 100))
            y_coords_var.set("{:.2f}".format(y * 100))
            return

        if isinstance(event, macro.MouseWheelEvent):
            mousewheel_amount_var.set(event.amount)

            mousewheel_horizontal_var.set("vertical" if isinstance(event, macro.MouseWheelMoveEvent) else "horizontal")

            current_edit_frame = move_mousewheel_frame

            show_edit_frame()
            return

        if isinstance(event, macro.MouseButtonEvent):
            mouse_button_var.set(util.mouse_button_to_name(event.mouse_button))

            current_edit_frame = mouse_button_frame

            show_edit_frame()
            return

        if isinstance(event, macro.KeyEvent):
            key_selection.config(text=util.vk_code_to_key_name(list_entries[current_selection].event_executor.event.vk_code))

            current_edit_frame = key_frame

            show_edit_frame()
            return

    def delete_event(e):
        global current_selection

        if current_selection and list_entries:
            del list_entries[current_selection]
            del list_entries[current_selection - 1]

            macro_list_widget.delete(current_selection - 1, current_selection)

            active = macro_list_widget.index(tkinter.ACTIVE)

            print(active)
            
            if active < current_selection - 1:
                current_selection = active

            macro_list_widget.selection_set(current_selection - 1, current_selection)
            macro_list_widget.activate(current_selection)

            if list_entries:
                on_select(None)
            else:
                current_selection = None
                hide_edit_frame()
                if cursor_showing:
                    hide_cursor()

    def rebind_func():
        macro_list_widget.bind("<<ListboxSelect>>", on_select)
        macro_list_widget.bind("<Delete>", delete_event)
        macro_list_widget.bind("<ButtonRelease-1>", lambda e: "break")
        macro_list_widget.bind("<Up>", lambda e: macro_list_widget.activate(macro_list_widget.index(tkinter.ACTIVE) - 1))

    rebind = rebind_func

    rebind()

    for list_entry in list_entries:
        macro_list_widget.insert(tkinter.END, list_entry.text)

    while 1:
        try:
            if cursor_showing:
                animate_cursor()
            window.update()
            if not window.winfo_exists():
                break
        except:
            break

def record_macro_dialog():
    global root

    options = {"keyboard" : tkinter.IntVar(value=int(config.get("record_keyboard", True))),
               "mouse": tkinter.IntVar(value=int(config.get("record_mouse", True))),
               "countdown" : tkinter.IntVar(value=int(config.get("countdown", 3))),
               "recording_stop_key" : config.get("recording_stop_key", winput.VK_ESCAPE),
               "recording_duration" : tkinter.StringVar(value=(config.get("recording_duration", 3))),
               "recording_mode" : tkinter.StringVar(value=config.get("recording_mode", "key"))}

    options["keyboard"].trace("w", lambda *args: (config.set("record_keyboard", bool(options["keyboard"].get()))))
    options["mouse"].trace("w", lambda *args: (config.set("record_mouse", bool(options["mouse"].get()))))
    options["countdown"].trace("w", lambda *args: (config.set("countdown", int(options["countdown"].get()))))
    options["recording_duration"].trace("w", lambda *args: (config.set("recording_duration", float(options["recording_duration"].get()) if (options["recording_duration"].get()) else "0")))
    options["recording_mode"].trace("w", lambda *args: (config.set("recording_mode", (options["recording_mode"].get()))))

    root_x = root.winfo_x()
    root_y = root.winfo_y()

    root_width = root.winfo_width()
    root_height = root.winfo_height()

    window_width = 400
    window_height = 250

    window = tkinter.Toplevel(root)
    window.title("Record")
    window.wm_attributes("-toolwindow", True)
    window.grab_set()
    window.focus_set()

    window.geometry("{}x{}+{}+{}".format(window_width, window_height, root_x + root_width // 2 - window_width // 2, root_y + root_height // 2 - window_height // 2))

    frame = tkinter.Frame(window)
    frame.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)

    PADX = PADY = 5

    macro_name_entry = PlaceholderEntry(frame, placeholder="Macro name")
    macro_name_entry.grid(column=0, columnspan=4, row=0, sticky=tkinter.W + tkinter.E, padx=PADX, pady=PADY)

    checkbuttonMouse = ttk.Checkbutton(frame, text="Record Mouse", variable = options["mouse"])
    checkbuttonMouse.grid(row=1,column=2, columnspan=2, sticky=tkinter.W, padx=PADX, pady=PADY)

    checkbuttonKeyboard = ttk.Checkbutton(frame, text="Record Keyboard", variable = options["keyboard"])
    checkbuttonKeyboard.grid(row=1,column=0, columnspan=2, padx=PADX, pady=PADY)

    countdown_label = tkinter.Label(frame, text="Countdown (in seconds):")
    countdown_label.grid(column=0, row=2, columnspan=2, sticky=tkinter.E, padx=PADX, pady=PADY)

    countdown_spinbox = ttk.Spinbox(frame, from_=0, to=10, width=3, textvariable = options["countdown"])
    countdown_spinbox.grid(column=2, row=2, columnspan=2, sticky=tkinter.W, padx=PADX, pady=PADY)

    radiobutton_descr_label = tkinter.Label(frame, text="Stop recording by:")
    radiobutton_descr_label.grid(row=3, column=0, columnspan=2, sticky=tkinter.E, padx=PADX, pady=PADY)

    label_stop_recording_key = tkinter.Label(frame, text="Key:")
    label_stop_recording_key.grid(row=4, column=0, sticky=tkinter.E, padx=PADX, pady=PADY)

    button_stop_recording_key = ttk.Button(frame, text=util.vk_code_to_key_name(options["recording_stop_key"]))
    button_stop_recording_key.grid(row=4, column=1, sticky=tkinter.W, padx=PADX, pady=PADY)

    def get_new_stop_recording_key():
        button_stop_recording_key.config(text="Press a Key...", state=tkinter.DISABLED)
        
        window.update()

        requested_key = macro.request_key(5)

        if requested_key:
            options["recording_stop_key"] = requested_key
            config.set("recording_stop_key", requested_key)

        button_stop_recording_key.config(text=util.vk_code_to_key_name(options["recording_stop_key"]), state=tkinter.NORMAL)
        
    button_stop_recording_key.config(command = get_new_stop_recording_key)

    label_time = tkinter.Label(frame, text="Duration (sec):")
    label_time.grid(row=4, column=2, sticky=tkinter.E, padx=PADX, pady=PADY)

    def float_validate_cmd(text):
        if text == "":
            options["recording_duration"].set(0)
            return False
        if len(text) >= 2 and text[0] == "0" and not "." in text:
            options["recording_duration"].set(text[1:])
            return False
        try:
            float(text)
            return True
        except:
            return False

    registered_validator = root.register(float_validate_cmd)

    duration_spinbox = ttk.Entry(frame, width=5, textvariable = options["recording_duration"], validate="all", validatecommand=(registered_validator, "%P"))
    duration_spinbox.grid(column=3, row=4, sticky=tkinter.W, padx=PADX, pady=PADY)

    radiobutton_stop_recording_key = ttk.Radiobutton(frame, text="Key", value="key", variable=options["recording_mode"], command=lambda: (button_stop_recording_key.config(state=tkinter.NORMAL), duration_spinbox.config(state=tkinter.DISABLED)))
    radiobutton_stop_recording_key.grid(column=2, row=3, sticky=tkinter.W, padx=PADX, pady=PADY)

    radiobutton_time = ttk.Radiobutton(frame, text="Timer", value="timer", variable=options["recording_mode"], command=lambda: (button_stop_recording_key.config(state=tkinter.DISABLED), duration_spinbox.config(state=tkinter.NORMAL)))
    radiobutton_time.grid(column=3, row=3, sticky=tkinter.W, padx=PADX, pady=PADY)

    def start_recording():
        global macro_list
        
        macro_name = macro_name_entry.get() or ("Unnamed Macro {}".format(len(macro_list)))
        window.grab_release()
        window.destroy()
        start_countdown(macro_name, options["countdown"].get())

    button_start = tkinter.Button(frame, text="Record", bg="#d11f45", fg="white", command=start_recording)
    button_start.grid(column=0, row=5, columnspan=4, sticky = tkinter.W + tkinter.E, padx=PADX, pady=PADY)

    button_cancel = ttk.Button(frame, text="Cancel", command=lambda: (window.grab_release(), window.destroy()))
    button_cancel.grid(column=0, row=6, columnspan=4, sticky = tkinter.W + tkinter.E, padx=PADX, pady=PADY)

    if options["recording_mode"].get() == "key":
        duration_spinbox.config(state=tkinter.DISABLED)
    else:
        button_stop_recording_key.config(state=tkinter.DISABLED)

def create_window():
    global root, macro_list, macro_list_widget, unnamed_macro_index, style, selection

    selection = ()

    unnamed_macro_index = 1

    macro_list = []
    
    root = tkinter.Tk()

    root.title("Irec - Input Recorder")

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    window_width = 800
    window_height = 600

    window_x = config.get("window_x", screen_width // 2 - window_width // 2)
    window_y = config.get("window_y", screen_height // 2 - window_height // 2)

    root.geometry("{}x{}+{}+{}".format(window_width, window_height, window_x, window_y))

    try: root.iconbitmap('Irec.ico')
    except: pass

    root.protocol("WM_DELETE_WINDOW", lambda: (config.set("window_x", root.winfo_x()), config.set("window_y", root.winfo_y()), root.destroy()))

    IPADX = 5
    IPADY = 10

    frame = tkinter.Frame(root)
    frame.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)

    macro_list_widget = tkinter.Listbox(frame, width=30, height=30)
    macro_list_widget.grid(column=0, row=0, rowspan=4, padx=50, pady=10)

    record_macro_button = ttk.Button(frame, text="Record macro", command=record_macro_dialog)
    record_macro_button.grid(column=1, row=0, padx=10, pady=10, ipadx=IPADX, ipady=IPADY)

    def create_macro():
        global selection
        mcr = macro.Macro("Unnamed Macro {}".format(len(macro_list)), macro.MacroConfig(screen_width, screen_height), [])
        edit_macro_dialog(mcr)
        macro_list.append(mcr)
        new_index = macro_list_widget.size()
        macro_list_widget.insert(tkinter.END, mcr.name)
        selection = (new_index,)
        macro_list_widget.focus_set()

    create_macro_button = ttk.Button(frame, text="Create macro", command=create_macro)
    create_macro_button.grid(column=2, row=0, padx=10, pady=10, ipadx=IPADX, ipady=IPADY)

    def edit_macro():
        selection = macro_list_widget.curselection()
        if selection:
            mcr = macro_list[selection[0]]
            edit_macro_dialog(mcr)
            macro_list_widget.delete(selection[0])
            macro_list_widget.insert(selection[0], mcr.name)
        macro_list_widget.focus_set()

    edit_macro_button = ttk.Button(frame, text="Edit macro", command=edit_macro, state=tkinter.DISABLED)
    edit_macro_button.grid(column=1, row=1, columnspan=2, padx=10, pady=10, ipadx=IPADX, ipady=IPADY)

    play_area = ttk.LabelFrame(frame, text="Play")
    play_area.grid(column=1, row=2, columnspan=2)

    repeat_label = tkinter.Label(play_area, text="Repeat:")
    repeat_label.grid(column=0, row=0, padx=10, pady=10)

    repeat_var = tkinter.StringVar()
    compression_level_var = tkinter.StringVar()

    def validate_repeat(text):
        if text == "":
            repeat_var.set("0")
            return False

        if len(text) > 1 and text.startswith("0"):
            repeat_var.set(text[1:])
            return False
        
        try:
            num = int(text)
            return 0 <= num <= 9999
        except:
            return False

    registered_validate_repeat = root.register(validate_repeat)

    repeat_spinbox = ttk.Spinbox(play_area, from_=0, to=9999, width=4, textvariable=repeat_var, validate="all", validatecommand=(registered_validate_repeat, "%P"))
    repeat_spinbox.grid(column=1, row=0, padx=10, pady=10)

    repeat_var.set("0")

    def play_macro():
        global selection
        if selection:
            root.withdraw()
            root.update()
            
            macro = macro_list[macro_list_widget.curselection()[0]]

            macro.config.screen_width = root.winfo_screenwidth()
            macro.config.screen_height = root.winfo_screenheight()
            
            for i in range(int(repeat_var.get()) + 1):
                macro.run()
                
            root.deiconify()
            root.update()

    play_macro_button = ttk.Button(play_area, text="Play macro", command=play_macro, state=tkinter.DISABLED)
    play_macro_button.grid(column=0, row=1, columnspan=2, padx=10, pady=10, ipadx=IPADX, ipady=IPADY)

    save_area = ttk.LabelFrame(frame, text="Save and Load")
    save_area.grid(column=1, row=3, columnspan=2)

    def validate_compression_level(text):
        if text == "":
            compression_level_var.set("0")
            return False

        if len(text) == 2 and text.startswith("0"):
            compression_level_var.set(text[1])
            return False
        
        try:
            num = int(text)
            return 0 <= num <= 9
        except:
            return False

    registered_validate_compression_level = root.register(validate_compression_level)

    compression_level_label = tkinter.Label(save_area, text="Compression level:")
    compression_level_label.grid(column=0, row=0, padx=10, pady=10, sticky=tkinter.E)

    compression_level_spinbox = ttk.Spinbox(save_area, from_=0, to=9, width=2, textvariable=compression_level_var, validate="all", validatecommand=(registered_validate_compression_level, "%P"))
    compression_level_spinbox.grid(column=1, row=0, padx=10, pady=10, sticky=tkinter.W)

    compression_level_var.set(config.get("compression_level", "9"))

    compression_level_var.trace("w", lambda *args: config.set("compression_level", compression_level_var.get()))

    save_macros_button = ttk.Button(save_area, text="Save macros", command=save_macros_dialog)
    save_macros_button.grid(column=0, row=1, padx=10, pady=10, ipadx=IPADX, ipady=IPADY)

    load_macros_button = ttk.Button(save_area, text="Load macros", command=load_macros_dialog)
    load_macros_button.grid(column=1, row=1, padx=10, pady=10, ipadx=IPADX, ipady=IPADY)

    def export_macro():
        global selection, macro_list       

        if selection:
            file_ = filedialog.asksaveasfile("wb", filetypes=[("Macro", "*.mcr"), ("All files", "*.*")], defaultextension="*.mcr")
        
            if file_ is None:
                return
            
            file_.write(macro.macros_to_bytes(macro_list[selection[0]], compressionlevel=int(config.get("compression_level", "9"))))
            file_.close()

    export_macro_button = ttk.Button(save_area, text="Export macro", state=tkinter.DISABLED, command=export_macro)
    export_macro_button.grid(column=0, row=2, columnspan=2, padx=10, pady=10, ipadx=IPADX, ipady=IPADY)

    def on_select(*e):
        global selection
        new_selection = macro_list_widget.curselection()

        if new_selection:
            selection = new_selection
            
            play_macro_button.config(state=tkinter.NORMAL)
            edit_macro_button.config(state=tkinter.NORMAL)
            export_macro_button.config(state=tkinter.NORMAL)
        else:
            play_macro_button.config(state=tkinter.DISABLED)
            edit_macro_button.config(state=tkinter.DISABLED)
            export_macro_button.config(state=tkinter.DISABLED)

    def do_select(*e):
        global selection

        if selection:
            macro_list_widget.selection_clear(0, tkinter.END)
            macro_list_widget.selection_set(selection)
            macro_list_widget.activate(selection[0])

        on_select()

    macro_list_widget.bind("<<ListboxSelect>>", on_select)
    macro_list_widget.bind("<FocusOut>", on_select)
    macro_list_widget.bind("<FocusIn>", do_select)

    

    root.mainloop()

create_window()
