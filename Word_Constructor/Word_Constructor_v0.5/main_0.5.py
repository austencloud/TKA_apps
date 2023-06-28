import tkinter as tk
import tkinter.ttk as ttk
from random import choice
from data import *
from functions import ButtonEventHandlers, UIUpdater, Interpolation, UIInitializer
from tkinter import BooleanVar, Checkbutton

root = tk.Tk()

root.geometry('1000x900')
root.title('Word Constructor')


buttons_frame = tk.Frame(root)
buttons_frame.grid(row=0, column=0, rowspan=len(letter_rows), sticky='nw')
buttons = {}

state_label = tk.Label(root, text='', font=('Helvetica', '20'))
state_label.grid(row=3, column=3, sticky='nw', padx=50)

sequence_label = tk.Text(root, font=('Helvetica', '32'), height=1, width=20, cursor="xterm")
sequence_label.bind("<1>", lambda event: sequence_label.focus_set())
sequence_label.tag_config('red', foreground='red')
sequence_label.tag_config('black', foreground='black')
sequence_label.tag_configure("sel", background="yellow")
sequence_label.grid(row=2, column=3, sticky='w')

scrollbar = tk.Scrollbar(root)
scrollbar.grid(row=8, column=4, sticky='ns')

start_position_label = tk.Label(root, text='', font=('Helvetica', '20'))
start_position_label.grid(row=0, column=3, sticky='w')

end_positions_label = tk.Label(root, text='', font=('Helvetica', '20'))
end_positions_label.grid(row=1, column=3, sticky='w')  # change row to 3

saved_label = tk.Label(root, text='Saved:', font=('Helvetica', '20'))
saved_label.grid(row=7, column=3, sticky='w')

sequence_clear_button = tk.Button(root, text="Clear", height=2, width=4, font=('Helvetica', '20'))
sequence_clear_button.grid(row=5, column=2, sticky='w', padx=50)

auto_fill_mode = tk.BooleanVar(value=False)
auto_fill_checkbox = tk.Checkbutton(root, text="Autofill Mode", variable=auto_fill_mode, font=('Helvetica', '20'))
auto_fill_checkbox.grid(row=3, column=3, sticky='nw', pady=(0,20))

interpolation_label = tk.Label(root, text='Type a Word:', font=('Helvetica', '20'))
interpolation_input = tk.Entry(root, font=('Helvetica', '20'))
interpolation_button = tk.Button(root, text="Generate", width=8, font=('Helvetica', '20'))

saved_text = tk.Text(root, font=('Helvetica', '20'), height=8, width=30)
saved_text.grid(row=8, column=3, sticky='w')
saved_text.config(state='disabled')
saved_text.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=saved_text.yview)

save_button = tk.Button(root, text="Save", height=1, width=4, font=('Helvetica', '20'))
save_button.grid(row=6, column=2, sticky='w', padx=50)

button_frame = tk.Frame(root)
button_frame.grid(row=9, column=3)  # place frame at row 9, column 3

clear_saved_button = tk.Button(button_frame, text="Clear", height=1, width=4, font=('Helvetica', '20'))
clear_saved_button.pack(side='left')  # add clear button to the left side of the frame

copy_saved_button = tk.Button(button_frame, text="Copy", height=1, width=4, font=('Helvetica', '20'))
copy_saved_button.pack(side='left')

context_menu_sequence = tk.Menu(root, tearoff=0)
context_menu_sequence.add_command(label="Copy", command=lambda: button_event_handler.copy_text(sequence_label))

context_menu_saved = tk.Menu(root, tearoff=0)
context_menu_saved.add_command(label="Copy", command=lambda: button_event_handler.copy_text(saved_text))

random_word_length_label = tk.Label(root, text="Word length:", font=('Helvetica', '20'))
random_word_length_input = tk.Entry(root, font=('Helvetica', '20'))
random_word_button = tk.Button(root, text="Generate Random Word", height=1, width=20, font=('Helvetica', '20'))
random_word_length_label.grid(row=10, column=3, sticky='w')
random_word_length_input.grid(row=11, column=3, sticky='w')
random_word_button.grid(row=12, column=3, sticky='w')

end_at_start_position_var = BooleanVar()

# Create the checkbox
end_at_start_position_checkbox = tk.Checkbutton(root, font=('Helvetica', '20'),  text="End at Start Position", variable=end_at_start_position_var)
end_at_start_position_checkbox.grid(row=13, column=3, sticky='w')  # Change row and column values accordingly

start_letters = [row[0] for row in letter_rows]

style = ttk.Style()
style.configure('TButton', font=('Helvetica', '20'), anchor='center')

saved_text.tag_config('red', foreground='red')
saved_text.tag_config('black', foreground='black')

for i, row in enumerate(letter_rows):
    row_frame = tk.Frame(buttons_frame)
    row_frame.grid(row=i, column=0, sticky='w')
    for letter in row:
        button = tk.Button(row_frame, text=letter, height=1, width=2, font=('Helvetica', '20'), background='gray', foreground='black')

        button.pack(side=tk.LEFT)
        buttons[letter] = button

interpolation = Interpolation(sequence_label, start_position_label, end_positions_label, interpolation_input, auto_fill_mode, start_letters, positions)
ui_updater = UIUpdater(root, sequence_label, saved_text, state_label, start_position_label, end_positions_label, buttons, scrollbar, auto_fill_mode, interpolation)
interpolation.set_ui_updater(ui_updater)
button_event_handler = ButtonEventHandlers(root, buttons, ui_updater, interpolation, auto_fill_mode, interpolation_label, interpolation_input, interpolation_button, context_menu_sequence, context_menu_saved, sequence_label, saved_text, end_positions_label, random_word_length_input, end_at_start_position_var)
ui_initializer = UIInitializer(root, buttons, interpolation, interpolation_label, interpolation_input, interpolation_button, button_event_handler, auto_fill_mode, random_word_button)
ui_initializer.initialize_ui()

sequence_clear_button.config(command=lambda: ui_updater.clear_sequence())
sequence_label.bind("<Button-3>", lambda event: button_event_handler.show_context_menu(event, sequence_label, context_menu_sequence))
sequence_label.bind("<KeyPress>", button_event_handler.on_key_press)
auto_fill_checkbox.config(command=button_event_handler.on_auto_fill_mode_toggle)
saved_text.bind("<Button-3>", lambda event: button_event_handler.show_context_menu(event, saved_text))

save_button.config(command=lambda: ui_updater.save_sequence())
clear_saved_button.config(command=lambda: ui_updater.clear_saved())
copy_saved_button.config(command=button_event_handler.copy_saved_text)
random_word_button.config(command=button_event_handler.generate_random_word)

root.mainloop()