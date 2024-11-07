import tkinter as tk


class PositionSwitch(tk.Frame):

    def __init__(self, parent, toplabel, label, bottomlabel, rightlabel, color, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.label_text = label

        self.toplabel_text = toplabel

        self.bottomlabel_text = bottomlabel

        self.rightlabel_text = rightlabel

        self.color = color

        self.state = "MID"

        # Frame to hold the switch and label together

        switch_frame = tk.Frame(self)

        switch_frame.pack(side="top")

        # Top label for the switch

        self.top_label = tk.Label(switch_frame, text=self.toplabel_text, justify="left")

        self.top_label.pack(side="top", padx=2, anchor="w")

        # Bottom label for the switch

        self.bottom_label = tk.Label(switch_frame, text=self.bottomlabel_text)

        self.bottom_label.pack(side="bottom", anchor="w")

        # Label for the switch, placed on the left

        self.label = tk.Label(switch_frame, text=self.label_text, justify="left")

        self.label.pack(side="left", padx=0, anchor="w")

        # Frame to hold the buttons vertically

        self.button_frame = tk.Frame(switch_frame)

        self.button_frame.pack(side="left", padx=1)

        # Thinner buttons representing the switch positions arranged vertically

        self.off_button = tk.Button(self.button_frame, text="", width=1, height=1, command=self.set_off)

        self.off_button.pack(pady=2)

        self.mid_button = tk.Button(self.button_frame, text="", width=1, height=1, command=self.set_mid)

        self.mid_button.pack(pady=2)

        self.on_button = tk.Button(self.button_frame, text="", width=1, height=1, command=self.set_on)

        self.on_button.pack(pady=2)

        # Initialize the button colors

        self.update_buttons()

    def set_off(self):
        self.state = "OFF"

        self.update_buttons()

    def set_mid(self):
        self.state = "MID"

        self.update_buttons()

    def set_on(self):
        self.state = "ON"

        self.update_buttons()

    def update_buttons(self):
        # Update the button colors to reflect the current state

        self.off_button.config(bg=self.color if self.state == "OFF" else "white")

        self.mid_button.config(bg=self.color if self.state == "MID" else "white")

        self.on_button.config(bg=self.color if self.state == "ON" else "white")


class CircularButton:

    def __init__(self, master, radius, color, command):
        self.master = master

        self.radius = radius

        self.command = command

        self.color = color

        # Create a Canvas to draw the button with no background

        self.canvas = tk.Canvas(master, width=2 * radius, height=2 * radius, bg='white', highlightthickness=0,
                                borderwidth=0)

        # Draw the circle

        self.circle = self.canvas.create_oval(0, 0, 2 * radius, 2 * radius, fill=self.color, outline='blue')

        # Bind mouse events

        self.canvas.bind("<Button-1>", self.on_click)

        self.canvas.bind("<Enter>", self.on_enter)

        self.canvas.bind("<Leave>", self.on_leave)

    def on_click(self, event):
        self.command()

    def on_enter(self, event):
        self.canvas.itemconfig(self.circle, fill='deepskyblue')

    def on_leave(self, event):
        self.canvas.itemconfig(self.circle, fill=self.color)

    def grid(self, row, column, padx=0, pady=0):
        self.canvas.grid(row=row, column=column, padx=padx, pady=pady)


def button_command(index):
    print(index)

    if index == 1:

        for i in range(1, 15):
            app.update_display(i, "  ", "grey")

    if index == 2:

        for i in range(1, 15):
            app.update_display(i, "0", "black")

    if index > 2:
        buttonentry(index)


def buttonentry(index):
    if index == 23:
        app.update_display(3, str(0), "black")

        app.update_display(4, str(0), "black")

        app.update_display(5, str(0), "black")

        app.update_display(6, str(0), "black")

        return

    if index == 37:
        app.update_display(7, str(0), "black")

        app.update_display(8, str(0), "black")

        app.update_display(9, str(0), "black")

        app.update_display(10, str(0), "black")

        return

    if index == 51:
        app.update_display(11, str(0), "black")

        app.update_display(12, str(0), "black")

        app.update_display(13, str(0), "black")

        app.update_display(14, str(0), "black")

        return

    if index > 23:
        index = index - 2

    if index > 37:
        index = index - 2

    displayindex = int((index - 2) / 3)  # hack to deal with 13 buttons (clear)

    print("displayindex", displayindex)

    modulo = (index - 2) % 3

    oldvalue = ("displayvalue", app.get_display(displayindex))[1]

    print("oldvalue", oldvalue)

    print("modulo", modulo)

    print("index", index)

    newvalue = oldvalue

    if oldvalue < "4" and ((modulo == 0) or (index == 37)):
        newvalue = str(int(oldvalue) + 4)

        print(oldvalue, modulo, index)

    if modulo == 2 and not (index == 37):

        decimal_number = int(oldvalue, 8)

        if not (decimal_number & 1):
            newvalue = str(int(oldvalue) + 1)

    if modulo == 1:

        decimal_number = int(oldvalue, 8)

        if not (decimal_number & (1 << 1)):
            newvalue = str(int(oldvalue) + 2)

    app.update_display(displayindex, str(newvalue), "black")


class SwitchApp(tk.Tk):

    def __init__(self):

        super().__init__()

        self.title("Position Switches")

        # Outer grid container

        outer_frame = tk.Frame(self)

        outer_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Dictionary to store references to display labels

        self.display_labels = {}

        # Display grid

        self.create_display_grid(outer_frame)

        # Button grid

        self.create_button_grid(outer_frame)

        # Switch and Circular Button grid

        self.create_switch_grid(outer_frame)

    def create_display_grid(self, outer_frame):

        display_frame = tk.Frame(outer_frame)

        display_frame.pack(side="top", fill="x")

        displays = [

            (0, "blank", 1, 1),

            (1, "STATUS", 1, 2),

            (2, "MCS MODE", 1, 3),

            (0, "blank", 1, 4),

            (3, "F", 1, 5),

            (4, "P", 2, 6),

            (5, "", 1, 7),

            (6, "S", 1, 8),

            (0, "blank", 1, 9),

            (7, "BFR REG", 1, 10),

            (8, "A", 2, 11),

            (9, "", 1, 12),

            (10, "A'", 1, 13),

            (0, "blank", 1, 14),

            (11, "BFR INT", 1, 15),

            (12, "Z", 2, 16),

            (13, "", 1, 17),

            (14, "BFR EXIT", 1, 18)

        ]

        for index, (name, label, span, column) in enumerate(displays):

            if label != "blank":

                # Create and store reference to the display value label using numeric key

                display_value_label = tk.Label(display_frame, text="0", font=("Arial", 88), width=1, borderwidth=3,
                                               relief="groove", bg="black", fg="white")

                display_value_label.grid(row=1, column=column, padx=0, pady=0)

                self.display_labels[name] = display_value_label  # Store reference using the numeric name

                # Create and display the corresponding label (if available)

                button_label = tk.Label(display_frame, text=label)

                button_label.grid(row=2, column=column, columnspan=span, padx=0, pady=0)

            else:

                button_label = tk.Label(display_frame, text="       ")

                button_label.grid(row=2, column=column, padx=10, pady=0)

    @staticmethod
    def create_button_grid(outer_frame):

        button_frame = tk.Frame(outer_frame)

        button_frame.pack(side="top", fill="x")

        buttons = [

            ("red", "OFF", 1, 1),

            ("yellow", "ON", 1, 2),

            ("white", "TL", 1, 3),

            ("white", "BFR", 1, 4),

            ("white", "DIR", 1, 5),

            ("white", "IND", 1, 6),

            ("white", "REL", 1, 7),

            ("blank", "", 1, 8),

            ("lightblue", "11", 1, 9),

            ("lightblue", "10", 1, 10),

            ("lightblue", "9", 1, 11),

            ("blue", "8", 1, 12),

            ("blue", "7", 1, 13),

            ("blue", "6", 1, 14),

            ("lightblue", "5", 1, 15),

            ("lightblue", "4", 1, 16),

            ("lightblue", "3", 1, 17),

            ("blue", "2", 1, 18),

            ("blue", "1", 1, 19),

            ("blue", "0", 1, 20),

            ("white", "", 1, 21),

            ("blank", "", 1, 22),

            ("lightblue", "11", 1, 23),

            ("lightblue", "10", 1, 24),

            ("lightblue", "9", 1, 25),

            ("blue", "8", 1, 26),

            ("blue", "7", 1, 27),

            ("blue", "6", 1, 28),

            ("lightblue", "5", 1, 29),

            ("lightblue", "4", 1, 30),

            ("lightblue", "3", 1, 31),

            ("blue", "2", 1, 32),

            ("blue", "1", 1, 33),

            ("blue", "0", 1, 34),

            ("white", "", 1, 35),

            ("blank", "", 1, 36),

            ("lightblue", "11", 1, 37),

            ("lightblue", "10", 1, 38),

            ("lightblue", "9", 1, 39),

            ("blue", "8", 1, 40),

            ("blue", "7", 1, 41),

            ("blue", "6", 1, 42),

            ("lightblue", "5", 1, 43),

            ("lightblue", "4", 1, 44),

            ("lightblue", "3", 1, 45),

            ("blue", "2", 1, 46),

            ("blue", "1", 1, 47),

            ("blue", "0", 1, 48),

            ("white", "", 1, 49),

            ("blank", "", 1, 50),

            ("red", "OFF", 3, 1),

            ("yellow", "ON", 3, 2),

            ("blank", "", 3, 3),

            ("blue", "2", 3, 4),

            ("blue", "1", 3, 5),

            ("blue", "0", 3, 6),

            ("white", "", 3, 7),

        ]

        radius = 6.5

        for index, (color, label, row, column) in enumerate(buttons):

            if color != "blank":

                circular_button = CircularButton(button_frame, radius, color=color,
                                                 command=lambda idx=column + 2: button_command(idx))

                circular_button.grid(row=row, column=column, padx=5, pady=(5, 0))

                button_label = tk.Label(button_frame, text=label)

                button_label.grid(row=row + 1, column=column, padx=5, pady=0)

            else:

                button_label = tk.Label(button_frame, text=" ")

                button_label.grid(row=row + 1, column=column, padx=5, pady=0)

    @staticmethod
    def create_switch_grid(outer_frame):

        # Create a frame for the switches and buttons grid

        switch_frame = tk.Frame(outer_frame)

        switch_frame.pack(side="top", fill="x", pady=(20, 0))

        # Configure grid rows and columns

        for i in range(15):  # Enough rows for switches

            switch_frame.grid_rowconfigure(i, weight=1)

        for j in range(15):  # Enough columns for buttons and switches

            switch_frame.grid_columnconfigure(j, weight=1)

        # Create two circular buttons in the first two columns

        radius = 25

        circular_button_red = CircularButton(switch_frame, radius, color="red",
                                             command=lambda idx=1: button_command(idx))

        circular_button_red.grid(row=0, column=0, padx=5, pady=5)  # Add padding

        circular_button_blue = CircularButton(switch_frame, radius, color="blue",
                                              command=lambda idx=2: button_command(idx))

        circular_button_blue.grid(row=0, column=1, padx=5, pady=5)  # Add padding

        # Create switches and place them in the same row, starting from the third column

        switches = [

            ("MARGIN", "HI\n\n\n\nLO", "", "", "red"),

            (" F", "", " S", "P", "black"),

            ("ENTER", "", "SWEEP", "", "red"),

            ("  4", "", "", "", "blue"),

            ("  2", "", "", "", "blue"),

            ("  1", "", "", "", "blue"),

            ("BFR REG", "", " A'", "A", "black"),

            ("  4", "", "", "", "blue"),

            ("  2", "", "", "", "blue"),

            ("  1", "", "", "", "blue"),

            ("LOAD", "", "CLEAR", "", "red"),

            ("BFR ENT", "", "BFR EXIT", "P", "black"),

            ("RUN", "", "STEP", "", "red"),

        ]

        # Place switches in the switch_frame starting from the first row, third column

        for index, (top, label, bottom, right, color) in enumerate(switches):
            switch = PositionSwitch(switch_frame, toplabel=top, label=label, bottomlabel=bottom, rightlabel=right,
                                    color=color)

            switch.grid(row=0, column=index + 2, padx=5, pady=5)  # Add padding between switches

        # Labels for categories

        label1 = tk.Label(switch_frame, text="SELECTIVE JUMPS")

        label1.grid(row=0, column=5, columnspan=3, sticky="sew")

        label3 = tk.Label(switch_frame, text="SWEEP")

        label3.grid(row=0, column=4, columnspan=1, sticky="sew")

        label0 = tk.Label(switch_frame, text="S")

        label0.grid(row=0, column=3, columnspan=1, sticky="sew")

        label2 = tk.Label(switch_frame, text="SELECTIVE STOPS")

        label2.grid(row=0, column=9, columnspan=3, sticky="sew")

    def update_display(self, label_name, new_text, bg):

        """

        Updates the text of the specified display using its numeric identifier.



        :param label_name: The numeric identifier of the display (e.g., '1', 2, etc.).

        :param new_text: The new text or value to display.

        :param bg: Background color to apply to the display.

        """

        if label_name in self.display_labels:

            self.display_labels[label_name].config(text=new_text, bg=bg)

        else:

            print(f"Display '{label_name}' not found!")

    def get_display(self, index):

        return self.display_labels[index].cget("text")


if __name__ == "__main__":
    app = SwitchApp()

    # Example of dynamically updating a display after 2 seconds

    # app.after(2000, lambda: app.update_display(1, "  ", "grey"))

    app.mainloop()
